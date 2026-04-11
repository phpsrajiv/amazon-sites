from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from src.models.common import Platform


class EngagementMetrics(BaseModel):
    impressions: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0


class EngagementLogEntry(BaseModel):
    platform: Platform
    published_at: datetime
    post_type: str
    event_context: Optional[str] = None
    metrics: EngagementMetrics


class WeeklyReport(BaseModel):
    week_start: date
    total_posts: int
    avg_engagement_rate: float
    best_performing_post: Optional[EngagementLogEntry] = None
    platform_breakdown: dict[str, EngagementMetrics]
    vs_previous_week: str
