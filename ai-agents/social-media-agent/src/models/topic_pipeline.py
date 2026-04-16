from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from src.models.common import ContentTone
from src.models.facebook import FacebookResponse
from src.models.linkedin import LinkedInResponse
from src.models.instagram import InstagramResponse
from src.models.timing import TimingResponse


class TopicSource(str, Enum):
    CALENDAR_EVENT = "calendar_event"
    SEO_KEYWORD = "seo_keyword"
    BLOG_REPURPOSE = "blog_repurpose"


class CandidateTopic(BaseModel):
    source: TopicSource
    title: str
    description: str
    relevance_score: float
    source_metadata: dict = {}


class SelectedTopic(BaseModel):
    topic: str
    source: TopicSource
    rationale: str
    suggested_tone: ContentTone
    event_context: Optional[str] = None
    priority: int = 1


class PlatformContent(BaseModel):
    topic: str
    source: TopicSource
    facebook: Optional[FacebookResponse] = None
    linkedin: Optional[LinkedInResponse] = None
    instagram: Optional[InstagramResponse] = None
    timing: Optional[TimingResponse] = None


class WeeklyContentPlanRequest(BaseModel):
    brand: str = "SellerBuddy"
    num_topics: int = 5
    calendar_days_ahead: int = 14
    max_blogs: int = 10


class WeeklyContentPlanResponse(BaseModel):
    plan_id: str
    generated_at: datetime
    topics_considered: int
    topics_selected: int
    content: list[PlatformContent]
    sources_summary: dict
    warnings: list[str] = []
