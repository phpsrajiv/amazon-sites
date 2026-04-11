import json
import logging
from datetime import date, timedelta
from pathlib import Path
from collections import defaultdict

from src.models.common import Platform
from src.models.engagement import EngagementLogEntry, EngagementMetrics, WeeklyReport

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
ENGAGEMENT_FILE = DATA_DIR / "engagement_log.json"
MIN_DATA_POINTS = 10


class EngagementService:

    def __init__(self):
        self._entries: list[dict] = []
        self._load()

    def _load(self):
        if ENGAGEMENT_FILE.exists():
            try:
                with open(ENGAGEMENT_FILE) as f:
                    self._entries = json.load(f)
            except (json.JSONDecodeError, Exception):
                self._entries = []

    def _save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(ENGAGEMENT_FILE, "w") as f:
            json.dump(self._entries, f, indent=2, default=str)

    def log_engagement(self, entry: EngagementLogEntry):
        self._entries.append(entry.model_dump(mode="json"))
        self._save()

    def _engagement_rate(self, metrics: dict) -> float:
        reach = metrics.get("reach", 0) or metrics.get("impressions", 0)
        if reach == 0:
            return 0.0
        interactions = metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0) + metrics.get("saves", 0)
        return interactions / reach

    def get_avg_engagement(self, platform: Platform, day_of_week: str, hour: int) -> float | None:
        matching = [
            e for e in self._entries
            if e.get("platform") == platform.value
        ]
        # Filter by day and approximate hour
        filtered = []
        for e in matching:
            pub = e.get("published_at", "")
            if not pub:
                continue
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(pub) if isinstance(pub, str) else pub
                day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                if day_names[dt.weekday()] == day_of_week and dt.hour == hour:
                    filtered.append(e)
            except Exception:
                continue

        if len(filtered) < MIN_DATA_POINTS:
            return None

        rates = [self._engagement_rate(e.get("metrics", {})) for e in filtered]
        return sum(rates) / len(rates) if rates else None

    def get_platform_average(self, platform: Platform) -> float | None:
        matching = [
            e for e in self._entries
            if e.get("platform") == platform.value
        ]
        if len(matching) < MIN_DATA_POINTS:
            return None
        rates = [self._engagement_rate(e.get("metrics", {})) for e in matching]
        return sum(rates) / len(rates) if rates else None

    def get_best_times(self, platform: Platform, top_n: int = 5) -> list[dict]:
        matching = [e for e in self._entries if e.get("platform") == platform.value]
        if not matching:
            return []

        slot_rates = defaultdict(list)
        for e in matching:
            pub = e.get("published_at", "")
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(pub) if isinstance(pub, str) else pub
                day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                slot_key = f"{day_names[dt.weekday()]}_{dt.hour}"
                slot_rates[slot_key].append(self._engagement_rate(e.get("metrics", {})))
            except Exception:
                continue

        averages = []
        for slot, rates in slot_rates.items():
            if len(rates) >= 3:
                day, hour = slot.rsplit("_", 1)
                averages.append({
                    "day": day,
                    "hour": int(hour),
                    "avg_engagement_rate": round(sum(rates) / len(rates), 4),
                    "data_points": len(rates),
                })

        averages.sort(key=lambda x: x["avg_engagement_rate"], reverse=True)
        return averages[:top_n]

    def get_weekly_report(self, week_start: date) -> WeeklyReport:
        week_end = week_start + timedelta(days=7)
        prev_start = week_start - timedelta(days=7)

        current_entries = []
        prev_entries = []
        for e in self._entries:
            pub = e.get("published_at", "")
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(pub) if isinstance(pub, str) else pub
                d = dt.date() if hasattr(dt, "date") else dt
                if week_start <= d < week_end:
                    current_entries.append(e)
                elif prev_start <= d < week_start:
                    prev_entries.append(e)
            except Exception:
                continue

        current_rates = [self._engagement_rate(e.get("metrics", {})) for e in current_entries]
        prev_rates = [self._engagement_rate(e.get("metrics", {})) for e in prev_entries]

        avg_current = sum(current_rates) / len(current_rates) if current_rates else 0
        avg_prev = sum(prev_rates) / len(prev_rates) if prev_rates else 0

        if avg_prev > 0:
            change = ((avg_current - avg_prev) / avg_prev) * 100
            vs_prev = f"{'+' if change >= 0 else ''}{change:.1f}% engagement"
        else:
            vs_prev = "No previous data"

        # Platform breakdown
        breakdown = {}
        for e in current_entries:
            p = e.get("platform", "unknown")
            if p not in breakdown:
                breakdown[p] = EngagementMetrics()
            m = e.get("metrics", {})
            breakdown[p] = EngagementMetrics(
                impressions=breakdown[p].impressions + m.get("impressions", 0),
                likes=breakdown[p].likes + m.get("likes", 0),
                comments=breakdown[p].comments + m.get("comments", 0),
                shares=breakdown[p].shares + m.get("shares", 0),
                saves=breakdown[p].saves + m.get("saves", 0),
                reach=breakdown[p].reach + m.get("reach", 0),
            )

        # Best performing post
        best = None
        if current_entries:
            best_entry = max(current_entries, key=lambda e: self._engagement_rate(e.get("metrics", {})))
            best = EngagementLogEntry(**best_entry)

        return WeeklyReport(
            week_start=week_start,
            total_posts=len(current_entries),
            avg_engagement_rate=round(avg_current, 4),
            best_performing_post=best,
            platform_breakdown=breakdown,
            vs_previous_week=vs_prev,
        )
