import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from src.models.common import Platform, PostingUrgency
from src.models.timing import (
    TimingRecommendation,
    TimingRequest,
    TimingResponse,
    ShouldPostResponse,
)
from src.models.logging import DecisionType
from src.services.events_calendar_service import EventsCalendarService
from src.services.news_sentiment_service import NewsSentimentService

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class TimingEngine:

    def __init__(self, calendar_service, news_service, engagement_service=None, agent_logger=None):
        self.calendar = calendar_service
        self.news = news_service
        self.engagement = engagement_service
        self.agent_logger = agent_logger
        self._platform_timing = self._load_platform_timing()

    def _load_platform_timing(self) -> dict:
        timing_file = DATA_DIR / "platform_timing.json"
        if timing_file.exists():
            with open(timing_file) as f:
                return json.load(f)
        return {}

    def _get_platform_multiplier(self, platform: Platform, day_name: str, hour: int) -> tuple[float, str]:
        config = self._platform_timing.get(platform.value, {})

        # Check avoid windows first
        for window in config.get("avoid_windows", []):
            if day_name in window["days"] and window["start_hour"] <= hour < window["end_hour"]:
                return window["multiplier"], f"Avoid: {window['label']}"

        # Check peak windows
        for window in config.get("peak_windows", []):
            if day_name in window["days"] and window["start_hour"] <= hour < window["end_hour"]:
                return window["multiplier"], f"Peak: {window['label']}"

        return config.get("default_multiplier", 0.5), "Off-peak"

    def _score_slot(self, platform: Platform, target_date: date, hour: int) -> tuple[float, str]:
        day_name = DAY_NAMES[target_date.weekday()]
        reasons = []
        score = 0.0

        # Step 1: Platform engagement baseline
        multiplier, window_label = self._get_platform_multiplier(platform, day_name, hour)
        score += multiplier
        reasons.append(f"Platform baseline: {multiplier:.1f} ({window_label})")

        # Step 2: Calendar event boost
        active_events = self.calendar.get_active_events(target_date)
        for event in active_events:
            if platform in event.platforms:
                boost = event.relevance_score * 0.5
                score += boost
                reasons.append(f"Active event '{event.name}': +{boost:.2f}")
                if event.posting_urgency == PostingUrgency.BOOST:
                    score += 0.3
                    reasons.append(f"Boost urgency for '{event.name}': +0.3")

        # Step 3: Pre-event ramp-up
        upcoming = self.calendar.get_events_for_platform(platform, target_date)
        for event in upcoming:
            if event not in active_events and event.date_start > target_date:
                days_until = (event.date_start - target_date).days
                if days_until <= event.pre_event_days and event.pre_event_days > 0:
                    ramp = event.relevance_score * 0.2 * (1 - days_until / event.pre_event_days)
                    score += ramp
                    reasons.append(f"Pre-event '{event.name}' in {days_until}d: +{ramp:.2f}")

        # Step 4: News sentiment
        advisory = self.news.get_cached_advisory()
        if advisory:
            if advisory.get("crisis_active"):
                score = -1.0
                reasons = [f"CRISIS BLOCKED: {advisory.get('reason', 'Active crisis')}"]
            elif advisory.get("urgency") == "reduce":
                score *= 0.5
                reasons.append(f"News negative sentiment: score halved ({advisory.get('reason', '')})")

        # Step 5: Historical engagement adjustment
        if self.engagement:
            try:
                avg_eng = self.engagement.get_avg_engagement(platform, day_name, hour)
                platform_avg = self.engagement.get_platform_average(platform)
                if avg_eng is not None and platform_avg is not None and platform_avg > 0:
                    if avg_eng > platform_avg * 1.2:
                        score += 0.3
                        reasons.append(f"Historical engagement above avg: +0.3")
                    elif avg_eng < platform_avg * 0.5:
                        score -= 0.2
                        reasons.append(f"Historical engagement below avg: -0.2")
            except Exception:
                pass

        rationale = " | ".join(reasons)
        return score, rationale

    def recommend_timing(self, req: TimingRequest) -> TimingResponse:
        # Refresh news sentiment
        self.news.get_posting_advisory()

        recommendations = []
        current = req.date_start
        while current <= req.date_end:
            for platform in req.platforms:
                # Score candidate hours
                candidates = []
                for hour in range(7, 22):
                    score, rationale = self._score_slot(platform, current, hour)
                    candidates.append((hour, score, rationale))

                # Pick top N slots per platform
                candidates.sort(key=lambda x: x[1], reverse=True)
                for hour, score, rationale in candidates[:req.slots_per_platform]:
                    if score < 0:
                        urgency = PostingUrgency.PAUSE
                    elif score >= 1.5:
                        urgency = PostingUrgency.BOOST
                    elif score >= 0.8:
                        urgency = PostingUrgency.NORMAL
                    else:
                        urgency = PostingUrgency.REDUCE

                    active = [e.name for e in self.calendar.get_active_events(current) if platform in e.platforms]
                    upcoming = [
                        e.name for e in self.calendar.get_events_for_platform(platform, current)
                        if e.date_start > current
                    ]

                    rec = TimingRecommendation(
                        platform=platform,
                        recommended_datetime=datetime(current.year, current.month, current.day, hour, 0),
                        score=round(score, 2),
                        urgency=urgency,
                        rationale=rationale,
                        active_events=active,
                        upcoming_events=upcoming,
                    )
                    recommendations.append(rec)
            current += timedelta(days=1)

        advisory = self.news.get_cached_advisory() or {}

        result = TimingResponse(
            recommendations=sorted(recommendations, key=lambda r: r.score, reverse=True),
            date_range=f"{req.date_start} to {req.date_end}",
            news_sentiment=advisory.get("urgency", "normal"),
            crisis_active=advisory.get("crisis_active", False),
        )

        # Log the decision
        if self.agent_logger:
            self.agent_logger.log_decision(
                decision_type=DecisionType.TIMING_RECOMMENDATION,
                agent_name="timing_engine",
                action=f"Generated {len(recommendations)} timing recommendations for {len(req.platforms)} platforms",
                rationale=f"Date range: {req.date_start} to {req.date_end}, News: {advisory.get('urgency', 'normal')}, Crisis: {advisory.get('crisis_active', False)}",
                input_summary=req.model_dump(mode="json"),
                output_summary={"total_recommendations": len(recommendations), "top_score": recommendations[0].score if recommendations else 0},
            )

        return result

    def get_weekly_schedule(self, week_start: date, platforms: list[Platform]) -> list[TimingRecommendation]:
        req = TimingRequest(
            platforms=platforms,
            date_start=week_start,
            date_end=week_start + timedelta(days=6),
            slots_per_platform=1,
        )
        result = self.recommend_timing(req)
        return result.recommendations

    def should_post_now(self, platform: Platform) -> ShouldPostResponse:
        now = datetime.now()
        score, rationale = self._score_slot(platform, now.date(), now.hour)

        should = score >= 0.8
        if score < 0:
            reason = f"BLOCKED: {rationale}"
        elif should:
            reason = f"Good time to post. {rationale}"
        else:
            # Find next good slot
            reason = f"Not ideal right now (score={score:.2f}). {rationale}"

        result = ShouldPostResponse(
            should_post=should,
            platform=platform,
            reason=reason,
            score=round(score, 2),
        )

        if self.agent_logger:
            self.agent_logger.log_decision(
                decision_type=DecisionType.TIMING_RECOMMENDATION,
                agent_name="timing_engine",
                action=f"Should-post-now check for {platform.value}: {'YES' if should else 'NO'}",
                rationale=rationale,
                input_summary={"platform": platform.value, "hour": now.hour},
                output_summary={"should_post": should, "score": round(score, 2)},
                platform=platform,
            )

        return result
