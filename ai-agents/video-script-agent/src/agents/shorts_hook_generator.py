"""
YouTube Shorts Hook Generator
===============================
Takes a ContentOutline or blog HTML and generates punchy 60-second
YouTube Shorts scripts derived from the most engaging points.

Uses the fast model (gpt-3.5-turbo) with higher temperature for creative hooks.
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
from src.models.shorts_hook import ShortsHook

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


class ShortsHookGenerator:
    def __init__(self) -> None:
        fast_model = os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(
            model=fast_model,
            temperature=0.8,
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
                f"CTA: \"{outline.cta}\"\n\n"
                f"Key sections:\n{sections_text}"
            )
        elif blog_html:
            plain = re.sub(r"<[^>]+>", " ", blog_html)
            truncated = plain[:2000]
            title = blog_title or "Blog Post"
            return f"Blog title: \"{title}\"\n\nContent summary:\n{truncated}"
        else:
            raise ValueError("Either 'outline' or 'blog_html' must be provided.")

    def generate_hooks(
        self,
        brand: str = "SellerBuddy",
        num_hooks: int = 3,
        outline: Optional[ContentOutline] = None,
        blog_html: Optional[str] = None,
        blog_title: Optional[str] = None,
    ) -> List[ShortsHook]:
        """Generate YouTube Shorts hook scripts."""
        context = self._build_context(outline, blog_html, blog_title)

        messages = [
            SystemMessage(content=(
                f"You are a YouTube Shorts content creator for {brand}. "
                "Create punchy, viral-worthy Shorts scripts from the provided blog content.\n\n"
                "Rules:\n"
                f"- Generate exactly {num_hooks} Shorts hooks as a JSON array.\n"
                "- Each Short must be speakable in 60 seconds or less (~150 words max).\n"
                "- Pick the most surprising, controversial, or actionable points from the blog.\n"
                "- Structure each hook:\n"
                "  - hook_number: sequential number\n"
                "  - title: catchy title for the Short (50 chars max)\n"
                "  - narration: full script the presenter reads (conversational, fast-paced, ~150 words max)\n"
                "  - on_screen_text: array of 3-5 brief text overlays shown at key moments\n"
                "  - cta: short call-to-action at the end (e.g. \"Follow for more Amazon tips\")\n"
                "- Tone: energetic, direct, no fluff. Start with a hook in the first 3 seconds.\n"
                "- Each Short should stand alone — no need for context from the full blog.\n\n"
                "Return ONLY the JSON array. No markdown fences."
            )),
            HumanMessage(content=context),
        ]

        response = self.llm.invoke(messages)
        text = _strip_fences(response.content.strip())
        data = json.loads(text)

        return [ShortsHook(**hook) for hook in data]
