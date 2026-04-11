from pydantic import BaseModel
from typing import Optional

from src.models.common import ContentTone


class ReelSegment(BaseModel):
    timestamp: str
    visual: str
    voiceover: str
    text_overlay: str


class ReelScript(BaseModel):
    hook: str
    segments: list[ReelSegment]
    cta: str
    duration_seconds: int
    music_mood: str
    text_overlays: list[str]


class InstagramCaption(BaseModel):
    text: str
    hashtags: list[str]


class InstagramRequest(BaseModel):
    topic: str
    brand: str = "SellerBuddy"
    tone: ContentTone = ContentTone.INSPIRATIONAL
    event_context: Optional[str] = None
    reel_duration: int = 30


class InstagramResponse(BaseModel):
    reel_script: ReelScript
    caption: InstagramCaption
    topic: str
    event_context: Optional[str] = None
