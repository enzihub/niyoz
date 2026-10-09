# app/routes.py

# app/core/api/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config.config import settings
from app.core.config.logger import logger
from app.core.messaging.message_service import MessageService
from app.core.scheduler.scheduler_service import SchedulerService
from app.db.database import get_db
from app.db.redis_service import RedisService
from fastapi import Depends
from app.core.scheduler.job_tasks import send_newsletter_task


router = APIRouter()

# Initialize services
redis_service = RedisService()
message_service = MessageService(redis_service)
scheduler_service = SchedulerService(message_service)

class NewsletterRequest(BaseModel):
    email: str

@router.post("/send-newsletter")
async def send_newsletter(request: NewsletterRequest, db: Session = Depends(get_db)):
    """Endpoint to trigger immediate newsletter sending for a specific user"""
    try:
        email = request.email
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        if settings.YOUTUBE_DEMO_MODE:
            # Demo mode: build the email right now from invented videos and
            # keep it in the local outbox instead of queueing and sending it.
            from app.integrations.youtube.demo_outbox import build_demo_newsletter
            result = await build_demo_newsletter(email)
            return {"status": "Your Niyoz digest is ready", **result}

        # Schedule for immediate sending
        logger.info(f"Received request to send newsletter to {email}")
        send_newsletter_task.delay(email)

        return {"status": "Newsletter sending scheduled"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def root():
    return {"service": "niyoz-core", "environment": settings.ENVIRONMENT}




@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/demo/outbox/latest")
async def demo_outbox_latest():
    """Demo mode only: the last email the demo pipeline produced."""
    from fastapi.responses import HTMLResponse
    from app.integrations.youtube.demo_outbox import latest_html

    if not settings.YOUTUBE_DEMO_MODE:
        raise HTTPException(status_code=404, detail="Not found")
    return HTMLResponse(latest_html())
