"""
SEO Agent for SellerBuddy
=============================
Runs weekly keyword research using Google Search Console, identifies blog
topics with the highest traffic potential, and generates SEO-optimised
outlines ready for the Content Writer.

Three-step pipeline:
  1. _classify_keywords  — Analyse GSC data, classify by taxonomy, score opportunities
  2. _generate_topics    — Cluster into 2 blog topics (How-To + Comparison per week)
  3. _generate_outline   — Produce full content outlines (1,800-2,500 words each)

Optional Step 4: push outlines as Draft blog_post nodes to Drupal via JSON:API.
"""

from __future__ import annotations

import json
import os
import re
from typing import List, Optional

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GSCRow(BaseModel):
    query: str
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    position: float = 0.0
    page: str = "/"


class KeywordOpportunity(BaseModel):
    keyword: str
    category: str          # problem-aware | category | pain-point | education | competitor
    impressions: int
    clicks: int
    position: float
    opportunity: str       # quick-win | grow | new


class BlogTopic(BaseModel):
    title: str
    post_type: str         # how-to | comparison | list | guide
    target_keyword: str
    secondary_keywords: List[str]
    estimated_word_count: int
    cta: str


class ContentSection(BaseModel):
    heading: str
    word_count: int
    notes: str


class ContentOutline(BaseModel):
    title: str
    post_type: str
    target_keyword: str
    meta_description: str
    schema_types: List[str]
    featured_image_spec: str
    sections: List[ContentSection]
    cta: str
    internal_links: List[str]
    faq_questions: List[str]


class SEOWeeklyRunRequest(BaseModel):
    site_url: str
    gsc_data: List[GSCRow] = []
    brand: str = "SellerBuddy"
    niche: str = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"


class SEOWeeklyRunResult(BaseModel):
    keyword_opportunities: List[KeywordOpportunity]
    blog_topics: List[BlogTopic]
    outlines: List[ContentOutline]


class SEOGenerateOutlineRequest(BaseModel):
    title: str
    target_keyword: str
    post_type: str = "how-to"
    secondary_keywords: List[str] = []
    brand: str = "SellerBuddy"
    niche: str = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"


class SEOPushToDrupalRequest(BaseModel):
    outline: ContentOutline
    author: str = "SellerBuddy"
    category: str = "SEO"


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TAXONOMY = {
    "problem-aware": "User is aware of a problem but not the solution. Volume 2K-8K/mo.",
    "category": "User knows the category/solution type. Volume 1K-5K/mo.",
    "pain-point": "Specific pain or frustration keyword. Volume 500-2K/mo.",
    "education": "How-to / what-is informational intent. Volume 3K-10K/mo.",
    "competitor": "Mentions a competitor brand or tool. Volume 500-1.5K/mo.",
}

CTA = "Start your free trial — automate your Amazon ads in minutes"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class SEOAgent:
    def __init__(self):
        model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        fast_model = os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm_fast = ChatOpenAI(
            model=fast_model, temperature=0.2, openai_api_key=api_key
        )
        self.llm_gen = ChatOpenAI(
            model=model_name, temperature=0.7, openai_api_key=api_key
        )

    # ------------------------------------------------------------------
    # Step 1: keyword analysis
    # ------------------------------------------------------------------
    def _classify_keywords(
        self, gsc_data: List[GSCRow], brand: str, niche: str
    ) -> List[KeywordOpportunity]:
        if not gsc_data:
            return []

        rows_text = "\n".join(
            f'- "{r.query}" | impressions={r.impressions} clicks={r.clicks} '
            f"position={r.position:.1f}"
            for r in gsc_data
        )
        taxonomy_text = "\n".join(f"  {k}: {v}" for k, v in TAXONOMY.items())

        messages = [
            SystemMessage(content=(
                f"You are an SEO strategist for {brand}, a {niche}. "
                "Classify each keyword into exactly one taxonomy category and assign an opportunity label."
            )),
            HumanMessage(content=f"""
Taxonomy categories:
{taxonomy_text}

Opportunity labels:
- quick-win: position 11-20, decent impressions — small push needed
- grow: position 1-10 but low CTR — optimise meta / title
- new: position >20 or no data — create fresh content

Keywords to classify:
{rows_text}

Return a JSON array. Each element:
{{
  "keyword": "<query>",
  "category": "<taxonomy>",
  "impressions": <int>,
  "clicks": <int>,
  "position": <float>,
  "opportunity": "<quick-win|grow|new>"
}}
Return ONLY the JSON array, no markdown fences.
"""),
        ]

        response = self.llm_fast.invoke(messages)
        text = response.content.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        data = json.loads(text)
        return [KeywordOpportunity(**item) for item in data]

    # ------------------------------------------------------------------
    # Step 2: topic ideation
    # ------------------------------------------------------------------
    def _generate_topics(
        self,
        opportunities: List[KeywordOpportunity],
        brand: str,
        niche: str,
    ) -> List[BlogTopic]:
        kw_summary = "\n".join(
            f'- [{o.category} / {o.opportunity}] "{o.keyword}" (pos {o.position:.1f})'
            for o in opportunities
        ) or "- No GSC data; generate from niche knowledge"

        messages = [
            SystemMessage(content=(
                f"You are a content strategist for {brand}, a {niche}. "
                "Plan exactly 2 blog posts for the week following the content workflow below."
            )),
            HumanMessage(content=f"""
Content workflow:
- Post 1: How-To / Guide  (target: education or problem-aware keyword)
- Post 2: Comparison / List  (target: category or competitor keyword)
- Word count: 1,800-2,500 words each
- CTA for both: "{CTA}"

Keyword opportunities this week:
{kw_summary}

Return a JSON array of exactly 2 objects:
{{
  "title": "<H1 blog title>",
  "post_type": "<how-to|comparison|list|guide>",
  "target_keyword": "<primary keyword>",
  "secondary_keywords": ["<kw1>", "<kw2>"],
  "estimated_word_count": <int between 1800-2500>,
  "cta": "<call-to-action text>"
}}
Return ONLY the JSON array, no markdown fences.
"""),
        ]

        response = self.llm_gen.invoke(messages)
        text = response.content.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        data = json.loads(text)
        return [BlogTopic(**item) for item in data]

    # ------------------------------------------------------------------
    # Step 3: outline generation
    # ------------------------------------------------------------------
    def _generate_outline(
        self,
        topic: BlogTopic,
        brand: str,
        niche: str,
    ) -> ContentOutline:
        is_how_to = topic.post_type in ("how-to", "guide")
        schema_types = ["BlogPosting"]
        if is_how_to:
            schema_types.append("FAQPage")

        messages = [
            SystemMessage(content=(
                f"You are a senior SEO content writer for {brand}, a {niche}. "
                "Create a detailed content outline following the specified format."
            )),
            HumanMessage(content=f"""
Post details:
- Title: {topic.title}
- Type: {topic.post_type}
- Target keyword: {topic.target_keyword}
- Secondary keywords: {', '.join(topic.secondary_keywords)}
- Target word count: {topic.estimated_word_count}
- Schema types: {', '.join(schema_types)}
- CTA: {topic.cta}

Rules:
- Featured image: 1200x628 px, title as text overlay (Canva)
- Add schema: {', '.join(schema_types)}
- Include 3-5 FAQ questions {"(required for FAQPage schema)" if is_how_to else ""}
- Include 2-3 internal link suggestions (use paths like /features, /pricing, /blog)
- Meta description: 150-160 chars, include target keyword

Return a single JSON object:
{{
  "title": "<H1>",
  "post_type": "{topic.post_type}",
  "target_keyword": "<keyword>",
  "meta_description": "<150-160 char description>",
  "schema_types": {schema_types},
  "featured_image_spec": "1200x628px | Canva | title text overlay",
  "sections": [
    {{"heading": "<H2 or H3>", "word_count": <int>, "notes": "<brief guidance>"}}
  ],
  "cta": "<call-to-action>",
  "internal_links": ["<path1>", "<path2>"],
  "faq_questions": ["<q1>", "<q2>", "<q3>"]
}}
Return ONLY the JSON object, no markdown fences.
"""),
        ]

        response = self.llm_gen.invoke(messages)
        text = response.content.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        data = json.loads(text)
        data["sections"] = [ContentSection(**s) for s in data.get("sections", [])]
        return ContentOutline(**data)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def weekly_run(self, request: SEOWeeklyRunRequest) -> SEOWeeklyRunResult:
        """Full 3-step pipeline: classify → topics → outlines."""
        opportunities = self._classify_keywords(
            request.gsc_data, request.brand, request.niche
        )
        topics = self._generate_topics(opportunities, request.brand, request.niche)
        outlines = [
            self._generate_outline(topic, request.brand, request.niche)
            for topic in topics
        ]
        return SEOWeeklyRunResult(
            keyword_opportunities=opportunities,
            blog_topics=topics,
            outlines=outlines,
        )

    def generate_outline(self, request: SEOGenerateOutlineRequest) -> ContentOutline:
        """Generate a single outline on demand."""
        topic = BlogTopic(
            title=request.title,
            post_type=request.post_type,
            target_keyword=request.target_keyword,
            secondary_keywords=request.secondary_keywords,
            estimated_word_count=2000,
            cta=CTA,
        )
        return self._generate_outline(topic, request.brand, request.niche)
