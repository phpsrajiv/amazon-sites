"""Request / response models for the LinkedIn carousel endpoint."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from src.models.outline import ContentOutline


class CarouselSlide(BaseModel):
    slide_number: int
    heading: str
    body_text: str
    speaker_notes: str = ""


class LinkedInRequest(BaseModel):
    outline: Optional[ContentOutline] = None
    blog_html: Optional[str] = None
    blog_title: Optional[str] = None
    brand: str = "SellerBuddy"


class LinkedInResponse(BaseModel):
    title: str
    slides: List[CarouselSlide]
    total_slides: int
