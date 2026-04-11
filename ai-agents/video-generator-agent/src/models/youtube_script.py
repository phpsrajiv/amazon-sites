"""
YouTube script models — input contract from the Video Script Agent.

These models mirror the ScriptSegment and YouTubeScriptResponse from
video-script-agent so the video generator can accept script output.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class ScriptSegment(BaseModel):
    timestamp: str                    # e.g. "0:00", "1:30"
    section_title: str                # e.g. "Hook", "Intro", "Main Point 1"
    narration: str                    # What the presenter says
    on_screen_text: str = ""          # Text overlay / lower third
    b_roll_suggestion: str = ""       # Visual suggestion for B-roll footage
    duration_seconds: int = 30        # Duration of this segment


class YouTubeScriptResponse(BaseModel):
    title: str
    description: str
    tags: List[str]
    segments: List[ScriptSegment]
    total_duration_seconds: int
    thumbnail_suggestion: str
