"""
Google Search Console Service
Fetches search analytics data for keyword research and opportunity identification.

Authentication:
  - Service account: set GSC_SERVICE_ACCOUNT_JSON env var to the path of the
    service account JSON key file. Default in Docker: /app/credentials/sellerbuddy-gsc.json
  - OAuth2: set GSC_CREDENTIALS_JSON env var to an OAuth2 client secrets file.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
_TOKEN_PATH = os.path.expanduser("~/.config/gsc_token.json")


class GSCService:
    """Thin wrapper around the Search Console API."""

    def __init__(self) -> None:
        self._service = self._build_service()

    def _build_service(self):
        creds = self._get_credentials()
        return build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    def _get_credentials(self) -> Any:
        # 1. Service-account key (preferred — default path for Docker mount)
        sa_path = os.getenv(
            "GSC_SERVICE_ACCOUNT_JSON",
            "/app/credentials/sellerbuddy-gsc.json",
        )
        if sa_path and os.path.isfile(sa_path):
            return service_account.Credentials.from_service_account_file(
                sa_path, scopes=SCOPES
            )

        # 2. Saved OAuth2 token
        creds: Credentials | None = None
        if os.path.isfile(_TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(_TOKEN_PATH, SCOPES)

        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self._save_token(creds)
            return creds

        # 3. Interactive OAuth2 flow (first-time setup)
        oauth_path = os.getenv("GSC_CREDENTIALS_JSON")
        if not oauth_path or not os.path.isfile(oauth_path):
            raise EnvironmentError(
                "Google Search Console credentials not configured. "
                "Set GSC_SERVICE_ACCOUNT_JSON or mount credentials/sellerbuddy-gsc.json."
            )
        flow = InstalledAppFlow.from_client_secrets_file(oauth_path, SCOPES)
        creds = flow.run_local_server(port=0)
        self._save_token(creds)
        return creds

    @staticmethod
    def _save_token(creds: Credentials) -> None:
        os.makedirs(os.path.dirname(_TOKEN_PATH), exist_ok=True)
        with open(_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    def fetch_search_analytics(
        self,
        site_url: str,
        start_date: str | None = None,
        end_date: str | None = None,
        dimensions: list[str] | None = None,
        row_limit: int = 1000,
    ) -> list[dict]:
        """
        Fetch search analytics rows from GSC.

        Returns list of dicts with keys matching the requested dimensions
        plus "clicks", "impressions", "ctr", "position".
        """
        today = date.today()
        if end_date is None:
            end_date = (today - timedelta(days=1)).isoformat()
        if start_date is None:
            start_date = (today - timedelta(days=7)).isoformat()
        if dimensions is None:
            dimensions = ["query"]

        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "dataState": "final",
        }

        response = (
            self._service.searchanalytics()
            .query(siteUrl=site_url, body=body)
            .execute()
        )

        rows = response.get("rows", [])
        results = []
        for row in rows:
            entry: dict = {}
            for i, dim in enumerate(dimensions):
                entry[dim] = row["keys"][i]
            entry["clicks"] = row.get("clicks", 0)
            entry["impressions"] = row.get("impressions", 0)
            entry["ctr"] = round(row.get("ctr", 0.0), 4)
            entry["position"] = round(row.get("position", 0.0), 1)
            results.append(entry)
        return results

    def get_keyword_opportunities(
        self,
        site_url: str,
        start_date: str | None = None,
        end_date: str | None = None,
        min_impressions: int = 100,
        max_position: float = 30.0,
    ) -> list[dict]:
        """
        Return queries that are surfacing in search but not yet well-ranked.
        Filters: impressions >= min_impressions, position between 4.0 and max_position.
        """
        rows = self.fetch_search_analytics(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=["query", "page"],
            row_limit=5000,
        )

        opportunities = [
            r for r in rows
            if r["impressions"] >= min_impressions
            and 4.0 <= r["position"] <= max_position
        ]
        opportunities.sort(key=lambda r: r["impressions"], reverse=True)
        return opportunities

    def get_top_performing_pages(
        self,
        site_url: str,
        start_date: str | None = None,
        end_date: str | None = None,
        top_n: int = 20,
    ) -> list[dict]:
        """Return the top N pages by click volume — useful for internal linking."""
        rows = self.fetch_search_analytics(
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
            dimensions=["page"],
            row_limit=500,
        )
        rows.sort(key=lambda r: r["clicks"], reverse=True)
        return rows[:top_n]
