"""
LinkedIn Carousel Generator
============================
Takes a ContentOutline (or raw blog HTML) and produces 8-12 carousel slide
copy, ready for design in Canva or similar tools.

Uses the fast model (gpt-3.5-turbo) since this is short-form content.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.models.outline import ContentOutline
from src.models.linkedin import CarouselSlide

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


class LinkedInGenerator:
    def __init__(self) -> None:
        fast_model = os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(
            model=fast_model,
            temperature=0.7,
            openai_api_key=api_key,
        )

    def _build_context(
        self,
        outline: Optional[ContentOutline] = None,
        blog_html: Optional[str] = None,
        blog_title: Optional[str] = None,
    ) -> str:
        """Build context string from either outline or blog HTML."""
        if outline:
            sections_text = "\n".join(
                f"  - {s.heading}: {s.notes}" for s in outline.sections
            )
            return (
                f"Blog title: \"{outline.title}\"\n"
                f"Target keyword: \"{outline.target_keyword}\"\n"
                f"Meta description: \"{outline.meta_description}\"\n"
                f"CTA: \"{outline.cta}\"\n\n"
                f"Sections:\n{sections_text}"
            )
        elif blog_html:
            # Strip HTML tags for a plain-text summary
            plain = re.sub(r"<[^>]+>", " ", blog_html)
            # Truncate to ~2000 chars to stay within token limits
            truncated = plain[:2000]
            title = blog_title or "Blog Post"
            return f"Blog title: \"{title}\"\n\nContent summary:\n{truncated}"
        else:
            raise ValueError("Either 'outline' or 'blog_html' must be provided.")

    def generate_carousel(
        self,
        brand: str = "SellerBuddy",
        outline: Optional[ContentOutline] = None,
        blog_html: Optional[str] = None,
        blog_title: Optional[str] = None,
    ) -> List[CarouselSlide]:
        """Generate 8-12 LinkedIn carousel slides."""
        context = self._build_context(outline, blog_html, blog_title)

        messages = [
            SystemMessage(content=(
                f"You are a LinkedIn content strategist for {brand}. "
                "Create carousel slide copy from the provided blog content.\n\n"
                "Rules:\n"
                "- Generate 8-12 slides as a JSON array.\n"
                "- Slide 1: Hook/title slide with a bold claim or statistic.\n"
                "- Slides 2 to N-1: One key insight per slide. "
                "Body text should be 30-60 words (readable on a carousel image).\n"
                "- Final slide: CTA slide encouraging action.\n"
                "- Tone: professional but engaging, short sentences, no jargon.\n"
                "- Each slide object must have: slide_number, heading, body_text, speaker_notes.\n"
                "- speaker_notes: a longer talking point (1-2 sentences) for the presenter.\n\n"
                "Return ONLY the JSON array. No markdown fences."
            )),
            HumanMessage(content=context),
        ]

        response = self.llm.invoke(messages)
        text = _strip_fences(response.content.strip())
        data = json.loads(text)

        return [CarouselSlide(**slide) for slide in data]
