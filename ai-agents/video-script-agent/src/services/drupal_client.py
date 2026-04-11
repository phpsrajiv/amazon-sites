"""
Drupal JSON:API Client
Pushes generated content to the Drupal 11 backend as blog_post nodes.

NOTE: This file is duplicated from content-writer-agent/src/services/drupal_client.py.
      Included for potential future use (e.g. storing video metadata in Drupal).
"""

from __future__ import annotations

import os

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
                    "status": False,
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
