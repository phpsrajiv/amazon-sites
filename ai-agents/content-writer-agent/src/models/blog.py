"""Request / response models for the blog writing endpoint."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from src.models.outline import ContentOutline


class BlogWriteRequest(BaseModel):
    outline: ContentOutline
    push_to_drupal: bool = False
    author: str = "SellerBuddy"
    category: str = "SEO"
    brand: str = "SellerBuddy"
    niche: str = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"


class BlogWriteResponse(BaseModel):
    title: str
    meta_description: str
    body_html: str
    word_count: int
    drupal_id: Optional[str] = None
    drupal_status: Optional[str] = None
