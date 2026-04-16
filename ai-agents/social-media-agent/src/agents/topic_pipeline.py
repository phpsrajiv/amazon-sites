"""
Topic Pipeline — auto-sources content topics from 3 systems and generates
weekly social media content for all platforms.

Sources:
  1. Calendar Events (local) — upcoming festivals, sales, holidays
  2. SEO Agent (HTTP) — keyword opportunities + blog topics
  3. Drupal Blogs (HTTP) — recent unpromoted blog posts

Flow:
  gather candidates → dedup against recent posts → LLM selects best topics →
  generate FB + LinkedIn + IG content for each → return weekly plan
"""

import json
import logging
import os
import re
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.models.common import Platform, ContentTone
from src.models.topic_pipeline import (
    TopicSource,
    CandidateTopic,
    SelectedTopic,
    PlatformContent,
    WeeklyContentPlanRequest,
    WeeklyContentPlanResponse,
)
from src.models.facebook import FacebookRequest
from src.models.linkedin import LinkedInRequest
from src.models.instagram import InstagramRequest
from src.models.timing import TimingRequest
from src.models.logging import DecisionType, PostLogQuery

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


class TopicPipeline:
    """Orchestrates weekly content topic selection and generation."""

    def __init__(
        self,
        calendar_service,
        seo_client,
        drupal_client,
        agent_logger,
        timing_engine,
        facebook_gen,
        linkedin_gen,
        instagram_gen,
    ):
        self.calendar_service = calendar_service
        self.seo_client = seo_client
        self.drupal_client = drupal_client
        self.agent_logger = agent_logger
        self.timing_engine = timing_engine
        self.facebook_gen = facebook_gen
        self.linkedin_gen = linkedin_gen
        self.instagram_gen = instagram_gen

        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=0.4,
        )

    # ------------------------------------------------------------------
    # Step 1: Gather candidates from all sources
    # ------------------------------------------------------------------

    def _gather_calendar_topics(self, days_ahead: int = 14) -> list[CandidateTopic]:
        """Pull upcoming events from the calendar and convert to candidates."""
        events = self.calendar_service.get_upcoming_events(days_ahead=days_ahead)
        candidates = []
        for event in events:
            themes = ", ".join(event.suggested_themes[:3]) if event.suggested_themes else ""
            candidates.append(CandidateTopic(
                source=TopicSource.CALENDAR_EVENT,
                title=event.name,
                description=f"{event.category} event from {event.date_start} to {event.date_end}. Themes: {themes}",
                relevance_score=event.relevance_score,
                source_metadata={
                    "event_name": event.name,
                    "date_start": str(event.date_start),
                    "date_end": str(event.date_end),
                    "category": event.category,
                    "posting_urgency": event.posting_urgency,
                    "platforms": [p.value for p in event.platforms],
                    "suggested_themes": event.suggested_themes,
                    "pre_event_days": event.pre_event_days,
                },
            ))
        logger.info(f"Calendar: gathered {len(candidates)} event candidates")
        return candidates

    def _gather_seo_topics(self, brand: str = "SellerBuddy") -> list[CandidateTopic]:
        """Pull keyword opportunities + blog topics from the SEO Agent."""
        result = self.seo_client.fetch_weekly_run(brand=brand)
        if result is None:
            return []

        candidates = []

        # Keyword opportunities
        for kw in result.get("keyword_opportunities", []):
            opportunity = kw.get("opportunity", "new")
            score_map = {"quick-win": 0.9, "grow": 0.7, "new": 0.5}
            score = score_map.get(opportunity, 0.5)
            candidates.append(CandidateTopic(
                source=TopicSource.SEO_KEYWORD,
                title=f"SEO: {kw.get('keyword', 'unknown')}",
                description=(
                    f"Keyword opportunity ({opportunity}): {kw.get('keyword', '')}. "
                    f"Position: {kw.get('position', 'N/A')}, "
                    f"Impressions: {kw.get('impressions', 0)}, Clicks: {kw.get('clicks', 0)}"
                ),
                relevance_score=score,
                source_metadata=kw,
            ))

        # Blog topics from SEO research
        for bt in result.get("blog_topics", []):
            candidates.append(CandidateTopic(
                source=TopicSource.SEO_KEYWORD,
                title=bt.get("title", "Untitled SEO topic"),
                description=(
                    f"SEO blog topic ({bt.get('post_type', 'article')}). "
                    f"Target keyword: {bt.get('target_keyword', 'N/A')}. "
                    f"Secondary: {', '.join(bt.get('secondary_keywords', [])[:3])}"
                ),
                relevance_score=0.8,
                source_metadata=bt,
            ))

        logger.info(f"SEO Agent: gathered {len(candidates)} keyword/topic candidates")
        return candidates

    def _gather_blog_topics(self, max_blogs: int = 10) -> list[CandidateTopic]:
        """Pull recent blog posts from Drupal for repurposing."""
        posts = self.drupal_client.list_blog_posts(limit=max_blogs)
        if not posts:
            return []

        candidates = []
        for i, post in enumerate(posts):
            # Score decays by recency: newest=0.9, oldest=0.4
            score = 0.9 - (i / max(len(posts), 1)) * 0.5
            score = max(score, 0.4)
            candidates.append(CandidateTopic(
                source=TopicSource.BLOG_REPURPOSE,
                title=f"Blog: {post.get('title', 'Untitled')}",
                description=f"Existing blog post in category '{post.get('category', 'General')}'. Repurpose key insights for social media.",
                relevance_score=round(score, 2),
                source_metadata={
                    "drupal_id": post.get("id", ""),
                    "title": post.get("title", ""),
                    "category": post.get("category", ""),
                },
            ))

        logger.info(f"Drupal: gathered {len(candidates)} blog candidates")
        return candidates

    # ------------------------------------------------------------------
    # Step 2: Dedup against recent posts
    # ------------------------------------------------------------------

    def _get_recent_post_topics(self) -> list[str]:
        """Get content previews of recently generated posts for dedup."""
        query = PostLogQuery(limit=50)
        recent_posts = self.agent_logger.get_posts(query)
        topics = []
        for p in recent_posts:
            topics.append(p.content_preview)
        return topics

    # ------------------------------------------------------------------
    # Step 3: LLM-powered topic selection
    # ------------------------------------------------------------------

    def _select_topics(
        self,
        candidates: list[CandidateTopic],
        recent_posts: list[str],
        num_topics: int = 5,
        brand: str = "SellerBuddy",
    ) -> list[SelectedTopic]:
        """Use LLM to select the best topics from candidates, avoiding recent duplicates."""
        if not candidates:
            return []

        # Build candidate list for the prompt
        candidate_lines = []
        for i, c in enumerate(candidates):
            candidate_lines.append(
                f"{i+1}. [{c.source.value}] {c.title} (score: {c.relevance_score})\n"
                f"   Description: {c.description}"
            )

        recent_lines = []
        for rp in recent_posts[:20]:
            recent_lines.append(f"- {rp[:150]}")

        messages = [
            SystemMessage(content=(
                f"You are a social media content strategist for {brand}, an AI-powered Amazon seller tool in India.\n\n"
                "Your job is to select the BEST topics for this week's social media content from the candidates below.\n\n"
                "## Selection Criteria (priority order):\n"
                "1. **Deduplication** — Do NOT select topics that overlap with recently published posts\n"
                "2. **Time sensitivity** — Calendar events happening soon should be prioritized\n"
                "3. **Source diversity** — Mix calendar events, SEO keywords, and blog repurposing\n"
                "4. **Opportunity score** — Higher relevance scores indicate better opportunities\n"
                "5. **Freshness** — Prefer topics not covered recently\n"
                "6. **Variety** — Mix educational, promotional, and festive content\n\n"
                "## Tone Assignment Rules:\n"
                "- Calendar events (festivals) → 'festive'\n"
                "- Calendar events (ecommerce sales) → 'promotional'\n"
                "- Calendar events (national/awareness) → 'inspirational'\n"
                "- SEO keywords → 'educational'\n"
                "- Blog repurpose → 'conversational'\n\n"
                f"Select up to {num_topics} topics. You may select fewer if there aren't enough good candidates.\n\n"
                "Respond in JSON array format:\n"
                "[\n"
                '  {"topic": "The topic title for content creation", "source": "calendar_event|seo_keyword|blog_repurpose", '
                '"rationale": "Why this topic was selected", "suggested_tone": "festive|promotional|inspirational|educational|conversational|professional", '
                '"event_context": "event name if applicable, else null", "priority": 1}\n'
                "]\n\n"
                "Priority 1 = highest priority, higher numbers = lower priority."
            )),
            HumanMessage(content=(
                f"## Candidate Topics ({len(candidates)} total):\n\n"
                + "\n\n".join(candidate_lines)
                + "\n\n## Recently Published Posts (avoid overlap):\n\n"
                + ("\n".join(recent_lines) if recent_lines else "No recent posts found.")
            )),
        ]

        response = self.llm.invoke(messages)
        parsed = json.loads(_strip_fences(response.content))

        selected = []
        for item in parsed:
            try:
                selected.append(SelectedTopic(
                    topic=item["topic"],
                    source=TopicSource(item["source"]),
                    rationale=item.get("rationale", ""),
                    suggested_tone=ContentTone(item.get("suggested_tone", "conversational")),
                    event_context=item.get("event_context"),
                    priority=item.get("priority", len(selected) + 1),
                ))
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping invalid topic from LLM: {e}")
                continue

        # Log the selection decision
        self.agent_logger.log_decision(
            decision_type=DecisionType.TOPIC_SELECTION,
            agent_name="topic_pipeline",
            action=f"Selected {len(selected)} topics from {len(candidates)} candidates",
            rationale=f"Sources: {len([c for c in candidates if c.source == TopicSource.CALENDAR_EVENT])} calendar, "
                      f"{len([c for c in candidates if c.source == TopicSource.SEO_KEYWORD])} SEO, "
                      f"{len([c for c in candidates if c.source == TopicSource.BLOG_REPURPOSE])} blog. "
                      f"Deduped against {len(recent_posts)} recent posts.",
            input_summary={
                "total_candidates": len(candidates),
                "recent_posts_checked": len(recent_posts),
                "num_topics_requested": num_topics,
            },
            output_summary={
                "selected_topics": [s.topic for s in selected],
                "sources_used": [s.source.value for s in selected],
            },
        )

        logger.info(f"LLM selected {len(selected)} topics from {len(candidates)} candidates")
        return selected

    # ------------------------------------------------------------------
    # Step 4: Generate content for each selected topic
    # ------------------------------------------------------------------

    def _generate_content_for_topic(self, selected: SelectedTopic, brand: str) -> PlatformContent:
        """Generate Facebook + LinkedIn + Instagram content for a single topic."""
        event_ctx = selected.event_context

        # Facebook
        fb_req = FacebookRequest(
            topic=selected.topic,
            brand=brand,
            tone=selected.suggested_tone,
            event_context=event_ctx,
        )
        fb_result = self.facebook_gen.generate(fb_req)

        # LinkedIn
        li_req = LinkedInRequest(
            topic=selected.topic,
            brand=brand,
            tone=ContentTone.PROFESSIONAL if selected.suggested_tone == ContentTone.EDUCATIONAL else selected.suggested_tone,
            event_context=event_ctx,
        )
        li_result = self.linkedin_gen.generate(li_req)

        # Instagram
        ig_req = InstagramRequest(
            topic=selected.topic,
            brand=brand,
            tone=selected.suggested_tone,
            event_context=event_ctx,
        )
        ig_result = self.instagram_gen.generate(ig_req)

        # Timing recommendation for the next 7 days
        today = date.today()
        timing_req = TimingRequest(
            platforms=[Platform.FACEBOOK, Platform.LINKEDIN, Platform.INSTAGRAM],
            date_start=today,
            date_end=today + timedelta(days=7),
        )
        timing = self.timing_engine.recommend_timing(timing_req)

        return PlatformContent(
            topic=selected.topic,
            source=selected.source,
            facebook=fb_result,
            linkedin=li_result,
            instagram=ig_result,
            timing=timing,
        )

    # ------------------------------------------------------------------
    # Main orchestrator
    # ------------------------------------------------------------------

    def generate_weekly_plan(self, request: WeeklyContentPlanRequest) -> WeeklyContentPlanResponse:
        """
        Full weekly content pipeline:
        1. Gather candidates from all 3 sources
        2. Dedup against recent posts
        3. LLM selects best topics
        4. Generate platform content for each
        5. Return complete plan
        """
        plan_id = str(uuid.uuid4())
        warnings: list[str] = []

        # Step 1: Gather candidates
        calendar_topics = self._gather_calendar_topics(days_ahead=request.calendar_days_ahead)
        seo_topics = self._gather_seo_topics(brand=request.brand)
        blog_topics = self._gather_blog_topics(max_blogs=request.max_blogs)

        if not seo_topics:
            warnings.append("SEO Agent was unreachable — plan generated without SEO-sourced topics")

        all_candidates = calendar_topics + seo_topics + blog_topics

        if not all_candidates:
            warnings.append("No topic sources available — returning empty plan")
            return WeeklyContentPlanResponse(
                plan_id=plan_id,
                generated_at=datetime.now(),
                topics_considered=0,
                topics_selected=0,
                content=[],
                sources_summary={
                    "calendar": 0,
                    "seo": 0,
                    "blog": 0,
                },
                warnings=warnings,
            )

        # Step 2: Get recent posts for dedup
        recent_posts = self._get_recent_post_topics()

        # Step 3: LLM selects best topics
        selected = self._select_topics(
            candidates=all_candidates,
            recent_posts=recent_posts,
            num_topics=request.num_topics,
            brand=request.brand,
        )

        # Step 4: Generate content for each selected topic
        content_list: list[PlatformContent] = []
        for topic in selected:
            try:
                pc = self._generate_content_for_topic(topic, request.brand)
                content_list.append(pc)
            except Exception as e:
                logger.error(f"Failed to generate content for topic '{topic.topic}': {e}")
                warnings.append(f"Content generation failed for topic: {topic.topic}")

        # Build sources summary
        sources_summary = {
            "calendar": len(calendar_topics),
            "seo": len(seo_topics),
            "blog": len(blog_topics),
            "total_candidates": len(all_candidates),
            "topics_selected": len(selected),
            "content_generated": len(content_list),
        }

        # Log the plan generation
        self.agent_logger.log_decision(
            decision_type=DecisionType.WEEKLY_PLAN_GENERATED,
            agent_name="topic_pipeline",
            action=f"Generated weekly content plan with {len(content_list)} topics",
            rationale=(
                f"Gathered {len(all_candidates)} candidates "
                f"({len(calendar_topics)} calendar, {len(seo_topics)} SEO, {len(blog_topics)} blog). "
                f"Selected {len(selected)}, generated content for {len(content_list)}."
            ),
            input_summary=request.model_dump(mode="json"),
            output_summary={
                "plan_id": plan_id,
                "topics": [pc.topic for pc in content_list],
                "sources": sources_summary,
                "warnings": warnings,
            },
        )

        return WeeklyContentPlanResponse(
            plan_id=plan_id,
            generated_at=datetime.now(),
            topics_considered=len(all_candidates),
            topics_selected=len(content_list),
            content=content_list,
            sources_summary=sources_summary,
            warnings=warnings,
        )
