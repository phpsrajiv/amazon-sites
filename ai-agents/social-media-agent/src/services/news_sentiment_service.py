import os
import json
import logging
import re

import requests
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.models.common import PostingUrgency

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


class NewsSentimentService:

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY", "")
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=0.0,
        )
        self._cached_headlines: list[str] = []
        self._cached_advisory: dict | None = None

    def check_news_sentiment(self) -> list[str]:
        if not self.api_key:
            logger.warning("NEWS_API_KEY not set — skipping news sentiment check")
            return []

        try:
            resp = requests.get(
                "https://newsapi.org/v2/top-headlines",
                params={"country": "in", "pageSize": 20, "apiKey": self.api_key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            headlines = [
                a.get("title", "") for a in data.get("articles", []) if a.get("title")
            ]
            self._cached_headlines = headlines
            return headlines
        except Exception as e:
            logger.error(f"NewsAPI fetch failed: {e}")
            return []

    def is_crisis_active(self, headlines: list[str] | None = None) -> dict:
        if headlines is None:
            headlines = self._cached_headlines or self.check_news_sentiment()

        if not headlines:
            return {"crisis": False, "reason": "No headlines available", "urgency": PostingUrgency.NORMAL}

        headlines_text = "\n".join(f"- {h}" for h in headlines[:15])

        messages = [
            SystemMessage(content=(
                "You are a crisis detection system for a social media scheduling tool. "
                "Analyze news headlines and determine if there is an active crisis that "
                "would make social media marketing posts inappropriate.\n\n"
                "Crisis criteria:\n"
                "- Active war or military conflict involving India\n"
                "- Major natural disaster (earthquake, flood, cyclone) with significant casualties\n"
                "- National mourning (death of major leader)\n"
                "- Major political crisis affecting daily life\n"
                "- Terrorist attack\n\n"
                "Respond in JSON:\n"
                '{"crisis": true/false, "severity": "high/medium/low/none", '
                '"reason": "brief explanation", '
                '"urgency": "pause/reduce/normal"}'
            )),
            HumanMessage(content=f"Today's top India headlines:\n{headlines_text}"),
        ]

        try:
            response = self.llm.invoke(messages)
            parsed = json.loads(_strip_fences(response.content))
            urgency_map = {
                "pause": PostingUrgency.PAUSE,
                "reduce": PostingUrgency.REDUCE,
                "normal": PostingUrgency.NORMAL,
            }
            return {
                "crisis": parsed.get("crisis", False),
                "severity": parsed.get("severity", "none"),
                "reason": parsed.get("reason", ""),
                "urgency": urgency_map.get(parsed.get("urgency", "normal"), PostingUrgency.NORMAL),
                "headlines_checked": len(headlines),
            }
        except Exception as e:
            logger.error(f"Crisis detection LLM failed: {e}")
            return {"crisis": False, "reason": f"LLM error: {e}", "urgency": PostingUrgency.NORMAL}

    def get_posting_advisory(self) -> dict:
        headlines = self.check_news_sentiment()
        crisis_result = self.is_crisis_active(headlines)

        advisory = {
            "urgency": crisis_result["urgency"].value if isinstance(crisis_result["urgency"], PostingUrgency) else crisis_result["urgency"],
            "crisis_active": crisis_result.get("crisis", False),
            "reason": crisis_result.get("reason", ""),
            "headlines_checked": len(headlines),
            "top_headlines": headlines[:5],
        }
        self._cached_advisory = advisory
        return advisory

    def get_cached_advisory(self) -> dict | None:
        return self._cached_advisory
