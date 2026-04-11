from pydantic import BaseModel
from typing import Optional

from src.models.common import ContentTone


class FacebookPost(BaseModel):
    text: str
    hashtags: list[str]
    engagement_question: str
    image_prompt: str
    tone: ContentTone


class FacebookRequest(BaseModel):
    topic: str
    brand: str = "SellerBuddy"
    tone: ContentTone = ContentTone.CONVERSATIONAL
    event_context: Optional[str] = None
    num_variants: int = 3


class FacebookResponse(BaseModel):
    variants: list[FacebookPost]
    topic: str
    event_context: Optional[str] = None
