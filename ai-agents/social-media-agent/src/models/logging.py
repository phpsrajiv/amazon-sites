from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

from src.models.common import Platform


class DecisionType(str, Enum):
    TIMING_RECOMMENDATION = "timing_recommendation"
    CRISIS_OVERRIDE = "crisis_override"
    CONTENT_GENERATION = "content_generation"
    POST_PUBLISHED = "post_published"
    ENGAGEMENT_LOGGED = "engagement_logged"


class DecisionLogEntry(BaseModel):
    id: str
    timestamp: datetime
    decision_type: DecisionType
    platform: Optional[Platform] = None
    agent_name: str
    action: str
    rationale: str
    input_summary: dict
    output_summary: dict
    event_context: Optional[str] = None
    news_context: Optional[str] = None


class PostLogEntry(BaseModel):
    id: str
    timestamp: datetime
    platform: Platform
    post_type: str
    content_preview: str
    timing_score: float
    timing_rationale: str
    event_context: Optional[str] = None
    decision_log_id: str


class DecisionLogQuery(BaseModel):
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    platform: Optional[Platform] = None
    decision_type: Optional[DecisionType] = None
    agent_name: Optional[str] = None
    limit: int = 50


class PostLogQuery(BaseModel):
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    platform: Optional[Platform] = None
    post_type: Optional[str] = None
    limit: int = 50


class LogSummary(BaseModel):
    total_decisions: int
    total_posts: int
    decisions_by_type: dict[str, int]
    posts_by_platform: dict[str, int]
    recent_decisions: list[DecisionLogEntry]
    recent_posts: list[PostLogEntry]
