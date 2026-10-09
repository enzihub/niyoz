import jinja2
import asyncio
import inflect
import pytz
from openai import AsyncOpenAI

from app.core.ai.prompts import TRANSCRIPT_SUMMARY_PROMPT, VIDEO_TITLE_SUMMARY_PROMPT, SUBJECT_LINE_PROMPT
from app.core.config.config import settings
from app.core.config.logger import logger

p = inflect.engine()

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path


# Rate limiting configuration
class RateLimitConfig:
    def __init__(self,
                 max_concurrent_calls: int = 5,
                 requests_per_minute: int = 50):
        self.max_concurrent_calls = max_concurrent_calls
        self.requests_per_minute = requests_per_minute


@dataclass
class TranscriptSegment:
    text: str
    start: float
    duration: float


@dataclass
class TranscriptData:
    video_id: str
    video_title: str
    video_url: str
    channel_name: str
    segments: List[TranscriptSegment]
    timestamp: datetime
    thumbnail_url: Optional[str] = None

    def get_full_text(self) -> str:
        return ' '.join(segment.text for segment in self.segments)


class TranscriptProcessor:
    def __init__(self):
        self.logger = logger
        self.transcript_queue: List[TranscriptData] = []
        self.summaries: List[Dict] = []
        self.rate_limit = RateLimitConfig()
        self.semaphore = asyncio.Semaphore(self.rate_limit.max_concurrent_calls)

        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "not-set")

        # Setup template environment
        template_dir = Path(__file__).parent.parent.parent.parent / 'templates'
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=True
        )

    async def _make_openai_call(self, prompt: str) -> str:
        if settings.YOUTUBE_DEMO_MODE and not settings.OPENAI_API_KEY:
            # Demo mode without a key: canned, invented summaries (no network call)
            from app.integrations.youtube.demo_data import fake_completion
            return fake_completion(prompt)
        async with self.semaphore:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # or your preferred model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content

    async def add_transcript(self, transcript_data: TranscriptData) -> None:
        self.transcript_queue.append(transcript_data)
        self.logger.info(f"Added transcript for video '{transcript_data.video_title}' to queue")

    async def process_queued_transcripts(self, user_timezone, is_premium: bool = True) -> dict:
        self.logger.info(f"Processing {len(self.transcript_queue)} transcripts")
        self.summaries = []

        # Process transcripts concurrently with rate limiting
        tasks = [
            self.process_single_transcript(transcript)
            for transcript in self.transcript_queue
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        self.summaries = [r for r in results if r is not None and not isinstance(r, Exception)]

        if self.summaries:
            return await self.generate_final_newsletter(user_timezone, is_premium)

        self.transcript_queue.clear()
        self.summaries.clear()

    async def process_single_transcript(self, transcript: TranscriptData) -> Optional[Dict]:
        """Process a single transcript and return its summary"""
        try:
            self.logger.info(f"Processing transcript for video: {transcript.video_title}")

            prompt = TRANSCRIPT_SUMMARY_PROMPT.format(
                video_title=transcript.video_title,
                transcript_text=transcript.get_full_text()
            )

            # Get response from OpenAI
            summary = await self._make_openai_call(prompt)

            return {
                "video_title": transcript.video_title,
                "video_url": transcript.video_url,
                "channel_name": transcript.channel_name,
                "thumbnail_url": transcript.thumbnail_url,
                "summary": summary.strip()
            }

        except Exception as e:
            self.logger.error(f"Error processing transcript: {str(e)}")
            return None

    async def _generate_subject_line(self, summaries: List[Dict]) -> str:
        """
        Generate a clickbaity subject line for the newsletter based on video titles.
        """
        try:
            # Extract and join video titles
            video_titles = "\n".join([f"- {s['video_title']}" for s in summaries])

            prompt = SUBJECT_LINE_PROMPT.format(video_titles=video_titles)

            subject_line = await self._make_openai_call(prompt)
            return subject_line.strip()

        except Exception as e:
            self.logger.error(f"Error generating subject line: {str(e)}")
            return "Your YouTube Content Newsletter"

    async def _generate_video_title_summary(self, summaries: List[Dict]) -> str:
        """
        Generate a summary of the video titles for the introduction.
        """
        try:
            # Extract and join video titles
            video_titles = "\n".join([f"- {s['video_title']}" for s in summaries])

            prompt = VIDEO_TITLE_SUMMARY_PROMPT.format(video_titles=video_titles)

            title_summary = await self._make_openai_call(prompt)
            return title_summary.strip()

        except Exception as e:
            self.logger.error(f"Error generating video title summary: {str(e)}")
            return "an exciting mix of content spanning various topics"

    async def generate_final_newsletter(self, user_timezone, is_premium: bool = True) -> Dict:
        """
        Generate final newsletter using template and OpenAI-generated content
        """
        try:
            # Get user subscriptions and determine premium status
            # subscriptions = await get_user_subscriptions(user_id)


            # Load newsletter template
            template = self.template_env.get_template('newsletter.html')

            # Generate subject line and video title summary concurrently
            subject_line_task = self._generate_subject_line(self.summaries)
            video_title_summary_task = self._generate_video_title_summary(self.summaries)

            subject_line, video_title_summary = await asyncio.gather(
                subject_line_task,
                video_title_summary_task
            )

            # User TZ
            user_tz = pytz.timezone(user_timezone)
            now = datetime.now().astimezone(user_tz)
            day_of_week = now.strftime("%A")
            date = f"{now.strftime('%b')} {p.ordinal(now.day)}"

            # Render the newsletter template
            newsletter_content = template.render(
                video_summaries=self.summaries,
                video_title_summary=video_title_summary,
                logo_data=settings.NEWSLETTER_LOGO_URL,
                app_url=settings.APP_URL.rstrip('/'),
                contact_email=settings.CONTACT_EMAIL,
                title=subject_line,
                timestamp=now.strftime("%A, %B %d, %Y").replace(" 0", " "),
                day_of_week=day_of_week,
                date=date,
                is_premium=is_premium
            )

            return {
                "html_content": newsletter_content,
                "subject_line": subject_line
            }

        except Exception as e:
            self.logger.error(f"Error generating final newsletter: {str(e)}")
            return {"error": str(e)}