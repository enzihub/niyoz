"""Demo-mode outbox: run the real newsletter pipeline on invented videos and
store the result locally instead of emailing it."""

from datetime import datetime
from pathlib import Path

from app.integrations.youtube.youtube import generate_newsletter_content

OUTBOX = Path(__file__).resolve().parents[3] / "outbox"


async def build_demo_newsletter(email: str, timezone: str = "UTC") -> dict:
    result = await generate_newsletter_content(
        youtube_token=None, user_timezone=timezone, email=email, is_premium=False
    )
    if not result:
        raise RuntimeError("Demo newsletter generation failed")
    OUTBOX.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (OUTBOX / f"{stamp}.html").write_text(result["body"], encoding="utf-8")
    (OUTBOX / "latest.html").write_text(result["body"], encoding="utf-8")
    return {"subject": result["subject"], "preview": "/demo/outbox/latest"}


def latest_html() -> str:
    latest = OUTBOX / "latest.html"
    if not latest.exists():
        return "<p>No demo email yet. Press the button in the web app first.</p>"
    return latest.read_text(encoding="utf-8")
