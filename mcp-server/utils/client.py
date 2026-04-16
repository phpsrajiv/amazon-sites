"""
Shared httpx client for SellerBuddy AI Agents.

Base URLs are resolved from environment variables so the MCP server can
target either a local Docker stack or a remote server without code changes.

Environment variables (all optional, localhost defaults used if absent):
  SELLERBUDDY_SEO_URL             e.g. https://seo.api.sellerbuddy.app
  SELLERBUDDY_CONTENT_URL         e.g. https://content.api.sellerbuddy.app
  SELLERBUDDY_VIDEO_SCRIPT_URL    e.g. https://video-script.api.sellerbuddy.app
  SELLERBUDDY_VIDEO_GENERATOR_URL e.g. https://video-generator.api.sellerbuddy.app
  SELLERBUDDY_SOCIAL_URL          e.g. https://social.api.sellerbuddy.app

  Or set a single base for all agents:
  SELLERBUDDY_REMOTE_BASE         e.g. https://api.sellerbuddy.app
  (individual env vars take precedence over SELLERBUDDY_REMOTE_BASE)
"""

from __future__ import annotations

import os

import httpx
from typing import Any


def _resolve_urls() -> dict[str, str]:
    remote_base = os.getenv("SELLERBUDDY_REMOTE_BASE", "").rstrip("/")

    defaults = {
        "seo":             f"{remote_base}/seo"             if remote_base else "http://localhost:8001",
        "content":         f"{remote_base}/content"         if remote_base else "http://localhost:8002",
        "video_script":    f"{remote_base}/video-script"    if remote_base else "http://localhost:8003",
        "video_generator": f"{remote_base}/video-generator" if remote_base else "http://localhost:8004",
        "social":          f"{remote_base}/social"          if remote_base else "http://localhost:8005",
    }

    return {
        "seo":             os.getenv("SELLERBUDDY_SEO_URL",             defaults["seo"]).rstrip("/"),
        "content":         os.getenv("SELLERBUDDY_CONTENT_URL",         defaults["content"]).rstrip("/"),
        "video_script":    os.getenv("SELLERBUDDY_VIDEO_SCRIPT_URL",    defaults["video_script"]).rstrip("/"),
        "video_generator": os.getenv("SELLERBUDDY_VIDEO_GENERATOR_URL", defaults["video_generator"]).rstrip("/"),
        "social":          os.getenv("SELLERBUDDY_SOCIAL_URL",          defaults["social"]).rstrip("/"),
    }


BASE_URLS: dict[str, str] = _resolve_urls()

# Long timeout — LLM-backed agents can take 30-90 s per call
_TIMEOUT = httpx.Timeout(connect=10.0, read=180.0, write=30.0, pool=5.0)


def get(agent: str, path: str, **kwargs: Any) -> Any:
    url = f"{BASE_URLS[agent]}{path}"
    with httpx.Client(timeout=_TIMEOUT) as client:
        r = client.get(url, **kwargs)
        r.raise_for_status()
        return r.json()


def post(agent: str, path: str, body: dict | None = None, **kwargs: Any) -> Any:
    url = f"{BASE_URLS[agent]}{path}"
    with httpx.Client(timeout=_TIMEOUT) as client:
        r = client.post(url, json=body, **kwargs)
        r.raise_for_status()
        return r.json()


def agent_url(agent: str) -> str:
    return BASE_URLS[agent]
