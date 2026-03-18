"""Request / response models for the tweet thread endpoint."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from src.models.outline import ContentOutline


class Tweet(BaseModel):
    tweet_number: int
    text: str
    char_count: int


class TweetThreadRequest(BaseModel):
    outline: Optional[ContentOutline] = None
    blog_html: Optional[str] = None
    blog_title: Optional[str] = None
    brand: str = "SellerBuddy"


class TweetThreadResponse(BaseModel):
    title: str
    tweets: List[Tweet]
    total_tweets: int
