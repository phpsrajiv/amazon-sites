"""
HTTP client for the SEO Agent (port 8001).

Calls POST /api/seo/weekly-run to fetch keyword opportunities and blog topics.
Gracefully returns None if the SEO agent is unreachable.
"""

import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class SEOClient:

    def __init__(self):
        self.base_url = os.getenv("SEO_AGENT_URL", "http://seo-agent:8001").rstrip("/")

    def fetch_weekly_run(
        self,
        site_url: str = "https://sellerbuddy.in",
        brand: str = "SellerBuddy",
        niche: str = "AI-powered Amazon advertising automation SaaS for sellers, brands, and agencies",
    ) -> Optional[dict]:
        """
        Call the SEO Agent's weekly-run endpoint.

        Returns the full response dict containing:
          - keyword_opportunities: list of {keyword, category, impressions, clicks, position, opportunity}
          - blog_topics: list of {title, post_type, target_keyword, secondary_keywords}
          - outlines: list of content outlines

        Returns None if the SEO agent is unreachable or returns an error.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/api/seo/weekly-run",
                json={
                    "site_url": site_url,
                    "gsc_data": [],
                    "brand": brand,
                    "niche": niche,
                },
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.ConnectionError:
            logger.warning("SEO Agent is unreachable at %s — proceeding without SEO topics", self.base_url)
            return None
        except requests.Timeout:
            logger.warning("SEO Agent timed out at %s — proceeding without SEO topics", self.base_url)
            return None
        except Exception as e:
            logger.warning("SEO Agent call failed: %s — proceeding without SEO topics", e)
            return None
