"""
YouTube Script Writer
======================
Takes a ContentOutline or blog HTML and generates a full YouTube video script
with timestamps, narration, on-screen text cues, and B-roll suggestions.

Uses the primary model (gpt-4-turbo-preview) for high-quality script writing.
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
from src.models.youtube_script import ScriptSegment

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    """Remove optional markdown code fences from LLM output."""
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


class YouTubeScriptWriter:
    def __init__(self) -> None:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(
            model=model_name,
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
                f"  - {s.heading} ({s.word_count} words): {s.notes}"
                for s in outline.sections
            )
            faq_text = "\n".join(
                f"  - {q}" for q in outline.faq_questions
            ) if outline.faq_questions else "  (none)"
            return (
                f"Blog title: \"{outline.title}\"\n"
                f"Post type: {outline.post_type}\n"
                f"Target keyword: \"{outline.target_keyword}\"\n"
                f"Meta description: \"{outline.meta_description}\"\n"
                f"CTA: \"{outline.cta}\"\n\n"
                f"Sections:\n{sections_text}\n\n"
                f"FAQ questions:\n{faq_text}"
            )
        elif blog_html:
            plain = re.sub(r"<[^>]+>", " ", blog_html)
            # Allow more context for video scripts — up to 4000 chars
            truncated = plain[:4000]
            title = blog_title or "Blog Post"
            return f"Blog title: \"{title}\"\n\nContent:\n{truncated}"
        else:
            raise ValueError("Either 'outline' or 'blog_html' must be provided.")

    def generate_script(
        self,
        brand: str = "SellerBuddy",
        niche: str = "AI-powered Amazon advertising automation SaaS",
        target_duration_minutes: int = 8,
        outline: Optional[ContentOutline] = None,
        blog_html: Optional[str] = None,
        blog_title: Optional[str] = None,
    ) -> dict:
        """
        Generate a full YouTube video script.

        Returns dict with: title, description, tags, segments, total_duration_seconds, thumbnail_suggestion
        """
        context = self._build_context(outline, blog_html, blog_title)
        target_seconds = target_duration_minutes * 60

        messages = [
            SystemMessage(content=(
                f"You are a YouTube content strategist and scriptwriter for {brand}, a {niche}. "
                "Create a complete YouTube video script from the provided blog content.\n\n"
                "Rules:\n"
                f"- Target total duration: {target_duration_minutes} minutes ({target_seconds} seconds).\n"
                "- Structure the script as segments with timestamps.\n"
                "- Required segments:\n"
                "  1. Hook (0:00, 15-30 sec): Open with a surprising stat, bold question, or pain point.\n"
                "  2. Intro (after hook, 20-30 sec): Introduce the topic and what viewers will learn.\n"
                "  3. Main content (3-6 segments): Break the blog content into digestible video sections.\n"
                "  4. CTA + Outro (final 30-60 sec): Subscribe, like, comment prompt + brand CTA.\n"
                "- For each segment provide:\n"
                "  - timestamp: cumulative timestamp string (e.g. \"0:00\", \"0:30\", \"2:15\")\n"
                "  - section_title: short label for this part\n"
                "  - narration: exactly what the presenter should say (conversational, engaging tone)\n"
                "  - on_screen_text: text overlay or lower third to display (brief, impactful)\n"
                "  - b_roll_suggestion: what visuals/footage to show during this segment\n"
                "  - duration_seconds: how long this segment lasts\n"
                "- Also generate:\n"
                "  - title: SEO-optimized YouTube title (60 chars max)\n"
                "  - description: YouTube description (2-3 sentences + relevant hashtags)\n"
                "  - tags: 8-12 relevant YouTube tags\n"
                "  - thumbnail_suggestion: a single plain string describing the ideal thumbnail (text, imagery, colors). Must be a string, NOT an object.\n\n"
                "Return a single JSON object with keys: title, description, tags, segments, thumbnail_suggestion.\n"
                "Return ONLY the JSON object. No markdown fences."
            )),
            HumanMessage(content=context),
        ]

        response = self.llm.invoke(messages)
        text = _strip_fences(response.content.strip())
        data = json.loads(text)

        # Parse segments
        segments = [ScriptSegment(**seg) for seg in data.get("segments", [])]

        total_duration = sum(s.duration_seconds for s in segments)

        # Defensive: thumbnail_suggestion may come back as a dict instead of string
        thumbnail = data.get("thumbnail_suggestion", "")
        if isinstance(thumbnail, dict):
            # Flatten dict into a readable string
            parts = [f"{k}: {v}" for k, v in thumbnail.items()]
            thumbnail = " | ".join(parts)

        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "tags": data.get("tags", []),
            "segments": segments,
            "total_duration_seconds": total_duration,
            "thumbnail_suggestion": thumbnail,
        }
