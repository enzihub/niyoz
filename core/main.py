# main.py

import google.generativeai as genai
import sentry_sdk
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.api.routes import router
from app.core.config.config import settings
from app.core.config.logger import logger
from app.db.redis_service import RedisService

from fastapi import FastAPI, Request

load_dotenv()

if settings.SENTRY_DSN:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0)

# Initialize FastAPI app
app = FastAPI()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Create Redis service instance
redis_service = RedisService()

# Store redis_service in app state
setattr(app, "redis_service", redis_service)

# Include the router
app.include_router(router)

if settings.YOUTUBE_DEMO_MODE:
    # Serve the invented, AI-generated demo thumbnails (docs/demo-thumbs)
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles

    thumbs = Path(__file__).resolve().parent.parent / "docs" / "demo-thumbs"
    if thumbs.is_dir():
        app.mount("/demo/thumbs", StaticFiles(directory=thumbs), name="demo-thumbs")

class APISecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow healthcheck without API key
        if request.url.path in ["/health"] or (
            settings.YOUTUBE_DEMO_MODE and request.url.path.startswith("/demo/")
        ):
            return await call_next(request)

        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        if not settings.API_KEY or api_key != settings.API_KEY:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid API key"}
            )

        return await call_next(request)

app.add_middleware(APISecurityMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    # Check Redis connection using the service
    if not app.redis_service.check_connection():
        error_msg = "Failed to establish Redis connection"
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    logger.info("Redis connection established successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    try:
        # Close Redis connection
        app.redis_service.client.close()
        logger.info("Redis connection closed successfully")
    except Exception as e:
        logger.error(f"Redis shutdown error: {str(e)}")
