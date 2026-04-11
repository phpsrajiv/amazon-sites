from pydantic import BaseModel
from typing import Optional

from src.models.common import ContentTone


class LinkedInTextPost(BaseModel):
    hook_line: str
    body: str
    hashtags: list[str]
    cta: str


class LinkedInPoll(BaseModel):
    question: str
    options: list[str]
    context_text: str


class LinkedInRequest(BaseModel):
    topic: str
    brand: str = "SellerBuddy"
    tone: ContentTone = ContentTone.PROFESSIONAL
    event_context: Optional[str] = None
    include_poll: bool = True


class LinkedInResponse(BaseModel):
    text_post: LinkedInTextPost
    poll: Optional[LinkedInPoll] = None
    topic: str
    event_context: Optional[str] = None
