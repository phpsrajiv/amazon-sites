"""
Tweet Thread Generator
=======================
Takes a ContentOutline (or raw blog HTML) and produces a 5-8 tweet thread
with a hook, key points, and CTA.

Uses the fast model (gpt-3.5-turbo) with slightly higher temperature for
engaging, creative copy.
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
from src.models.twitter import Tweet

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


class TwitterGenerator:
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

    def generate_thread(
        self,
        brand: str = "SellerBuddy",
        outline: Optional[ContentOutline] = None,
        blog_html: Optional[str] = None,
        blog_title: Optional[str] = None,
    ) -> List[Tweet]:
        """Generate a 5-8 tweet thread."""
        context = self._build_context(outline, blog_html, blog_title)

        messages = [
            SystemMessage(content=(
                f"You are a Twitter/X content strategist for {brand}. "
                "Create a tweet thread from the provided blog content.\n\n"
                "Rules:\n"
                "- Generate 5-8 tweets as a JSON array.\n"
                "- Tweet 1: Hook — a provocative question or surprising stat. "
                'End with "A thread 🧵"\n'
                "- Tweets 2 to N-1: One key point per tweet. Use short punchy "
                "sentences, numbers, and emojis sparingly.\n"
                "- Final tweet: CTA with a link placeholder [LINK].\n"
                "- HARD CONSTRAINT: each tweet MUST be 280 characters or fewer.\n"
                "- Each tweet object: tweet_number, text, char_count.\n"
                "- char_count must accurately reflect the length of text.\n\n"
                "Return ONLY the JSON array. No markdown fences."
            )),
            HumanMessage(content=context),
        ]

        response = self.llm.invoke(messages)
        text = _strip_fences(response.content.strip())
        data = json.loads(text)

        tweets = []
        for item in data:
            tweet_text = item["text"]
            # Enforce 280-char limit — truncate if LLM exceeded
            if len(tweet_text) > 280:
                logger.warning(
                    "Tweet %d exceeded 280 chars (%d), truncating.",
                    item["tweet_number"],
                    len(tweet_text),
                )
                tweet_text = tweet_text[:277] + "..."

            tweets.append(Tweet(
                tweet_number=item["tweet_number"],
                text=tweet_text,
                char_count=len(tweet_text),
            ))

        return tweets
