# scheduler_service.py

from datetime import datetime
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth.auth_service import get_user_token
from app.core.config.config import settings
from app.core.config.logger import logger
from app.core.messaging.message_service import MessageService
from app.db import database
from app.integrations.youtube.youtube import generate_newsletter_content


class SchedulerService:
    def __init__(self, message_service: MessageService):
        self.message_service = message_service

    async def get_users_for_scheduling(
            self, db: Session, lookahead_minutes: int
    ) -> List[Dict]:
        """
        Calls the stored procedure to get users whose prefTime is within the next lookahead window
        """
        try:
            query = text("SELECT * FROM get_scheduled_users(:lookahead_minutes)")
            result = db.execute(query, {"lookahead_minutes": lookahead_minutes})
            rows = result.fetchall()

            return [{
                "clerk_id": str(row.clerk_id),
                "user_id": str(row.user_id),
                "email": row.email,
                "phone": row.phone,
                "timezone": row.timezone,
                "scheduled_for": row.scheduled_for.isoformat(),
                "target_hour": row.target_hour,
                "local_time": row.local_time
            } for row in rows]
        except Exception as e:
            logger.error(f"Error fetching users for scheduling: {str(e)}")
            return []

    async def produce_messages_async(self):
        """Async logic for scheduling newsletters"""
        db = database.SessionLocal()
        try:
            users = await self.get_users_for_scheduling(db, 60)
            logger.info(f"Found {len(users)} users for scheduling")
            for user in users:
                try:
                    target_time = datetime.fromisoformat(user["scheduled_for"])
                    # Check existing newsletters
                    existing_newsletters = self.message_service.get_user_messages(
                        user["user_id"]
                    )
                    if any(
                            abs(float(n["scheduled_time"]) - target_time.timestamp()) < 3600
                            for n in existing_newsletters
                    ):
                        logger.info(
                            f"Message already scheduled for {user['user_id']} at {target_time}"
                        )
                        continue

                    # First, enqueue a placeholder message immediately
                    placeholder_payload = {
                        "status": "generating",
                        "subject": "Newsletter being generated...",
                        "body": "Your newsletter is being generated..."
                    }
                    message_data = self.message_service.get_message_data(
                        user, placeholder_payload, target_time.timestamp()
                    )

                    # Enqueue placeholder immediately
                    success = self.message_service.enqueue_message(
                        user["user_id"], target_time, message_data
                    )

                    if success:
                        # Now generate the actual content asynchronously
                        clerk_id = user["clerk_id"]
                        user_timezone = user["timezone"]
                        youtube_token = (None if settings.YOUTUBE_DEMO_MODE else await get_user_token(clerk_id, "oauth_google"))
                        message_payload = await generate_newsletter_content(youtube_token, user_timezone, db, user["email"])

                        # Update the already enqueued message with real content
                        self.message_service.update_message_content(
                            message_data.id,
                            message_payload
                        )

                        logger.info(
                            f"Updated message content for {user['user_id']} at {target_time}"
                        )
                    else:
                        logger.error(f"Failed to schedule for {user['user_id']}")

                except Exception as e:
                    logger.error(f"Error processing {user['user_id']}: {str(e)}")

        except Exception as e:
            logger.error(f"Producer error: {str(e)}")
        finally:
            db.close()

    async def consume_messages_async(self):
        """Async logic for processing and sending messages"""
        try:
            # Get pending messages using the service
            messages = self.message_service.get_pending_messages()
            for message in messages:
                logger.info(f"Processing message {message.id}")
                try:
                    # Send the message
                    success = await self.message_service.send_user_message(
                        message.email, message.payload
                    )

                    if success:
                        # Mark as sent using the service
                        self.message_service.mark_message_sent(message.id)
                        logger.info(f"Message sent successfully to {message.phone}")
                    else:
                        logger.error(f"Failed to send message to {message.email}")

                except Exception as e:
                    logger.error(f"Error processing message {message.id}: {str(e)}")

        except Exception as e:
            logger.error(f"Async consumer error: {str(e)}")
