"""
Social Media Agent tools — wraps http://localhost:8005

Covers content generation (Facebook / LinkedIn / Instagram), smart timing,
calendar, news sentiment, engagement analytics, and audit logs.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from utils import client

_PLATFORMS = ["facebook", "linkedin", "instagram"]


def register(mcp: FastMCP) -> None:

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @mcp.tool()
    def social_health() -> dict:
        """Check whether the Social Media Agent service is running."""
        return client.get("social", "/health")

    # ------------------------------------------------------------------
    # Content generation — individual platforms
    # ------------------------------------------------------------------

    @mcp.tool()
    def social_generate_facebook(
        topic: str,
        brand: str = "SellerBuddy",
        tone: str = "conversational",
        event_context: str | None = None,
        num_variants: int = 3,
    ) -> dict:
        """
        Generate Facebook post variants for a given topic.

        Returns post text, hashtags, an engagement question, and an image
        prompt for each variant.

        Args:
            topic: What the post should be about
            brand: Brand voice/name to use
            tone: One of "professional", "conversational", "inspirational",
                  "educational", "promotional", "festive"
            event_context: Optional upcoming event or seasonal hook
            num_variants: Number of post variants to generate (default 3)
        """
        return client.post("social", "/api/social/generate/facebook", {
            "topic": topic,
            "brand": brand,
            "tone": tone,
            "event_context": event_context,
            "num_variants": num_variants,
        })

    @mcp.tool()
    def social_generate_linkedin(
        topic: str,
        brand: str = "SellerBuddy",
        tone: str = "professional",
        event_context: str | None = None,
    ) -> dict:
        """
        Generate a LinkedIn post for a given topic.

        Returns post copy optimised for professional reach and engagement.

        Args:
            topic: What the post should be about
            brand: Brand voice/name to use
            tone: One of "professional", "conversational", "inspirational",
                  "educational", "promotional", "festive"
            event_context: Optional upcoming event or seasonal hook
        """
        return client.post("social", "/api/social/generate/linkedin", {
            "topic": topic,
            "brand": brand,
            "tone": tone,
            "event_context": event_context,
        })

    @mcp.tool()
    def social_generate_instagram(
        topic: str,
        brand: str = "SellerBuddy",
        tone: str = "inspirational",
        event_context: str | None = None,
    ) -> dict:
        """
        Generate an Instagram post (caption + hashtags) for a given topic.

        Args:
            topic: What the post should be about
            brand: Brand voice/name to use
            tone: One of "professional", "conversational", "inspirational",
                  "educational", "promotional", "festive"
            event_context: Optional upcoming event or seasonal hook
        """
        return client.post("social", "/api/social/generate/instagram", {
            "topic": topic,
            "brand": brand,
            "tone": tone,
            "event_context": event_context,
        })

    @mcp.tool()
    def social_generate_all(
        topic: str,
        brand: str = "SellerBuddy",
        event_context: str | None = None,
    ) -> dict:
        """
        Generate content for all platforms (Facebook, LinkedIn, Instagram)
        in a single call, including smart timing recommendations.

        Use this when you want a complete social media package for a topic.

        Args:
            topic: What the posts should be about
            brand: Brand voice/name to use
            event_context: Optional upcoming event or seasonal hook
        """
        params: dict = {"topic": topic, "brand": brand}
        if event_context:
            params["event_context"] = event_context
        return client.post("social", "/api/social/generate/all", params=params)

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    @mcp.tool()
    def social_timing_recommend(
        date_start: str,
        date_end: str,
        platforms: list[str] = _PLATFORMS,
        slots_per_platform: int = 3,
    ) -> dict:
        """
        Get optimal posting time recommendations for a date range.

        Takes into account calendar events, news sentiment, and historical
        engagement data to score each slot.

        Args:
            date_start: Start date in ISO format (YYYY-MM-DD)
            date_end: End date in ISO format (YYYY-MM-DD)
            platforms: List of platforms — any of "facebook", "linkedin", "instagram"
            slots_per_platform: Number of time slots to recommend per platform
        """
        return client.post("social", "/api/social/timing/recommend", {
            "date_start": date_start,
            "date_end": date_end,
            "platforms": platforms,
            "slots_per_platform": slots_per_platform,
        })

    @mcp.tool()
    def social_weekly_schedule(
        week_start: str,
        platforms: list[str] = _PLATFORMS,
    ) -> dict:
        """
        Get a full week's optimised posting schedule across all platforms.

        Args:
            week_start: Monday of the target week in ISO format (YYYY-MM-DD)
            platforms: List of platforms — any of "facebook", "linkedin", "instagram"
        """
        return client.post("social", "/api/social/timing/weekly-schedule", {
            "week_start": week_start,
            "platforms": platforms,
        })

    # ------------------------------------------------------------------
    # Calendar
    # ------------------------------------------------------------------

    @mcp.tool()
    def social_calendar_events(days_ahead: int = 30) -> dict:
        """
        Get upcoming calendar events (holidays, Amazon events, promotions)
        that should inform social media content.

        Args:
            days_ahead: How many days into the future to look (default 30)
        """
        return client.get("social", "/api/social/calendar/events",
                          params={"days_ahead": days_ahead})

    # ------------------------------------------------------------------
    # News sentiment
    # ------------------------------------------------------------------

    @mcp.tool()
    def social_news_sentiment() -> dict:
        """
        Get the current news sentiment advisory.

        Returns a recommendation on whether to post normally, boost activity,
        reduce posting, or pause during a news crisis — along with rationale.
        """
        return client.get("social", "/api/social/news/sentiment")

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    @mcp.tool()
    def social_analytics_best_times(platform: str) -> dict:
        """
        Get historically best posting times for a specific platform based on
        logged engagement data.

        Args:
            platform: One of "facebook", "linkedin", "instagram"
        """
        return client.get("social", f"/api/social/analytics/best-times/{platform}")

    @mcp.tool()
    def social_weekly_report(week_start: str | None = None) -> dict:
        """
        Get the weekly engagement report for all platforms.

        Args:
            week_start: ISO date (YYYY-MM-DD) of the Monday to report on.
                        Defaults to the current week if omitted.
        """
        params = {}
        if week_start:
            params["week_start"] = week_start
        return client.get("social", "/api/social/analytics/weekly-report", params=params)

    # ------------------------------------------------------------------
    # Audit logs
    # ------------------------------------------------------------------

    @mcp.tool()
    def social_decision_logs(
        date_start: str | None = None,
        date_end: str | None = None,
        platform: str | None = None,
        agent_name: str | None = None,
        limit: int = 50,
    ) -> dict:
        """
        Query the agent's decision audit log.

        Useful for reviewing why the agent chose specific timing or content
        strategies.

        Args:
            date_start: Filter from this ISO date (YYYY-MM-DD)
            date_end: Filter to this ISO date (YYYY-MM-DD)
            platform: Filter by platform ("facebook" | "linkedin" | "instagram")
            agent_name: Filter by agent name (e.g. "timing_engine")
            limit: Maximum number of records to return (default 50)
        """
        params: dict = {"limit": limit}
        if date_start:
            params["date_start"] = date_start
        if date_end:
            params["date_end"] = date_end
        if platform:
            params["platform"] = platform
        if agent_name:
            params["agent_name"] = agent_name
        return client.get("social", "/api/social/logs/decisions", params=params)

    @mcp.tool()
    def social_post_logs(
        date_start: str | None = None,
        date_end: str | None = None,
        platform: str | None = None,
        limit: int = 50,
    ) -> dict:
        """
        Query the post history log.

        Args:
            date_start: Filter from this ISO date (YYYY-MM-DD)
            date_end: Filter to this ISO date (YYYY-MM-DD)
            platform: Filter by platform ("facebook" | "linkedin" | "instagram")
            limit: Maximum number of records to return (default 50)
        """
        params: dict = {"limit": limit}
        if date_start:
            params["date_start"] = date_start
        if date_end:
            params["date_end"] = date_end
        if platform:
            params["platform"] = platform
        return client.get("social", "/api/social/logs/posts", params=params)
