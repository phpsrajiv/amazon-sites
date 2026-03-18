"""
Blog Writer Agent
=================
Takes a ContentOutline (produced by the SEO Agent) and generates a full
blog post (1,800-2,500 words) in semantic HTML.

Strategy:
  1. Generate each section individually (honours per-section word counts,
     avoids output-token limits).
  2. Run a single "polish" pass that adds an intro, weaves internal links,
     builds the FAQ section, appends the CTA, and ensures clean H2/H3 nesting.
  3. Programmatic word-count validation.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.models.outline import ContentOutline, ContentSection

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    """Remove optional markdown code fences from LLM output."""
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _count_words(html: str) -> int:
    """Rough word count: strip HTML tags, split on whitespace."""
    plain = re.sub(r"<[^>]+>", " ", html)
    return len(plain.split())


class BlogWriter:
    def __init__(self) -> None:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            openai_api_key=api_key,
        )

    # ------------------------------------------------------------------
    # Step 1: section-by-section generation
    # ------------------------------------------------------------------
    def _write_section(
        self,
        section: ContentSection,
        outline: ContentOutline,
        previous_headings: List[str],
        brand: str,
        niche: str,
    ) -> str:
        """Generate a single section's HTML fragment."""
        context = ""
        if previous_headings:
            context = (
                "Sections already written (for coherence — do NOT repeat content):\n"
                + "\n".join(f"  - {h}" for h in previous_headings)
            )

        messages = [
            SystemMessage(content=(
                f"You are a senior content writer for {brand}, a {niche}. "
                "Write engaging, actionable blog content in semantic HTML. "
                "Rules:\n"
                "- Use <h2> for main headings, <h3> for sub-headings.\n"
                "- Use <p>, <ul>, <ol>, <strong>, <em> — no <h1> (Drupal renders the title).\n"
                "- Be specific, data-driven, and avoid fluff.\n"
                f"- Target keyword: \"{outline.target_keyword}\" — weave it in naturally.\n"
                "- Return ONLY the HTML fragment, no markdown fences, no wrapping <html>/<body>."
            )),
            HumanMessage(content=(
                f"Blog post title: \"{outline.title}\"\n\n"
                f"Section heading: \"{section.heading}\"\n"
                f"Target word count for this section: {section.word_count} words\n"
                f"Writing guidance: {section.notes}\n\n"
                f"{context}\n\n"
                "Write this section now. Output only the HTML fragment."
            )),
        ]

        response = self.llm.invoke(messages)
        return _strip_fences(response.content.strip())

    # ------------------------------------------------------------------
    # Step 2: polish pass
    # ------------------------------------------------------------------
    def _polish(
        self,
        sections_html: str,
        outline: ContentOutline,
        brand: str,
        niche: str,
    ) -> str:
        """
        Final assembly pass:
        - Add a compelling intro paragraph (150-200 words)
        - Weave in internal links naturally
        - Generate FAQ section with schema-friendly markup
        - Append CTA block
        - Ensure clean heading hierarchy
        """
        internal_links_text = "\n".join(
            f"  - {link}" for link in outline.internal_links
        ) or "  (none provided)"

        faq_text = "\n".join(
            f"  {i+1}. {q}" for i, q in enumerate(outline.faq_questions)
        ) or "  (none provided)"

        messages = [
            SystemMessage(content=(
                f"You are a senior editor for {brand}, a {niche}. "
                "You are finalising a blog post. Your job is to assemble the "
                "provided section HTML into a polished, publish-ready blog post.\n\n"
                "Rules:\n"
                "- Add a compelling intro paragraph (150-200 words) with a hook BEFORE the first <h2>.\n"
                f"- The intro must mention the target keyword \"{outline.target_keyword}\" in the first 100 words.\n"
                "- Weave the internal links naturally as <a> tags within the existing content "
                "(do NOT add a separate links section).\n"
                "- Generate a FAQ section at the end using this markup for each question:\n"
                '  <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">\n'
                '    <h3 itemprop="name">Question here</h3>\n'
                '    <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">\n'
                '      <p itemprop="text">Answer here (50-80 words)</p>\n'
                "    </div>\n"
                "  </div>\n"
                "- Append a CTA block at the very end.\n"
                "- Do NOT add an <h1> — Drupal renders the title.\n"
                "- Return ONLY the final HTML. No markdown fences."
            )),
            HumanMessage(content=(
                f"Blog title: \"{outline.title}\"\n"
                f"Meta description: \"{outline.meta_description}\"\n"
                f"Target keyword: \"{outline.target_keyword}\"\n\n"
                f"Internal links to weave in:\n{internal_links_text}\n\n"
                f"FAQ questions to answer:\n{faq_text}\n\n"
                f"CTA text: \"{outline.cta}\"\n\n"
                "--- SECTION HTML (assemble and polish) ---\n\n"
                f"{sections_html}"
            )),
        ]

        response = self.llm.invoke(messages)
        return _strip_fences(response.content.strip())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def write_blog(
        self,
        outline: ContentOutline,
        brand: str = "SellerBuddy",
        niche: str = "AI-powered Amazon advertising automation SaaS",
    ) -> tuple[str, int]:
        """
        Generate a full blog post from a ContentOutline.

        Returns:
            (body_html, word_count)
        """
        # Step 1: generate each section
        section_fragments: List[str] = []
        previous_headings: List[str] = []

        for section in outline.sections:
            logger.info("Writing section: %s (%d words)", section.heading, section.word_count)
            fragment = self._write_section(
                section=section,
                outline=outline,
                previous_headings=previous_headings,
                brand=brand,
                niche=niche,
            )
            section_fragments.append(fragment)
            previous_headings.append(section.heading)

        raw_html = "\n\n".join(section_fragments)

        # Step 2: polish pass
        logger.info("Running polish pass...")
        final_html = self._polish(raw_html, outline, brand, niche)

        # Step 3: validate word count
        word_count = _count_words(final_html)
        if word_count < 1800:
            logger.warning(
                "Blog is under target: %d words (target 1,800-2,500)", word_count
            )
        elif word_count > 2500:
            logger.warning(
                "Blog exceeds target: %d words (target 1,800-2,500)", word_count
            )
        else:
            logger.info("Blog word count: %d (within target range)", word_count)

        return final_html, word_count
