"""
Content Writer Agent API for SellerBuddy
=========================================
Takes SEO outlines and produces full blog posts, LinkedIn carousel copy,
and tweet threads. Runs as a standalone Docker service alongside the
SEO Agent and Drupal backend.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models.outline import ContentOutline
from src.models.blog import BlogWriteRequest, BlogWriteResponse
from src.models.linkedin import LinkedInRequest, LinkedInResponse
from src.models.twitter import TweetThreadRequest, TweetThreadResponse

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SellerBuddy — Content Writer Agent",
    description=(
        "Takes SEO-optimised outlines and produces full blog posts "
        "(1,800-2,500 words), LinkedIn carousel copy, and tweet threads. "
        "Can optionally push blog posts to Drupal as drafts via JSON:API."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Lazy-loaded singletons
# ---------------------------------------------------------------------------

_blog_writer = None
_linkedin_gen = None
_twitter_gen = None


def get_blog_writer():
    global _blog_writer
    if _blog_writer is None:
        from src.agents.blog_writer import BlogWriter
        _blog_writer = BlogWriter()
    return _blog_writer


def get_linkedin_gen():
    global _linkedin_gen
    if _linkedin_gen is None:
        from src.agents.linkedin_generator import LinkedInGenerator
        _linkedin_gen = LinkedInGenerator()
    return _linkedin_gen


def get_twitter_gen():
    global _twitter_gen
    if _twitter_gen is None:
        from src.agents.twitter_generator import TwitterGenerator
        _twitter_gen = TwitterGenerator()
    return _twitter_gen


# ---------------------------------------------------------------------------
# Full pipeline request / response
# ---------------------------------------------------------------------------

class FullPipelineRequest(BaseModel):
    outline: ContentOutline
    push_to_drupal: bool = False
    author: str = "SellerBuddy"
    category: str = "SEO"
    brand: str = "SellerBuddy"
    niche: str = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"


class FullPipelineResponse(BaseModel):
    blog: BlogWriteResponse
    linkedin: LinkedInResponse
    twitter: TweetThreadResponse


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/content/write-blog", response_model=BlogWriteResponse)
async def write_blog(request: BlogWriteRequest):
    """
    Generate a full blog post (1,800-2,500 words) from an SEO outline.
    Optionally push to Drupal as a draft.
    """
    try:
        writer = get_blog_writer()
        body_html, word_count = writer.write_blog(
            outline=request.outline,
            brand=request.brand,
            niche=request.niche,
        )

        drupal_id = None
        drupal_status = None

        if request.push_to_drupal:
            from src.services.drupal_client import DrupalClient
            client = DrupalClient()
            result = client.create_blog_draft(
                title=request.outline.title,
                body_html=body_html,
                summary=request.outline.meta_description,
                author=request.author,
                category=request.category,
            )
            drupal_id = result.get("data", {}).get("id")
            drupal_status = "draft_created"

        return BlogWriteResponse(
            title=request.outline.title,
            meta_description=request.outline.meta_description,
            body_html=body_html,
            word_count=word_count,
            drupal_id=drupal_id,
            drupal_status=drupal_status,
        )
    except Exception as e:
        logger.exception("Error writing blog")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/linkedin-carousel", response_model=LinkedInResponse)
async def linkedin_carousel(request: LinkedInRequest):
    """Generate LinkedIn carousel copy (8-12 slides) from an outline or blog."""
    try:
        if not request.outline and not request.blog_html:
            raise HTTPException(
                status_code=400,
                detail="Either 'outline' or 'blog_html' must be provided.",
            )

        gen = get_linkedin_gen()
        slides = gen.generate_carousel(
            brand=request.brand,
            outline=request.outline,
            blog_html=request.blog_html,
            blog_title=request.blog_title,
        )

        title = (
            request.outline.title
            if request.outline
            else request.blog_title or "LinkedIn Carousel"
        )

        return LinkedInResponse(
            title=title,
            slides=slides,
            total_slides=len(slides),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating LinkedIn carousel")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/tweet-thread", response_model=TweetThreadResponse)
async def tweet_thread(request: TweetThreadRequest):
    """Generate a tweet thread (5-8 tweets) from an outline or blog."""
    try:
        if not request.outline and not request.blog_html:
            raise HTTPException(
                status_code=400,
                detail="Either 'outline' or 'blog_html' must be provided.",
            )

        gen = get_twitter_gen()
        tweets = gen.generate_thread(
            brand=request.brand,
            outline=request.outline,
            blog_html=request.blog_html,
            blog_title=request.blog_title,
        )

        title = (
            request.outline.title
            if request.outline
            else request.blog_title or "Tweet Thread"
        )

        return TweetThreadResponse(
            title=title,
            tweets=tweets,
            total_tweets=len(tweets),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating tweet thread")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/content/full-pipeline", response_model=FullPipelineResponse)
async def full_pipeline(request: FullPipelineRequest):
    """
    Generate all content from a single outline:
      1. Full blog post (1,800-2,500 words)
      2. LinkedIn carousel (8-12 slides)
      3. Tweet thread (5-8 tweets)

    The blog is generated first so LinkedIn and Twitter generators can
    use the full blog content for richer context.
    """
    try:
        # Step 1: write the blog
        writer = get_blog_writer()
        body_html, word_count = writer.write_blog(
            outline=request.outline,
            brand=request.brand,
            niche=request.niche,
        )

        drupal_id = None
        drupal_status = None

        if request.push_to_drupal:
            from src.services.drupal_client import DrupalClient
            client = DrupalClient()
            result = client.create_blog_draft(
                title=request.outline.title,
                body_html=body_html,
                summary=request.outline.meta_description,
                author=request.author,
                category=request.category,
            )
            drupal_id = result.get("data", {}).get("id")
            drupal_status = "draft_created"

        blog_response = BlogWriteResponse(
            title=request.outline.title,
            meta_description=request.outline.meta_description,
            body_html=body_html,
            word_count=word_count,
            drupal_id=drupal_id,
            drupal_status=drupal_status,
        )

        # Step 2: LinkedIn carousel (using blog HTML for richer context)
        linkedin_gen = get_linkedin_gen()
        slides = linkedin_gen.generate_carousel(
            brand=request.brand,
            outline=request.outline,
            blog_html=body_html,
            blog_title=request.outline.title,
        )
        linkedin_response = LinkedInResponse(
            title=request.outline.title,
            slides=slides,
            total_slides=len(slides),
        )

        # Step 3: tweet thread (using blog HTML for richer context)
        twitter_gen = get_twitter_gen()
        tweets = twitter_gen.generate_thread(
            brand=request.brand,
            outline=request.outline,
            blog_html=body_html,
            blog_title=request.outline.title,
        )
        twitter_response = TweetThreadResponse(
            title=request.outline.title,
            tweets=tweets,
            total_tweets=len(tweets),
        )

        return FullPipelineResponse(
            blog=blog_response,
            linkedin=linkedin_response,
            twitter=twitter_response,
        )
    except Exception as e:
        logger.exception("Error in full pipeline")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "content-writer-agent",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "drupal_configured": bool(os.getenv("DRUPAL_BASE_URL")),
    }
