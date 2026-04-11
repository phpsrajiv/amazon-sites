from pydantic import BaseModel
from typing import Optional
from datetime import date

from src.models.common import Platform, PostingUrgency


class CalendarEvent(BaseModel):
    name: str
    date_start: date
    date_end: date
    category: str
    relevance_score: float
    posting_urgency: PostingUrgency
    platforms: list[Platform]
    suggested_themes: list[str]
    pre_event_days: int = 5
    post_event_days: int = 1


class CalendarEventCreate(BaseModel):
    name: str
    date_start: date
    date_end: date
    category: str
    relevance_score: float = 0.5
    posting_urgency: PostingUrgency = PostingUrgency.NORMAL
    platforms: list[Platform] = [Platform.FACEBOOK, Platform.INSTAGRAM]
    suggested_themes: list[str] = []
    pre_event_days: int = 5
    post_event_days: int = 1


class AnnualCalendar(BaseModel):
    year: int
    events: list[CalendarEvent]
    total_events: int
