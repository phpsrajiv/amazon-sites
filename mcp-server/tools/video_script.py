"""
Video Script Agent tools — wraps http://localhost:8003
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from utils import client

_NICHE = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def video_script_health() -> dict:
        """Check whether the Video Script Agent service is running."""
        return client.get("video_script", "/health")

    @mcp.tool()
    def video_youtube_script(
        brand: str = "SellerBuddy",
        niche: str = _NICHE,
        target_duration_minutes: int = 8,
        outline_json: str | None = None,
        blog_html: str | None = None,
        blog_title: str | None = None,
    ) -> dict:
        """
        Generate a full YouTube video script with timestamps, on-screen text
        cues, narration, and B-roll suggestions.

        Provide either outline_json (from seo_generate_outline) OR blog_html
        (from content_write_blog). Using blog_html gives richer narration.

        Args:
            brand: Brand name used in the script intro/outro
            niche: Product/market niche for contextual accuracy
            target_duration_minutes: Desired video length in minutes (default 8)
            outline_json: JSON string of a ContentOutline (optional)
            blog_html: Full blog HTML string (optional, preferred over outline)
            blog_title: Blog title — required when blog_html is provided
        """
        body: dict = {
            "brand": brand,
            "niche": niche,
            "target_duration_minutes": target_duration_minutes,
        }
        if outline_json:
            body["outline"] = json.loads(outline_json)
        if blog_html:
            body["blog_html"] = blog_html
        if blog_title:
            body["blog_title"] = blog_title
        return client.post("video_script", "/api/video/youtube-script", body)

    @mcp.tool()
    def video_shorts_hooks(
        brand: str = "SellerBuddy",
        num_hooks: int = 3,
        outline_json: str | None = None,
        blog_html: str | None = None,
        blog_title: str | None = None,
    ) -> dict:
        """
        Generate YouTube Shorts hook scripts — punchy 60-second scripts
        designed to maximise retention in the first 3 seconds.

        Provide either outline_json OR blog_html.

        Args:
            brand: Brand name for hook voice
            num_hooks: Number of hook variants to generate (default 3)
            outline_json: JSON string of a ContentOutline (optional)
            blog_html: Full blog HTML string (optional, preferred over outline)
            blog_title: Blog title — required when blog_html is provided
        """
        body: dict = {"brand": brand, "num_hooks": num_hooks}
        if outline_json:
            body["outline"] = json.loads(outline_json)
        if blog_html:
            body["blog_html"] = blog_html
        if blog_title:
            body["blog_title"] = blog_title
        return client.post("video_script", "/api/video/shorts-hooks", body)

    @mcp.tool()
    def video_script_full_pipeline(
        brand: str = "SellerBuddy",
        niche: str = _NICHE,
        target_duration_minutes: int = 8,
        num_shorts_hooks: int = 3,
        outline_json: str | None = None,
        blog_html: str | None = None,
        blog_title: str | None = None,
    ) -> dict:
        """
        Generate both a YouTube video script and Shorts hooks in one call.

        Returns youtube_script and shorts_hooks in a single response.

        Args:
            brand: Brand name for all generated scripts
            niche: Product/market niche for contextual accuracy
            target_duration_minutes: Desired YouTube video length (default 8)
            num_shorts_hooks: Number of Shorts hook variants (default 3)
            outline_json: JSON string of a ContentOutline (optional)
            blog_html: Full blog HTML string (optional, preferred over outline)
            blog_title: Blog title — required when blog_html is provided
        """
        body: dict = {
            "brand": brand,
            "niche": niche,
            "target_duration_minutes": target_duration_minutes,
            "num_shorts_hooks": num_shorts_hooks,
        }
        if outline_json:
            body["outline"] = json.loads(outline_json)
        if blog_html:
            body["blog_html"] = blog_html
        if blog_title:
            body["blog_title"] = blog_title
        return client.post("video_script", "/api/video/full-pipeline", body)
