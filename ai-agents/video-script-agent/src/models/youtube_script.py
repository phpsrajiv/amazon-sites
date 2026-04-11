"""Request / response models for the YouTube video script endpoint."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from src.models.outline import ContentOutline


class ScriptSegment(BaseModel):
    timestamp: str                    # e.g. "0:00", "1:30"
    section_title: str                # e.g. "Hook", "Intro", "Main Point 1"
    narration: str                    # What the presenter says
    on_screen_text: str = ""          # Text overlay / lower third
    b_roll_suggestion: str = ""       # Visual suggestion for B-roll footage
    duration_seconds: int = 30        # Duration of this segment


class YouTubeScriptRequest(BaseModel):
    outline: Optional[ContentOutline] = None
    blog_html: Optional[str] = None
    blog_title: Optional[str] = None
    brand: str = "SellerBuddy"
    niche: str = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"
    target_duration_minutes: int = 8  # Target video length


class YouTubeScriptResponse(BaseModel):
    title: str
    description: str
    tags: List[str]
    segments: List[ScriptSegment]
    total_duration_seconds: int
    thumbnail_suggestion: str
