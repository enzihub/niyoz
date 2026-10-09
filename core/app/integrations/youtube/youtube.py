# youtube.py

import asyncio
import random
from datetime import datetime

import httpx

from typing import List, Optional, Dict

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from fastapi import HTTPException

from app.core.config.config import settings
from app.core.config.logger import logger
from app.core.subscription.check_subscription import verify_premium_status
from app.integrations.youtube.models import VideoInfo
from app.integrations.youtube.transcript_processor import TranscriptProcessor, TranscriptData, TranscriptSegment
from app.integrations.youtube.video_processing import process_video_batch

load_dotenv()

YOUTUBE_BROWSE_ENDPOINT = 'https://www.youtube.com/youtubei/v1/browse'

# Add semaphore for controlling concurrent API requests
YOUTUBE_SEMAPHORE = asyncio.Semaphore(10)
TRANSCRIPT_SEMAPHORE = asyncio.Semaphore(10)


async def get_recommended_videos(token) -> List[VideoInfo]:
    """Fetch recommended videos with controlled concurrency"""
    if settings.YOUTUBE_DEMO_MODE:
        from app.integrations.youtube.demo_data import demo_recommendations
        return demo_recommendations()
    async with YOUTUBE_SEMAPHORE:  # Control concurrent requests to YouTube API
        try:
            # token = await get_valid_credentials(token_info)

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'X-Origin': 'https://www.youtube.com'
            }

            payload = {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": "2.20240104.01.00",
                        "mainAppWebInfo": {
                            "graftUrl": "/",
                            "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER"
                        }
                    }
                },
                "browseId": "FEwhat_to_watch"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:  # Add timeout
                response = await client.post(YOUTUBE_BROWSE_ENDPOINT,
                                             json=payload,
                                             headers=headers)
                response.raise_for_status()
                data = response.json()

                videos = []
                contents = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])

                for tab in contents:
                    if 'tabRenderer' in tab and tab['tabRenderer'].get('selected', False):
                        items = tab['tabRenderer'].get('content', {}).get('richGridRenderer', {}).get('contents', [])

                        for item in items:
                            if 'richItemRenderer' not in item:
                                continue

                            video_renderer = item['richItemRenderer'].get('content', {}).get('videoRenderer')
                            if not video_renderer:
                                continue

                            video_id = video_renderer.get('videoId')
                            if not video_id:
                                continue

                            title = video_renderer.get('title', {}).get('runs', [{}])[0].get('text', '')
                            channel_name = (video_renderer.get('ownerText', {})
                                            .get('runs', [{}])[0]
                                            .get('text', ''))

                            videos.append(VideoInfo(
                                title=title,
                                url=f"https://www.youtube.com/watch?v={video_id}",
                                video_id=video_id,
                                channel_name=channel_name
                            ))

                return videos

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch recommended videos: {str(e)}"
            )


async def get_video_transcript(video_id: str) -> List[TranscriptSegment]:
    """Fetch video transcript with controlled concurrency"""
    if settings.YOUTUBE_DEMO_MODE:
        from app.integrations.youtube.demo_data import demo_transcript
        segments = demo_transcript(video_id)
        if not segments:
            raise HTTPException(status_code=404, detail="No demo transcript")
        return [TranscriptSegment(**segment) for segment in segments]
    async with TRANSCRIPT_SEMAPHORE:  # Control concurrent transcript requests
        try:
            api_key = settings.SCRAPEOPS_API_KEY

            # First try with proxy if API key is available
            if api_key:
                proxy_config = {
                    "http": f"http://scrapeops:{api_key}@residential-proxy.scrapeops.io:8181",
                    "https": f"http://scrapeops:{api_key}@residential-proxy.scrapeops.io:8181"
                }
                try:
                    transcript = await asyncio.to_thread(
                        YouTubeTranscriptApi.get_transcript,
                        video_id,
                        proxies=proxy_config
                    )
                    return [TranscriptSegment(**segment) for segment in transcript]
                except Exception:
                    pass

            # Try without proxy
            transcript = await asyncio.to_thread(
                YouTubeTranscriptApi.get_transcript,
                video_id
            )
            return [TranscriptSegment(**segment) for segment in transcript]

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch transcript: {str(e)}"
            )


async def generate_newsletter_content(youtube_token: str, user_timezone, db = None, email: str = None, is_premium: Optional[bool] = None) -> Optional[Dict]:
    """Generate newsletter content with improved concurrency"""
    # logger.info(f"Starting newsletter generation for user {user_token.email}")
    processor = TranscriptProcessor()

    try:
        if is_premium is None:
            is_premium = await verify_premium_status(db, email)

        video_limit = 3
        if is_premium:
            video_limit = 12

        logger.info(f"User {email} has limit: {video_limit} videos")

        # Get recommended videos
        all_videos = await get_recommended_videos(youtube_token)
        random.shuffle(all_videos)

        # Process videos with retries
        valid_videos = await process_video_batch(all_videos, required_count=video_limit)

        if not valid_videos and all_videos:
            valid_videos = [(video, []) for video in all_videos[:video_limit]]

        # Process transcripts concurrently with semaphore
        semaphore = asyncio.Semaphore(5)  # Limit concurrent processing

        async def process_transcript(video, transcript_segments):
            async with semaphore:
                transcript_data = TranscriptData(
                    video_id=video.video_id,
                    video_title=video.title,
                    video_url=video.url,
                    channel_name=video.channel_name,
                    thumbnail_url=video.thumbnail_url,
                    segments=transcript_segments,
                    timestamp=datetime.now()
                )
                await processor.add_transcript(transcript_data)

        # Process all transcripts concurrently but controlled
        await asyncio.gather(*[process_transcript(video, transcript)
                               for video, transcript in valid_videos])

        newsletter_result = await processor.process_queued_transcripts(user_timezone, is_premium)

        return {
            "subject": newsletter_result["subject_line"],
            "body": newsletter_result["html_content"],
        }

    except Exception as e:
        logger.error(f"Error generating newsletter for user: {str(e)}")
        return None