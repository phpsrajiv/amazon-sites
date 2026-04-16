"""
SEO Agent tools — wraps http://localhost:8001
"""

from __future__ import annotations

import json
from typing import Annotated

from mcp.server.fastmcp import FastMCP

from utils import client

_NICHE = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def seo_health() -> dict:
        """Check whether the SEO Agent service is running and its integrations are configured."""
        return client.get("seo", "/health")

    @mcp.tool()
    def seo_generate_outline(
        title: str,
        target_keyword: str,
        post_type: str = "how-to",
        secondary_keywords: list[str] = [],
        brand: str = "SellerBuddy",
        niche: str = _NICHE,
    ) -> dict:
        """
        Generate a single SEO-optimised blog outline on demand.

        Returns a ContentOutline with title, sections, CTA, FAQ questions,
        internal link suggestions, and meta description.

        Args:
            title: Blog post title, e.g. "How to Lower Your Amazon ACoS in 30 Days"
            target_keyword: Primary keyword to rank for
            post_type: One of "how-to", "comparison", "list", "guide"
            secondary_keywords: Additional keywords to weave into the outline
            brand: Brand name used in CTA and tone
            niche: Product/market niche description for context
        """
        return client.post("seo", "/api/seo/generate-outline", {
            "title": title,
            "target_keyword": target_keyword,
            "post_type": post_type,
            "secondary_keywords": secondary_keywords,
            "brand": brand,
            "niche": niche,
        })

    @mcp.tool()
    def seo_weekly_run(
        site_url: str,
        brand: str = "SellerBuddy",
        niche: str = _NICHE,
    ) -> dict:
        """
        Run the full weekly SEO pipeline using live Google Search Console data.

        Steps: keyword classification → blog topic selection → outline generation.
        Returns keyword opportunities, two blog topics (how-to + comparison),
        and a full ContentOutline for each topic.

        Args:
            site_url: GSC property URL, e.g. "https://sellerbuddy.com"
            brand: Brand name for tone/CTA
            niche: Product/market niche description
        """
        return client.post("seo", "/api/seo/weekly-run", {
            "site_url": site_url,
            "gsc_data": [],
            "brand": brand,
            "niche": niche,
        })

    @mcp.tool()
    def seo_push_to_drupal(
        outline_json: str,
        author: str = "SellerBuddy",
        category: str = "SEO",
    ) -> dict:
        """
        Push a ContentOutline to Drupal as a draft blog_post node.

        Requires DRUPAL_BASE_URL, DRUPAL_USERNAME, DRUPAL_PASSWORD set in the
        SEO Agent's environment.

        Args:
            outline_json: JSON string of a ContentOutline object (output of
                          seo_generate_outline or seo_weekly_run)
            author: Drupal author field
            category: Drupal category/taxonomy term
        """
        outline = json.loads(outline_json)
        return client.post("seo", "/api/seo/push-to-drupal", {
            "outline": outline,
            "author": author,
            "category": category,
        })
