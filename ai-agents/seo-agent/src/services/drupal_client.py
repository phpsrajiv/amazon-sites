"""
Drupal JSON:API Client
Pushes generated blog outlines / drafts to the Drupal 11 backend as blog_post nodes.

Uses the Drupal JSON:API endpoint: POST /jsonapi/node/blog_post
Requires an OAuth2 bearer token (Simple OAuth module) or Basic auth for content_editor role.

Environment variables:
  DRUPAL_BASE_URL  — e.g. http://drupal:80  (Docker service name) or http://localhost:8080
  DRUPAL_USERNAME  — content_editor username
  DRUPAL_PASSWORD  — content_editor password
"""

from __future__ import annotations

import os
from typing import Any

import requests


class DrupalClient:
    """Push content to Drupal 11 via JSON:API."""

    def __init__(self) -> None:
        self.base_url = os.getenv("DRUPAL_BASE_URL", "http://drupal:80").rstrip("/")
        self.username = os.getenv("DRUPAL_USERNAME", "")
        self.password = os.getenv("DRUPAL_PASSWORD", "")

    def _auth(self) -> tuple[str, str] | None:
        if self.username and self.password:
            return (self.username, self.password)
        return None

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }

    def create_blog_draft(
        self,
        title: str,
        body_html: str,
        summary: str,
        author: str = "SellerBuddy",
        category: str = "SEO",
        image_url: str = "",
    ) -> dict:
        """
        Create a blog_post node in Drupal as a Draft.

        Returns the JSON:API response dict (includes the new node ID).
        """
        payload = {
            "data": {
                "type": "node--blog_post",
                "attributes": {
                    "title": title,
                    "field_blog_body": {
                        "value": body_html,
                        "format": "full_html",
                    },
                    "field_blog_summary": summary,
                    "field_blog_author": author,
                    "field_blog_category": category,
                    "field_blog_image": image_url,
                    "status": False,  # Draft — not published
                },
            }
        }

        resp = requests.post(
            f"{self.base_url}/jsonapi/node/blog_post",
            json=payload,
            headers=self._headers(),
            auth=self._auth(),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def list_blog_posts(self, limit: int = 20) -> list[dict]:
        """Fetch existing blog posts — useful for internal link suggestions."""
        resp = requests.get(
            f"{self.base_url}/jsonapi/node/blog_post",
            params={
                "sort": "-field_blog_weight",
                "page[limit]": limit,
            },
            headers={"Accept": "application/vnd.api+json"},
            auth=self._auth(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [
            {
                "id": node["id"],
                "title": node["attributes"]["title"],
                "category": node["attributes"].get("field_blog_category", ""),
            }
            for node in data
        ]
