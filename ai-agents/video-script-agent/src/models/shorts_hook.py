"""Request / response models for the YouTube Shorts hook endpoint."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from src.models.outline import ContentOutline


class ShortsHook(BaseModel):
    hook_number: int
    title: str                        # Short, punchy title for the Short
    narration: str                    # Full narration script (≤60 seconds of speech)
    on_screen_text: List[str] = []    # Text overlays shown during the Short
    cta: str = ""                     # Call-to-action at the end


class ShortsHookRequest(BaseModel):
    outline: Optional[ContentOutline] = None
    blog_html: Optional[str] = None
    blog_title: Optional[str] = None
    brand: str = "SellerBuddy"
    num_hooks: int = 3                # Number of Shorts hooks to generate


class ShortsHookResponse(BaseModel):
    blog_title: str
    hooks: List[ShortsHook]
    total_hooks: int
