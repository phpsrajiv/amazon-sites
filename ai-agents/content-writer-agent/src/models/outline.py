"""
Content outline models — shared contract with the SEO Agent.

These models mirror the ContentSection and ContentOutline classes defined in
seo-agent/src/agents/seo_agent.py so the content writer can accept outlines
produced by the SEO pipeline.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class ContentSection(BaseModel):
    heading: str
    word_count: int
    notes: str


class ContentOutline(BaseModel):
    title: str
    post_type: str = "how-to"
    target_keyword: str = ""
    meta_description: str
    schema_types: List[str] = []
    featured_image_spec: str = ""
    sections: List[ContentSection]
    cta: str
    internal_links: List[str] = []
    faq_questions: List[str] = []
