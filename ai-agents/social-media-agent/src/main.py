import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SellerBuddy Social Media Agent",
    description="AI agent for generating social media posts with smart timing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy singletons
# ---------------------------------------------------------------------------
_timing_engine = None
_facebook_gen = None
_linkedin_gen = None
_instagram_gen = None
_calendar_service = None
_news_service = None
_engagement_service = None
_agent_logger = None
_drupal_client = None
_seo_client = None
_topic_pipeline = None


def get_calendar_service():
    global _calendar_service
    if _calendar_service is None:
        from src.services.events_calendar_service import EventsCalendarService
        _calendar_service = EventsCalendarService()
    return _calendar_service


def get_news_service():
    global _news_service
    if _news_service is None:
        from src.services.news_sentiment_service import NewsSentimentService
        _news_service = NewsSentimentService()
    return _news_service


def get_engagement_service():
    global _engagement_service
    if _engagement_service is None:
        from src.services.engagement_service import EngagementService
        _engagement_service = EngagementService()
    return _engagement_service


def get_agent_logger():
    global _agent_logger
    if _agent_logger is None:
        from src.services.agent_logger import AgentLogger
        _agent_logger = AgentLogger()
    return _agent_logger


def get_timing_engine():
    global _timing_engine
    if _timing_engine is None:
        from src.agents.timing_engine import TimingEngine
        _timing_engine = TimingEngine(
            calendar_service=get_calendar_service(),
            news_service=get_news_service(),
            engagement_service=get_engagement_service(),
            agent_logger=get_agent_logger(),
        )
    return _timing_engine


def get_facebook_gen():
    global _facebook_gen
    if _facebook_gen is None:
        from src.agents.facebook_generator import FacebookGenerator
        _facebook_gen = FacebookGenerator(agent_logger=get_agent_logger())
    return _facebook_gen


def get_linkedin_gen():
    global _linkedin_gen
    if _linkedin_gen is None:
        from src.agents.linkedin_post_generator import LinkedInPostGenerator
        _linkedin_gen = LinkedInPostGenerator(agent_logger=get_agent_logger())
    return _linkedin_gen


def get_instagram_gen():
    global _instagram_gen
    if _instagram_gen is None:
        from src.agents.instagram_generator import InstagramGenerator
        _instagram_gen = InstagramGenerator(agent_logger=get_agent_logger())
    return _instagram_gen


def get_drupal_client():
    global _drupal_client
    if _drupal_client is None:
        from src.services.drupal_client import DrupalClient
        _drupal_client = DrupalClient()
    return _drupal_client


def get_seo_client():
    global _seo_client
    if _seo_client is None:
        from src.services.seo_client import SEOClient
        _seo_client = SEOClient()
    return _seo_client


def get_topic_pipeline():
    global _topic_pipeline
    if _topic_pipeline is None:
        from src.agents.topic_pipeline import TopicPipeline
        _topic_pipeline = TopicPipeline(
            calendar_service=get_calendar_service(),
            seo_client=get_seo_client(),
            drupal_client=get_drupal_client(),
            agent_logger=get_agent_logger(),
            timing_engine=get_timing_engine(),
            facebook_gen=get_facebook_gen(),
            linkedin_gen=get_linkedin_gen(),
            instagram_gen=get_instagram_gen(),
        )
    return _topic_pipeline


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "social-media-agent",
        "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
        "fast_model": os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo"),
    }


# ---------------------------------------------------------------------------
# Calendar endpoints
# ---------------------------------------------------------------------------
from src.models.calendar_events import CalendarEventCreate

@app.get("/api/social/calendar/events")
async def get_upcoming_events(days_ahead: int = 30):
    try:
        svc = get_calendar_service()
        events = svc.get_upcoming_events(days_ahead=days_ahead)
        return {"events": [e.model_dump(mode="json") for e in events], "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/calendar/year/{year}")
async def get_annual_calendar(year: int):
    try:
        svc = get_calendar_service()
        cal = svc.get_annual_calendar(year=year)
        return cal.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/social/calendar/events")
async def add_custom_event(event: CalendarEventCreate):
    try:
        svc = get_calendar_service()
        created = svc.add_custom_event(event)
        return created.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Timing endpoints
# ---------------------------------------------------------------------------
from src.models.timing import TimingRequest, WeeklyScheduleRequest

@app.post("/api/social/timing/recommend")
async def recommend_timing(req: TimingRequest):
    try:
        engine = get_timing_engine()
        result = engine.recommend_timing(req)
        return result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/social/timing/weekly-schedule")
async def weekly_schedule(req: WeeklyScheduleRequest):
    try:
        engine = get_timing_engine()
        result = engine.get_weekly_schedule(req.week_start, req.platforms)
        return {"schedule": [r.model_dump(mode="json") for r in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/timing/should-post-now/{platform}")
async def should_post_now(platform: str):
    try:
        from src.models.common import Platform
        p = Platform(platform)
        engine = get_timing_engine()
        result = engine.should_post_now(p)
        return result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Content generation endpoints
# ---------------------------------------------------------------------------
from src.models.facebook import FacebookRequest
from src.models.linkedin import LinkedInRequest
from src.models.instagram import InstagramRequest

@app.post("/api/social/generate/facebook")
async def generate_facebook(req: FacebookRequest):
    try:
        gen = get_facebook_gen()
        result = gen.generate(req)
        return result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/social/generate/linkedin")
async def generate_linkedin(req: LinkedInRequest):
    try:
        gen = get_linkedin_gen()
        result = gen.generate(req)
        return result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/social/generate/instagram")
async def generate_instagram(req: InstagramRequest):
    try:
        gen = get_instagram_gen()
        result = gen.generate(req)
        return result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/social/generate/all")
async def generate_all(topic: str, brand: str = "SellerBuddy", event_context: str | None = None):
    try:
        from src.models.common import Platform, ContentTone
        from src.models.timing import TimingRequest
        from datetime import date, timedelta

        # Get timing first
        engine = get_timing_engine()
        today = date.today()
        timing_req = TimingRequest(
            platforms=[Platform.FACEBOOK, Platform.LINKEDIN, Platform.INSTAGRAM],
            date_start=today,
            date_end=today + timedelta(days=7),
        )
        timing = engine.recommend_timing(timing_req)

        # Generate content for all platforms
        fb_req = FacebookRequest(topic=topic, brand=brand, event_context=event_context)
        li_req = LinkedInRequest(topic=topic, brand=brand, event_context=event_context)
        ig_req = InstagramRequest(topic=topic, brand=brand, event_context=event_context)

        fb_result = get_facebook_gen().generate(fb_req)
        li_result = get_linkedin_gen().generate(li_req)
        ig_result = get_instagram_gen().generate(ig_req)

        return {
            "timing": timing.model_dump(mode="json"),
            "facebook": fb_result.model_dump(mode="json"),
            "linkedin": li_result.model_dump(mode="json"),
            "instagram": ig_result.model_dump(mode="json"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Weekly content pipeline (Topic Pipeline)
# ---------------------------------------------------------------------------
from src.models.topic_pipeline import WeeklyContentPlanRequest

@app.post("/api/social/generate/weekly-content")
async def generate_weekly_content(req: WeeklyContentPlanRequest):
    try:
        pipeline = get_topic_pipeline()
        result = pipeline.generate_weekly_plan(req)
        return result.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# News sentiment endpoint
# ---------------------------------------------------------------------------
@app.get("/api/social/news/sentiment")
async def news_sentiment():
    try:
        svc = get_news_service()
        advisory = svc.get_posting_advisory()
        return advisory
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Engagement endpoints
# ---------------------------------------------------------------------------
from src.models.engagement import EngagementLogEntry

@app.post("/api/social/engagement/log")
async def log_engagement(entry: EngagementLogEntry):
    try:
        svc = get_engagement_service()
        svc.log_engagement(entry)
        logger = get_agent_logger()
        from src.models.logging import DecisionType
        logger.log_decision(
            decision_type=DecisionType.ENGAGEMENT_LOGGED,
            agent_name="engagement_service",
            action=f"Logged engagement for {entry.platform.value} post",
            rationale=f"Post type: {entry.post_type}, Impressions: {entry.metrics.impressions}, Likes: {entry.metrics.likes}",
            input_summary=entry.model_dump(mode="json"),
            output_summary={"status": "logged"},
            platform=entry.platform,
            event_context=entry.event_context,
        )
        return {"status": "logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/analytics/best-times/{platform}")
async def best_times(platform: str):
    try:
        from src.models.common import Platform
        p = Platform(platform)
        svc = get_engagement_service()
        times = svc.get_best_times(p)
        return {"platform": platform, "best_times": times}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/analytics/weekly-report")
async def weekly_report(week_start: str | None = None):
    try:
        from datetime import date
        if week_start:
            ws = date.fromisoformat(week_start)
        else:
            today = date.today()
            ws = today - __import__("datetime").timedelta(days=today.weekday())
        svc = get_engagement_service()
        report = svc.get_weekly_report(ws)
        return report.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Logging / audit endpoints
# ---------------------------------------------------------------------------
from src.models.logging import DecisionLogQuery, PostLogQuery

@app.get("/api/social/logs/decisions")
async def get_decision_logs(
    date_start: str | None = None,
    date_end: str | None = None,
    platform: str | None = None,
    decision_type: str | None = None,
    agent_name: str | None = None,
    limit: int = 50,
):
    try:
        from datetime import date as d
        from src.models.common import Platform as P
        from src.models.logging import DecisionType
        logger = get_agent_logger()
        query = DecisionLogQuery(
            date_start=d.fromisoformat(date_start) if date_start else None,
            date_end=d.fromisoformat(date_end) if date_end else None,
            platform=P(platform) if platform else None,
            decision_type=DecisionType(decision_type) if decision_type else None,
            agent_name=agent_name,
            limit=limit,
        )
        decisions = logger.get_decisions(query)
        return {"decisions": [dec.model_dump(mode="json") for dec in decisions], "count": len(decisions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/logs/posts")
async def get_post_logs(
    date_start: str | None = None,
    date_end: str | None = None,
    platform: str | None = None,
    post_type: str | None = None,
    limit: int = 50,
):
    try:
        from datetime import date as d
        from src.models.common import Platform as P
        logger = get_agent_logger()
        query = PostLogQuery(
            date_start=d.fromisoformat(date_start) if date_start else None,
            date_end=d.fromisoformat(date_end) if date_end else None,
            platform=P(platform) if platform else None,
            post_type=post_type,
            limit=limit,
        )
        posts = logger.get_posts(query)
        return {"posts": [p.model_dump(mode="json") for p in posts], "count": len(posts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/logs/decisions/{decision_id}")
async def get_decision_chain(decision_id: str):
    try:
        logger = get_agent_logger()
        chain = logger.get_decision_chain(decision_id)
        return chain
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/social/logs/summary")
async def get_log_summary():
    try:
        logger = get_agent_logger()
        summary = logger.get_summary()
        return summary.model_dump(mode="json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
