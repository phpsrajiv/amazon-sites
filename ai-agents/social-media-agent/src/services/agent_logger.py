import json
import logging
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from src.models.common import Platform
from src.models.logging import (
    DecisionType,
    DecisionLogEntry,
    PostLogEntry,
    DecisionLogQuery,
    PostLogQuery,
    LogSummary,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
DECISION_LOG_FILE = DATA_DIR / "decision_log.json"
POST_LOG_FILE = DATA_DIR / "post_log.json"


class AgentLogger:

    def __init__(self):
        self._decisions: list[dict] = []
        self._posts: list[dict] = []
        self._load()

    def _load(self):
        if DECISION_LOG_FILE.exists():
            try:
                with open(DECISION_LOG_FILE) as f:
                    self._decisions = json.load(f)
            except (json.JSONDecodeError, Exception):
                self._decisions = []
        if POST_LOG_FILE.exists():
            try:
                with open(POST_LOG_FILE) as f:
                    self._posts = json.load(f)
            except (json.JSONDecodeError, Exception):
                self._posts = []

    def _save_decisions(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DECISION_LOG_FILE, "w") as f:
            json.dump(self._decisions, f, indent=2, default=str)

    def _save_posts(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(POST_LOG_FILE, "w") as f:
            json.dump(self._posts, f, indent=2, default=str)

    def log_decision(
        self,
        decision_type: DecisionType,
        agent_name: str,
        action: str,
        rationale: str,
        input_summary: dict,
        output_summary: dict,
        platform: Optional[Platform] = None,
        event_context: Optional[str] = None,
        news_context: Optional[str] = None,
    ) -> str:
        decision_id = str(uuid.uuid4())
        entry = DecisionLogEntry(
            id=decision_id,
            timestamp=datetime.now(),
            decision_type=decision_type,
            platform=platform,
            agent_name=agent_name,
            action=action,
            rationale=rationale,
            input_summary=input_summary,
            output_summary=output_summary,
            event_context=event_context,
            news_context=news_context,
        )
        self._decisions.append(entry.model_dump(mode="json"))
        self._save_decisions()
        logger.info(f"[DECISION] {agent_name}: {action} — {rationale}")
        return decision_id

    def log_post(
        self,
        platform: Platform,
        post_type: str,
        content_preview: str,
        timing_score: float,
        timing_rationale: str,
        event_context: Optional[str] = None,
        decision_log_id: Optional[str] = None,
    ) -> str:
        post_id = str(uuid.uuid4())
        if not decision_log_id and self._decisions:
            decision_log_id = self._decisions[-1].get("id", "")

        entry = PostLogEntry(
            id=post_id,
            timestamp=datetime.now(),
            platform=platform,
            post_type=post_type,
            content_preview=content_preview[:200],
            timing_score=timing_score,
            timing_rationale=timing_rationale,
            event_context=event_context,
            decision_log_id=decision_log_id or "",
        )
        self._posts.append(entry.model_dump(mode="json"))
        self._save_posts()
        logger.info(f"[POST] {platform.value}/{post_type}: {content_preview[:80]}...")
        return post_id

    def get_decisions(self, query: DecisionLogQuery) -> list[DecisionLogEntry]:
        results = []
        for d in self._decisions:
            if query.platform and d.get("platform") != query.platform.value:
                continue
            if query.decision_type and d.get("decision_type") != query.decision_type.value:
                continue
            if query.agent_name and d.get("agent_name") != query.agent_name:
                continue
            if query.date_start or query.date_end:
                ts = d.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(ts) if isinstance(ts, str) else ts
                    d_date = dt.date() if hasattr(dt, "date") else dt
                    if query.date_start and d_date < query.date_start:
                        continue
                    if query.date_end and d_date > query.date_end:
                        continue
                except Exception:
                    continue
            results.append(DecisionLogEntry(**d))

        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:query.limit]

    def get_posts(self, query: PostLogQuery) -> list[PostLogEntry]:
        results = []
        for p in self._posts:
            if query.platform and p.get("platform") != query.platform.value:
                continue
            if query.post_type and p.get("post_type") != query.post_type:
                continue
            if query.date_start or query.date_end:
                ts = p.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(ts) if isinstance(ts, str) else ts
                    p_date = dt.date() if hasattr(dt, "date") else dt
                    if query.date_start and p_date < query.date_start:
                        continue
                    if query.date_end and p_date > query.date_end:
                        continue
                except Exception:
                    continue
            results.append(PostLogEntry(**p))

        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:query.limit]

    def get_decision_chain(self, decision_id: str) -> dict:
        decision = None
        for d in self._decisions:
            if d.get("id") == decision_id:
                decision = DecisionLogEntry(**d)
                break

        if not decision:
            return {"error": "Decision not found", "decision_id": decision_id}

        linked_posts = [
            PostLogEntry(**p) for p in self._posts
            if p.get("decision_log_id") == decision_id
        ]

        return {
            "decision": decision.model_dump(mode="json"),
            "linked_posts": [p.model_dump(mode="json") for p in linked_posts],
            "total_linked_posts": len(linked_posts),
        }

    def get_summary(self) -> LogSummary:
        decisions_by_type: dict[str, int] = {}
        for d in self._decisions:
            dt = d.get("decision_type", "unknown")
            decisions_by_type[dt] = decisions_by_type.get(dt, 0) + 1

        posts_by_platform: dict[str, int] = {}
        for p in self._posts:
            plat = p.get("platform", "unknown")
            posts_by_platform[plat] = posts_by_platform.get(plat, 0) + 1

        recent_decisions = sorted(self._decisions, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        recent_posts = sorted(self._posts, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]

        return LogSummary(
            total_decisions=len(self._decisions),
            total_posts=len(self._posts),
            decisions_by_type=decisions_by_type,
            posts_by_platform=posts_by_platform,
            recent_decisions=[DecisionLogEntry(**d) for d in recent_decisions],
            recent_posts=[PostLogEntry(**p) for p in recent_posts],
        )
