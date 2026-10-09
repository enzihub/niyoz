"""Invented YouTube data for demo mode (YOUTUBE_DEMO_MODE=true).

Every channel, title and transcript below is made up for the demo. The
thumbnails in docs/demo-thumbs/ are AI-generated scenes, not images from any
real creator. Nothing here calls YouTube, Google or OpenAI.
"""

import re
from typing import List

from app.core.config.config import settings
from app.integrations.youtube.models import VideoInfo

DEMO_VIDEOS = [
    {
        "video_id": "demo-sourdough",
        "title": "The 3-Ingredient Sourdough I Bake Every Sunday",
        "channel_name": "Crumb & Crust Kitchen",
        "thumb": "sourdough",
        "topic": "sourdough",
        "phrase": "a slow-proofed country loaf",
        "transcript": "Today we bake a simple country loaf with flour, water and salt. "
        "The trick is a long cold proof overnight, which gives the crust that blistered look. "
        "Score at a shallow angle and bake in a preheated cast iron pot for the best oven spring.",
    },
    {
        "video_id": "demo-trail",
        "title": "Riding the Longest Flow Trail in the Valley",
        "channel_name": "Northbound Wheels",
        "thumb": "trail",
        "topic": "flow trails",
        "phrase": "an eleven-kilometre forest ride",
        "transcript": "This trail runs eleven kilometres of berms and rollers through old forest. "
        "Keep your weight centred, look through the corners and let the bike float over the rollers. "
        "We finish at the lake, which is the best lunch spot on the mountain.",
    },
    {
        "video_id": "demo-cabin",
        "title": "Framing a Tiny Cabin in One Weekend (Solo Build)",
        "channel_name": "Weekend Timber",
        "thumb": "cabin",
        "topic": "a weekend cabin",
        "phrase": "a tiny cabin framed in two days",
        "transcript": "We pre-cut every stud on Friday night, so Saturday is only assembly. "
        "Square the floor deck first because every later mistake starts there. "
        "By Sunday afternoon the walls and the roof ridge are up and the cabin finally has a shape.",
    },
    {
        "video_id": "demo-telescope",
        "title": "What a $300 Telescope Can Really See",
        "channel_name": "Backyard Cosmos",
        "thumb": "telescope",
        "topic": "Saturn on a budget",
        "phrase": "what a small telescope can really see",
        "transcript": "A small reflector shows Saturn's rings, Jupiter's four big moons and craters on the Moon. "
        "Let the mirror cool for thirty minutes and use a red torch to keep your night vision. "
        "Dark skies matter more than magnification, so drive away from the city lights.",
    },
    {
        "video_id": "demo-synth",
        "title": "Patching a Whole Song with Six Modules",
        "channel_name": "Voltage Garden",
        "thumb": "synth",
        "topic": "modular synths",
        "phrase": "a whole song from six synth modules",
        "transcript": "One oscillator, one filter and an envelope are enough for a bass line. "
        "A random source into the filter cutoff keeps the pattern alive. "
        "We record it in one take and add a little tape delay at the end.",
    },
    {
        "video_id": "demo-ramen",
        "title": "Weeknight Ramen That Tastes Like a 12-Hour Broth",
        "channel_name": "Late Night Noodle Lab",
        "thumb": "ramen",
        "topic": "quick ramen",
        "phrase": "a weeknight ramen broth",
        "transcript": "Roast the bones and aromatics hard before they go in the pressure cooker. "
        "Forty-five minutes under pressure gives a cloudy, rich broth. "
        "Marinate soft eggs in soy and mirin for six hours for the classic topping.",
    },
    {
        "video_id": "demo-garden",
        "title": "Raised Beds: What I Would Do Differently",
        "channel_name": "Small Plot Growing",
        "thumb": "garden",
        "topic": "raised beds",
        "phrase": "raised-bed lessons",
        "transcript": "Make the beds narrow enough to reach the middle without stepping in. "
        "Fill with compost on top of cardboard instead of buying bags of soil. "
        "Tomatoes go in deep, right up to the first leaves, so they grow more roots.",
    },
    {
        "video_id": "demo-run",
        "title": "Training for My First Trail Half Marathon",
        "channel_name": "Coastline Miles",
        "thumb": "run",
        "topic": "trail running",
        "phrase": "training for a first trail half marathon",
        "transcript": "Most of my weekly running is slow, at a pace where I can still talk. "
        "One session a week is hills, because the race climbs four hundred metres. "
        "Practise eating on long runs so race day has no surprises.",
    },
]


def _thumb_url(name: str) -> str:
    base = (settings.DEMO_THUMB_BASE_URL or "").rstrip("/")
    return f"{base}/{name}.jpg" if base else ""


def demo_recommendations() -> List[VideoInfo]:
    return [
        VideoInfo(
            title=v["title"],
            url=f"https://www.youtube.com/watch?v={v['video_id']}",
            video_id=v["video_id"],
            channel_name=v["channel_name"],
            thumbnail_url=_thumb_url(v["thumb"]) or None,
        )
        for v in DEMO_VIDEOS
    ]


def demo_transcript(video_id: str) -> List[dict]:
    for v in DEMO_VIDEOS:
        if v["video_id"] == video_id:
            sentences = [s for s in re.split(r"(?<=\.)\s+", v["transcript"]) if s]
            return [
                {"text": s, "start": float(i * 8), "duration": 8.0}
                for i, s in enumerate(sentences)
            ]
    return []


def fake_completion(prompt: str) -> str:
    """Deterministic stand-in for the LLM when no OPENAI_API_KEY is set."""
    if "subject line" in prompt or "1-sentence summary" in prompt:
        picked = [v for v in DEMO_VIDEOS if v["title"] in prompt][:3]
        if "subject line" in prompt:
            names = [v["topic"].capitalize() if i == 0 else v["topic"] for i, v in enumerate(picked)]
            return ", ".join(names[:-1]) + " and " + names[-1] if len(names) > 1 else (names or ["Your videos"])[0]
        phrases = [v["phrase"] for v in picked]
        return ", ".join(phrases[:-1]) + " and " + phrases[-1] if len(phrases) > 1 else "".join(phrases)
    title = re.search(r"Title: (.*)", prompt)
    content = re.search(r"Content: (.*)", prompt, flags=re.S)
    title_text = title.group(1).strip() if title else "Today's video"
    sentences = [
        s.strip()
        for s in re.split(r"(?<=\.)\s+", content.group(1).strip() if content else "")
        if s.strip()
    ]
    items = "".join(f"<li>{s}</li>" for s in sentences[:3])
    return f"<div><p><b>{title_text}</b>: the short version.</p><ul>{items}</ul></div>"
