from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from src.models.common import Platform, PostingUrgency


class TimingRecommendation(BaseModel):
    platform: Platform
    recommended_datetime: datetime
    score: float
    urgency: PostingUrgency
    rationale: str
    active_events: list[str] = []
    upcoming_events: list[str] = []
    news_advisory: Optional[str] = None


class TimingRequest(BaseModel):
    platforms: list[Platform] = [Platform.FACEBOOK, Platform.LINKEDIN, Platform.INSTAGRAM]
    date_start: date
    date_end: date
    slots_per_platform: int = 3


class TimingResponse(BaseModel):
    recommendations: list[TimingRecommendation]
    date_range: str
    news_sentiment: str = "normal"
    crisis_active: bool = False


class WeeklyScheduleRequest(BaseModel):
    week_start: date
    platforms: list[Platform] = [Platform.FACEBOOK, Platform.LINKEDIN, Platform.INSTAGRAM]


class ShouldPostResponse(BaseModel):
    should_post: bool
    platform: Platform
    reason: str
    score: float
    suggested_time: Optional[datetime] = None
