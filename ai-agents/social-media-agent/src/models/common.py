from enum import Enum


class Platform(str, Enum):
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"


class ContentTone(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    FESTIVE = "festive"


class PostingUrgency(str, Enum):
    PAUSE = "pause"
    REDUCE = "reduce"
    NORMAL = "normal"
    BOOST = "boost"
