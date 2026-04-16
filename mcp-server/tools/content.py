"""
Content Writer Agent tools — wraps http://localhost:8002
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from utils import client

_NICHE = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def content_health() -> dict:
        """Check whether the Content Writer Agent service is running."""
        return client.get("content", "/health")

    @mcp.tool()
    def content_write_blog(
        outline_json: str,
        brand: str = "SellerBuddy",
        niche: str = _NICHE,
        push_to_drupal: bool = False,
        author: str = "SellerBuddy",
        category: str = "SEO",
    ) -> dict:
        """
        Generate a full blog post (1,800–2,500 words) from a ContentOutline.

        Returns title, meta_description, body_html, word_count, and optionally
        a Drupal draft ID if push_to_drupal is True.

        Args:
            outline_json: JSON string of a ContentOutline (from seo_generate_outline
                          or seo_weekly_run)
            brand: Brand name woven into the post voice and CTA
            niche: Product/market niche for contextual accuracy
            push_to_drupal: If True, immediately publish as a Drupal draft
            author: Drupal author (only used when push_to_drupal=True)
            category: Drupal taxonomy category (only used when push_to_drupal=True)
        """
        outline = json.loads(outline_json)
        return client.post("content", "/api/content/write-blog", {
            "outline": outline,
            "brand": brand,
            "niche": niche,
            "push_to_drupal": push_to_drupal,
            "author": author,
            "category": category,
        })

    @mcp.tool()
    def content_linkedin_carousel(
        brand: str = "SellerBuddy",
        outline_json: str | None = None,
        blog_html: str | None = None,
        blog_title: str | None = None,
    ) -> dict:
        """
        Generate LinkedIn carousel copy (8–12 slides) from an outline or blog post.

        Provide either outline_json (from seo_generate_outline) OR blog_html
        (from content_write_blog). Providing blog_html yields richer slides
        because the full post text is available.

        Args:
            brand: Brand name for slide voice/CTA
            outline_json: JSON string of a ContentOutline (optional)
            blog_html: Full blog HTML string (optional, preferred over outline)
            blog_title: Blog title — required when blog_html is provided
        """
        body: dict = {"brand": brand}
        if outline_json:
            body["outline"] = json.loads(outline_json)
        if blog_html:
            body["blog_html"] = blog_html
        if blog_title:
            body["blog_title"] = blog_title
        return client.post("content", "/api/content/linkedin-carousel", body)

    @mcp.tool()
    def content_tweet_thread(
        brand: str = "SellerBuddy",
        outline_json: str | None = None,
        blog_html: str | None = None,
        blog_title: str | None = None,
    ) -> dict:
        """
        Generate a tweet thread (5–8 tweets) from an outline or blog post.

        Provide either outline_json OR blog_html. Using blog_html produces more
        specific, data-rich tweets.

        Args:
            brand: Brand name for tweet voice
            outline_json: JSON string of a ContentOutline (optional)
            blog_html: Full blog HTML string (optional, preferred over outline)
            blog_title: Blog title — required when blog_html is provided
        """
        body: dict = {"brand": brand}
        if outline_json:
            body["outline"] = json.loads(outline_json)
        if blog_html:
            body["blog_html"] = blog_html
        if blog_title:
            body["blog_title"] = blog_title
        return client.post("content", "/api/content/tweet-thread", body)

    @mcp.tool()
    def content_full_pipeline(
        outline_json: str,
        brand: str = "SellerBuddy",
        niche: str = _NICHE,
        push_to_drupal: bool = False,
        author: str = "SellerBuddy",
        category: str = "SEO",
    ) -> dict:
        """
        Run the full content pipeline from a single outline in one call:
          1. Full blog post (1,800–2,500 words)
          2. LinkedIn carousel (8–12 slides, using the blog for richer context)
          3. Tweet thread (5–8 tweets, using the blog for richer context)

        Args:
            outline_json: JSON string of a ContentOutline
            brand: Brand name used across all generated content
            niche: Product/market niche for contextual accuracy
            push_to_drupal: If True, push the blog post as a Drupal draft
            author: Drupal author (only used when push_to_drupal=True)
            category: Drupal taxonomy category (only used when push_to_drupal=True)
        """
        outline = json.loads(outline_json)
        return client.post("content", "/api/content/full-pipeline", {
            "outline": outline,
            "brand": brand,
            "niche": niche,
            "push_to_drupal": push_to_drupal,
            "author": author,
            "category": category,
        })
