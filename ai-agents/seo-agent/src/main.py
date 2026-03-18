"""
SEO Agent API for SellerBuddy
Runs as a standalone Docker service alongside Drupal + React.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.agents.seo_agent import (
    SEOAgent,
    SEOWeeklyRunRequest,
    SEOWeeklyRunResult,
    SEOGenerateOutlineRequest,
    SEOPushToDrupalRequest,
    ContentOutline,
)

load_dotenv()

app = FastAPI(
    title="SellerBuddy — SEO Agent",
    description=(
        "Weekly keyword research via Google Search Console, "
        "blog topic identification, and SEO-optimised outline generation. "
        "Can optionally push drafts to Drupal via JSON:API."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-loaded singleton
_seo_agent: SEOAgent | None = None


def get_seo_agent() -> SEOAgent:
    global _seo_agent
    if _seo_agent is None:
        _seo_agent = SEOAgent()
    return _seo_agent


# ========== Endpoints ==========


@app.post("/api/seo/weekly-run", response_model=SEOWeeklyRunResult)
async def seo_weekly_run(request: SEOWeeklyRunRequest):
    """
    Full weekly SEO pipeline:
      1. Classify keywords from GSC data (or pass gsc_data directly)
      2. Generate 2 blog topics (How-To + Comparison)
      3. Generate SEO-optimised outlines for each topic

    Schedule this endpoint via cron every Monday.
    """
    try:
        agent = get_seo_agent()
        return agent.weekly_run(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seo/generate-outline", response_model=ContentOutline)
async def seo_generate_outline(request: SEOGenerateOutlineRequest):
    """Generate a single SEO-optimised blog outline on demand."""
    try:
        agent = get_seo_agent()
        return agent.generate_outline(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seo/push-to-drupal")
async def seo_push_to_drupal(request: SEOPushToDrupalRequest):
    """
    Push a generated outline to Drupal as a Draft blog_post node.
    Requires DRUPAL_BASE_URL, DRUPAL_USERNAME, DRUPAL_PASSWORD env vars.
    """
    try:
        from src.services.drupal_client import DrupalClient

        client = DrupalClient()
        outline = request.outline

        # Build a structured HTML body from the outline sections
        body_parts = [f"<h1>{outline.title}</h1>"]
        for section in outline.sections:
            body_parts.append(f"<h2>{section.heading}</h2>")
            body_parts.append(f"<p><em>[{section.word_count} words] {section.notes}</em></p>")
        body_parts.append(f'<div class="cta-block"><p><strong>{outline.cta}</strong></p></div>')

        if outline.faq_questions:
            body_parts.append("<h2>Frequently Asked Questions</h2>")
            for q in outline.faq_questions:
                body_parts.append(f"<h3>{q}</h3>")
                body_parts.append("<p><em>[Answer to be written]</em></p>")

        body_html = "\n".join(body_parts)

        result = client.create_blog_draft(
            title=f"[DRAFT] {outline.title}",
            body_html=body_html,
            summary=outline.meta_description,
            author=request.author,
            category=request.category,
        )
        return {
            "status": "created",
            "drupal_id": result.get("data", {}).get("id"),
            "message": f"Draft blog post '{outline.title}' created in Drupal.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "seo-agent",
        "gsc_configured": os.path.isfile(
            os.getenv("GSC_SERVICE_ACCOUNT_JSON", "/app/credentials/sellerbuddy-gsc.json")
        ),
        "drupal_configured": bool(os.getenv("DRUPAL_BASE_URL")),
    }
