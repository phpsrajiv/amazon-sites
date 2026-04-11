"""
Video Script Agent API for SellerBuddy
=======================================
Takes top-performing blog posts or SEO outlines and generates YouTube video
scripts (with timestamps, on-screen text cues, B-roll suggestions) and
YouTube Shorts hooks.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models.outline import ContentOutline
from src.models.youtube_script import YouTubeScriptRequest, YouTubeScriptResponse
from src.models.shorts_hook import ShortsHookRequest, ShortsHookResponse

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SellerBuddy — Video Script Agent",
    description=(
        "Takes blog posts or SEO outlines and generates YouTube video scripts "
        "with timestamps, on-screen text cues, and B-roll suggestions, plus "
        "YouTube Shorts hooks."
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

_script_writer = None
_shorts_gen = None


def get_script_writer():
    global _script_writer
    if _script_writer is None:
        from src.agents.youtube_script_writer import YouTubeScriptWriter
        _script_writer = YouTubeScriptWriter()
    return _script_writer


def get_shorts_gen():
    global _shorts_gen
    if _shorts_gen is None:
        from src.agents.shorts_hook_generator import ShortsHookGenerator
        _shorts_gen = ShortsHookGenerator()
    return _shorts_gen


# ---------------------------------------------------------------------------
# Full pipeline request / response
# ---------------------------------------------------------------------------

class FullPipelineRequest(BaseModel):
    outline: ContentOutline | None = None
    blog_html: str | None = None
    blog_title: str | None = None
    brand: str = "SellerBuddy"
    niche: str = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies"
    target_duration_minutes: int = 8
    num_shorts_hooks: int = 3


class FullPipelineResponse(BaseModel):
    youtube_script: YouTubeScriptResponse
    shorts_hooks: ShortsHookResponse


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/video/youtube-script", response_model=YouTubeScriptResponse)
async def youtube_script(request: YouTubeScriptRequest):
    """
    Generate a full YouTube video script with timestamps, narration,
    on-screen text cues, and B-roll suggestions.
    """
    try:
        if not request.outline and not request.blog_html:
            raise HTTPException(
                status_code=400,
                detail="Either 'outline' or 'blog_html' must be provided.",
            )

        writer = get_script_writer()
        result = writer.generate_script(
            brand=request.brand,
            niche=request.niche,
            target_duration_minutes=request.target_duration_minutes,
            outline=request.outline,
            blog_html=request.blog_html,
            blog_title=request.blog_title,
        )

        return YouTubeScriptResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating YouTube script")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/shorts-hooks", response_model=ShortsHookResponse)
async def shorts_hooks(request: ShortsHookRequest):
    """Generate YouTube Shorts hook scripts (60-second punchy scripts)."""
    try:
        if not request.outline and not request.blog_html:
            raise HTTPException(
                status_code=400,
                detail="Either 'outline' or 'blog_html' must be provided.",
            )

        gen = get_shorts_gen()
        hooks = gen.generate_hooks(
            brand=request.brand,
            num_hooks=request.num_hooks,
            outline=request.outline,
            blog_html=request.blog_html,
            blog_title=request.blog_title,
        )

        title = (
            request.outline.title
            if request.outline
            else request.blog_title or "YouTube Shorts"
        )

        return ShortsHookResponse(
            blog_title=title,
            hooks=hooks,
            total_hooks=len(hooks),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating Shorts hooks")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/full-pipeline", response_model=FullPipelineResponse)
async def full_pipeline(request: FullPipelineRequest):
    """
    Generate both a YouTube video script and Shorts hooks from a single input.
    """
    try:
        if not request.outline and not request.blog_html:
            raise HTTPException(
                status_code=400,
                detail="Either 'outline' or 'blog_html' must be provided.",
            )

        # Step 1: YouTube script
        writer = get_script_writer()
        script_result = writer.generate_script(
            brand=request.brand,
            niche=request.niche,
            target_duration_minutes=request.target_duration_minutes,
            outline=request.outline,
            blog_html=request.blog_html,
            blog_title=request.blog_title,
        )
        script_response = YouTubeScriptResponse(**script_result)

        # Step 2: Shorts hooks
        gen = get_shorts_gen()
        hooks = gen.generate_hooks(
            brand=request.brand,
            num_hooks=request.num_shorts_hooks,
            outline=request.outline,
            blog_html=request.blog_html,
            blog_title=request.blog_title,
        )

        title = (
            request.outline.title
            if request.outline
            else request.blog_title or "YouTube Shorts"
        )

        shorts_response = ShortsHookResponse(
            blog_title=title,
            hooks=hooks,
            total_hooks=len(hooks),
        )

        return FullPipelineResponse(
            youtube_script=script_response,
            shorts_hooks=shorts_response,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in video full pipeline")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "video-script-agent",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "drupal_configured": bool(os.getenv("DRUPAL_BASE_URL")),
    }
