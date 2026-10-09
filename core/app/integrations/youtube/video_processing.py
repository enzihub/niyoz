import asyncio
import logging
from typing import List, Tuple

from fastapi import HTTPException

MAX_RECOMMENDATION_RETRIES = 3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set APScheduler logger to WARNING level to reduce verbosity
logging.getLogger('apscheduler').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def process_video_batch(videos: List, required_count: int = 8) -> List[Tuple]:
    """Process videos until reaching required count of valid ones"""
    valid_videos = []
    semaphore = asyncio.Semaphore(10)  # Limit concurrent API calls

    async def process_video(video):
        async with semaphore:  # Control concurrent requests
            try:
                logger.info(f"Processing video {video.video_id}")
                from app.integrations.youtube.youtube import get_video_transcript
                transcript_segments = await get_video_transcript(video.video_id)
                return {
                    'video': video,
                    'transcript': transcript_segments,
                    'success': True
                }
            except HTTPException as e:
                logger.warning(f"Failed to get transcript for {video.video_id}: {str(e)}")
                return {
                    'video': video,
                    'success': False
                }

    # Process videos with retries
    retry_count = 0
    processed_video_ids = set()

    while retry_count < MAX_RECOMMENDATION_RETRIES and len(valid_videos) < required_count:
        # Get unprocessed videos
        unprocessed_videos = [v for v in videos if v.video_id not in processed_video_ids]
        if not unprocessed_videos:
            break

        # Process a batch of videos concurrently
        batch = unprocessed_videos[:required_count - len(valid_videos)]
        tasks = [process_video(video) for video in batch]
        results = await asyncio.gather(*tasks)

        # Update processed videos and collect successful results
        for result in results:
            processed_video_ids.add(result['video'].video_id)
            if result['success'] and len(valid_videos) < required_count:
                valid_videos.append((result['video'], result['transcript']))

        retry_count += 1
        logger.info(f"Retry {retry_count}: Got {len(valid_videos)} valid videos out of {required_count} needed")

    return valid_videos[:required_count]
