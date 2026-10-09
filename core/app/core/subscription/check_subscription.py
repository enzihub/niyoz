
from app.core.config.logger import logger
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any
from app.db.models import Subscription


async def get_user_subscriptions(db: Session, email: str) -> List[Dict[Any, Any]]:
    try:
        subscriptions = (
            db.query(Subscription)
            .filter(
                Subscription.email == email,
                or_(
                    Subscription.status.in_(["trialing", "active"])
                )
            )
            .all()
        )

        return [subscription.__dict__ for subscription in subscriptions]
    except Exception as e:
        logger.error(f"Error fetching subscriptions for user {email}: {str(e)}")
        return []


async def verify_premium_status(db: Session, email: str) -> bool:
    """Verify if user has premium access."""
    subscriptions = await get_user_subscriptions(db, email)

    # Return bool because trial subscriptions are also considered premium.
    # And we want to handle when they expire etc.
    return bool(subscriptions)
