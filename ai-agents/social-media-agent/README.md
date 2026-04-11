# SellerBuddy Social Media Agent

AI agent for generating social media posts (Facebook, LinkedIn, Instagram) with smart timing intelligence. The core differentiator is **understanding WHEN to publish**, not just WHAT to publish — posts during war/crisis get drowned out; posts during festivals/Amazon sales drive 3-5x engagement.

**Port:** 8005
**Stack:** FastAPI + LangChain + OpenAI (gpt-3.5-turbo / gpt-4-turbo-preview)
**Container:** `selleragent-social-media`

---

## Architecture

```
ai-agents/social-media-agent/
├── Dockerfile
├── requirements.txt
├── README.md
└── src/
    ├── main.py                              # FastAPI endpoints (21 total)
    ├── agents/
    │   ├── timing_engine.py                 # Core: 5-step scoring algorithm for WHEN to post
    │   ├── facebook_generator.py            # Facebook posts (gpt-3.5-turbo)
    │   ├── linkedin_post_generator.py       # LinkedIn text posts + polls (gpt-3.5-turbo)
    │   └── instagram_generator.py           # Instagram Reel scripts + captions (gpt-4-turbo)
    ├── models/
    │   ├── common.py                        # Platform, ContentTone, PostingUrgency enums
    │   ├── calendar_events.py               # CalendarEvent, AnnualCalendar
    │   ├── timing.py                        # TimingRecommendation, TimingRequest/Response
    │   ├── facebook.py                      # FacebookPost, FacebookRequest/Response
    │   ├── linkedin.py                      # LinkedInTextPost, LinkedInPoll
    │   ├── instagram.py                     # ReelScript, InstagramCaption
    │   ├── engagement.py                    # EngagementMetrics, EngagementLogEntry, WeeklyReport
    │   └── logging.py                       # DecisionLogEntry, PostLogEntry, DecisionType
    ├── services/
    │   ├── events_calendar_service.py       # Loads + queries annual events calendar
    │   ├── news_sentiment_service.py        # NewsAPI + LLM crisis detection
    │   ├── engagement_service.py            # Log + analyze engagement data
    │   ├── agent_logger.py                  # Decision & post audit logging
    │   └── drupal_client.py                 # Push drafts to Drupal (JSON:API)
    └── data/
        ├── india_events_2026.json           # 35 events: festivals, sales, holidays
        ├── platform_timing.json             # Peak engagement windows per platform (IST)
        ├── decision_log.json                # Auto-created: agent decision audit trail
        ├── post_log.json                    # Auto-created: post publication log
        └── engagement_log.json              # Auto-created: engagement metrics history
```

---

## Quick Start

```bash
# From the amazon-sites root directory
docker compose up social-media-agent --build

# Health check
curl http://localhost:8005/health

# Swagger UI
open http://localhost:8005/docs
```

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OPENAI_API_KEY` | — | Yes | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4-turbo-preview` | No | Model for Instagram Reels (creative content) |
| `OPENAI_FAST_MODEL` | `gpt-3.5-turbo` | No | Model for Facebook/LinkedIn + crisis detection |
| `NEWS_API_KEY` | — | No | NewsAPI.org key for crisis detection (graceful fallback if not set) |
| `DRUPAL_BASE_URL` | `http://drupal:80` | No | Drupal backend URL |
| `DRUPAL_USERNAME` | `admin` | No | Drupal basic auth username |
| `DRUPAL_PASSWORD` | `admin` | No | Drupal basic auth password |

---

## 5-Step Timing Scoring Algorithm

Every candidate posting slot is scored through these 5 steps:

```
score = 0.0

# Step 1: Platform engagement baseline (from platform_timing.json)
#   LinkedIn weekday 8-10am = 1.5x, Facebook 1-4pm = 1.4x, Instagram 6-9pm = 1.5x
if slot in peak_window: score += window.multiplier (1.2-1.5)
else: score += 0.5

# Step 2: Calendar event boost
for event in active_events(slot.date):
    if platform in event.platforms:
        score += event.relevance_score * 0.5   # Diwali = +0.5, minor event = +0.25
    if event.urgency == "boost": score += 0.3

# Step 3: Pre-event ramp-up (content builds anticipation)
for event in upcoming_events(slot.date, 7 days):
    days_until = event.start - slot.date
    if days_until <= event.pre_event_days:
        score += relevance * 0.2 * (1 - days_until/pre_event_days)

# Step 4: News sentiment (hard override)
if crisis_active: score = -1.0 (BLOCK all posts)
elif negative_sentiment: score *= 0.5

# Step 5: Historical engagement (requires >= 10 data points)
if this_slot_outperforms_avg_by_20%: score += 0.3
elif this_slot_underperforms_avg_by_50%: score -= 0.2
```

---

## API Reference (21 Endpoints)

### Health & Status

---

#### `GET /health`

Quick health check to verify the service is running.

**Response:**
```json
{
  "status": "ok",
  "service": "social-media-agent",
  "model": "gpt-4-turbo-preview",
  "fast_model": "gpt-3.5-turbo"
}
```

---

### Calendar Endpoints

---

#### `GET /api/social/calendar/events?days_ahead=30`

Get upcoming events within a date range from today. Use this to see what festivals, sales, or holidays are coming up that should influence your posting strategy.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `days_ahead` | int | 30 | How many days to look ahead |

**Response:**
```json
{
  "events": [
    {
      "name": "Diwali",
      "date_start": "2026-11-05",
      "date_end": "2026-11-05",
      "category": "festival",
      "relevance_score": 1.0,
      "posting_urgency": "boost",
      "platforms": ["facebook", "linkedin", "instagram"],
      "suggested_themes": ["festival of lights", "diwali deals", "gifting", "home decor", "diyas", "fireworks", "new beginnings"],
      "pre_event_days": 14,
      "post_event_days": 3
    }
  ],
  "count": 5
}
```

**Included Events (35 total):**
- **Festivals:** Makar Sankranti, Pongal, Holi, Ugadi, Ram Navami, Baisakhi, Eid ul-Fitr, Eid ul-Adha, Raksha Bandhan, Ganesh Chaturthi, Onam, Navratri, Dussehra, Karwa Chauth, Diwali, Bhai Dooj, Christmas
- **National:** Republic Day, Independence Day
- **Ecommerce:** Amazon Republic Day Sale, Amazon Summer Sale, Amazon Prime Day, Amazon Independence Day Sale, Amazon Great Indian Festival, Flipkart Big Billion Days, Black Friday, Cyber Monday, End of Year Sale
- **Awareness:** World MSME Day, Small Business Saturday
- **Seasonal:** Valentine's Day, Mother's Day, Father's Day, Back to School, Monsoon Season, Wedding Season

---

#### `GET /api/social/calendar/year/{year}`

Get the full annual calendar for a given year. Useful for annual planning and seeing all 35 events at once.

**Path Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `year` | int | Calendar year (e.g., 2026) |

**Response:**
```json
{
  "year": 2026,
  "events": [ ... ],
  "total_events": 35
}
```

---

#### `POST /api/social/calendar/events`

Add a custom event (e.g., your brand anniversary, a product launch) to the calendar so the timing engine factors it into recommendations.

**Request Body:**
```json
{
  "name": "SellerBuddy Product Launch",
  "date_start": "2026-05-15",
  "date_end": "2026-05-15",
  "category": "brand",
  "relevance_score": 0.9,
  "posting_urgency": "boost",
  "platforms": ["facebook", "linkedin", "instagram"],
  "suggested_themes": ["launch day", "new features", "early access"],
  "pre_event_days": 7,
  "post_event_days": 2
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | — | Event name |
| `date_start` | date | Yes | — | Start date (YYYY-MM-DD) |
| `date_end` | date | Yes | — | End date (YYYY-MM-DD) |
| `category` | string | Yes | — | Category: festival, ecommerce, national, seasonal, awareness, brand |
| `relevance_score` | float | No | 0.5 | 0.0 to 1.0 — how relevant to your brand |
| `posting_urgency` | string | No | "normal" | "pause", "reduce", "normal", "boost" |
| `platforms` | list | No | ["facebook", "instagram"] | Which platforms to target |
| `suggested_themes` | list | No | [] | Content theme suggestions |
| `pre_event_days` | int | No | 5 | Days before event to start ramping up |
| `post_event_days` | int | No | 1 | Days after event to continue posting |

**Response:** The created event object.

---

### Timing Endpoints (Core Intelligence)

---

#### `POST /api/social/timing/recommend`

The brain of the agent. Scores every possible posting slot across your requested platforms and date range using the 5-step scoring algorithm. Returns the best time slots sorted by score.

**Request Body:**
```json
{
  "platforms": ["facebook", "linkedin", "instagram"],
  "date_start": "2026-04-06",
  "date_end": "2026-04-12",
  "slots_per_platform": 3
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `platforms` | list | No | all 3 | Which platforms to score |
| `date_start` | date | Yes | — | Start of date range |
| `date_end` | date | Yes | — | End of date range |
| `slots_per_platform` | int | No | 3 | Top N time slots per platform per day |

**Response:**
```json
{
  "recommendations": [
    {
      "platform": "instagram",
      "recommended_datetime": "2026-04-08T19:00:00",
      "score": 1.85,
      "urgency": "boost",
      "rationale": "Platform baseline: 1.5 (Peak: Evening scroll) | Active event 'Ram Navami': +0.25 | Boost urgency for 'Ram Navami': +0.3",
      "active_events": ["Ram Navami"],
      "upcoming_events": ["Baisakhi"],
      "news_advisory": null
    },
    {
      "platform": "linkedin",
      "recommended_datetime": "2026-04-07T08:00:00",
      "score": 1.50,
      "urgency": "normal",
      "rationale": "Platform baseline: 1.5 (Peak: Morning commute)",
      "active_events": [],
      "upcoming_events": ["Ram Navami"],
      "news_advisory": null
    }
  ],
  "date_range": "2026-04-06 to 2026-04-12",
  "news_sentiment": "normal",
  "crisis_active": false
}
```

**Urgency mapping from score:**
- `score < 0` → `pause` (crisis blocked)
- `score >= 1.5` → `boost`
- `score >= 0.8` → `normal`
- `score < 0.8` → `reduce`

---

#### `POST /api/social/timing/weekly-schedule`

Generate a full week posting schedule — 1 best slot per platform per day. Think of this as your weekly content calendar.

**Request Body:**
```json
{
  "week_start": "2026-04-06",
  "platforms": ["facebook", "linkedin", "instagram"]
}
```

**Response:**
```json
{
  "schedule": [
    {
      "platform": "instagram",
      "recommended_datetime": "2026-04-06T19:00:00",
      "score": 1.50,
      "urgency": "normal",
      "rationale": "Platform baseline: 1.5 (Peak: Evening scroll)",
      "active_events": [],
      "upcoming_events": ["Ram Navami"]
    }
  ]
}
```

Returns 21 recommendations (7 days x 3 platforms), each with the single best time slot.

---

#### `GET /api/social/timing/should-post-now/{platform}`

Real-time check — "Should I post on Instagram RIGHT NOW?" Scores the current hour on the current day and gives a yes/no with reasoning.

**Path Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `platform` | string | `facebook`, `linkedin`, or `instagram` |

**Response:**
```json
{
  "should_post": true,
  "platform": "instagram",
  "reason": "Good time to post. Platform baseline: 1.5 (Peak: Evening scroll)",
  "score": 1.5,
  "suggested_time": null
}
```

Decision threshold: `score >= 0.8` = should post.

---

### Content Generation Endpoints

---

#### `POST /api/social/generate/facebook`

Generate 2-3 Facebook post variants. Each variant is conversational, uses emojis, ends with an engagement question, and includes a Canva image prompt.

**Model:** gpt-3.5-turbo (temperature=0.7)

**Request Body:**
```json
{
  "topic": "How to optimize Amazon PPC campaigns during festive season",
  "brand": "SellerBuddy",
  "tone": "conversational",
  "event_context": "Diwali",
  "num_variants": 3
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | Yes | — | Post topic |
| `brand` | string | No | "SellerBuddy" | Brand name |
| `tone` | string | No | "conversational" | One of: professional, conversational, inspirational, educational, promotional, festive |
| `event_context` | string | No | null | Event to weave into the post (e.g., "Diwali") |
| `num_variants` | int | No | 3 | Number of post variants to generate |

**Response:**
```json
{
  "variants": [
    {
      "text": "Diwali is coming and so are the BIG sales! Here's what smart sellers are doing to maximize their PPC returns this festive season...",
      "hashtags": ["#AmazonSeller", "#DiwaliSale", "#PPCTips", "#D2C"],
      "engagement_question": "What's your biggest PPC challenge during festive season?",
      "image_prompt": "Festive Diwali-themed infographic showing PPC optimization tips with gold and orange tones, diyas in background",
      "tone": "conversational"
    }
  ],
  "topic": "How to optimize Amazon PPC campaigns during festive season",
  "event_context": "Diwali"
}
```

---

#### `POST /api/social/generate/linkedin`

Generate a professional LinkedIn text post + optional poll. The post has a strong hook line, insightful body, hashtags, and CTA. Does NOT generate carousels (those are handled by the content-writer-agent).

**Model:** gpt-3.5-turbo (temperature=0.6)

**Request Body:**
```json
{
  "topic": "Why D2C brands should invest in A+ Content on Amazon",
  "brand": "SellerBuddy",
  "tone": "professional",
  "event_context": null,
  "include_poll": true
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | Yes | — | Post topic |
| `brand` | string | No | "SellerBuddy" | Brand name |
| `tone` | string | No | "professional" | Content tone |
| `event_context` | string | No | null | Event to reference |
| `include_poll` | bool | No | true | Whether to generate a LinkedIn poll |

**Response:**
```json
{
  "text_post": {
    "hook_line": "82% of Amazon shoppers read A+ Content before buying. Are you leaving money on the table?",
    "body": "In the last 6 months, we've seen D2C brands increase their conversion by 15-25% with well-crafted A+ Content. Here's what the top sellers are doing differently...",
    "hashtags": ["#AmazonSeller", "#D2CBrands", "#APlusContent", "#Ecommerce"],
    "cta": "Follow SellerBuddy for weekly Amazon seller insights"
  },
  "poll": {
    "question": "Does your brand use A+ Content on Amazon?",
    "options": ["Yes, fully optimized", "Yes, but needs work", "No, haven't started", "What's A+ Content?"],
    "context_text": "We're curious about A+ Content adoption among D2C brands."
  },
  "topic": "Why D2C brands should invest in A+ Content on Amazon",
  "event_context": null
}
```

---

#### `POST /api/social/generate/instagram`

Generate an Instagram Reel script + caption. Uses the more creative gpt-4 model because Reels need higher quality, structured output (hook, body segments with timestamps, CTA, music mood, text overlays) plus a caption with 20-30 hashtags.

**Model:** gpt-4-turbo-preview (temperature=0.7)

**Request Body:**
```json
{
  "topic": "5 mistakes new Amazon sellers make",
  "brand": "SellerBuddy",
  "tone": "inspirational",
  "event_context": null,
  "reel_duration": 30
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | Yes | — | Reel topic |
| `brand` | string | No | "SellerBuddy" | Brand name |
| `tone` | string | No | "inspirational" | Content tone |
| `event_context` | string | No | null | Event to make the Reel timely |
| `reel_duration` | int | No | 30 | Target duration in seconds |

**Response:**
```json
{
  "reel_script": {
    "hook": "STOP making these 5 mistakes on Amazon!",
    "segments": [
      {
        "timestamp": "0:03-0:08",
        "visual": "Screen recording of a bad listing with red highlights",
        "voiceover": "Mistake number 1: Your title is a keyword dump. Amazon's algorithm hates this.",
        "text_overlay": "Mistake #1: Keyword-stuffed titles"
      },
      {
        "timestamp": "0:08-0:14",
        "visual": "Split screen: bad vs good product images",
        "voiceover": "Mistake number 2: Low-quality product images. Your main image is your storefront.",
        "text_overlay": "Mistake #2: Bad product photos"
      }
    ],
    "cta": "Follow @SellerBuddy for daily Amazon tips!",
    "duration_seconds": 30,
    "music_mood": "upbeat",
    "text_overlays": ["Mistake #1: Keyword-stuffed titles", "Mistake #2: Bad product photos", "Mistake #3: Ignoring A+ Content", "Mistake #4: No PPC strategy", "Mistake #5: Pricing too high"]
  },
  "caption": {
    "text": "Are you making these costly mistakes as an Amazon seller? I've seen hundreds of new sellers lose money because of these 5 common errors. The good news? They're all fixable. Save this Reel and share it with a seller friend who needs to see this!",
    "hashtags": ["#AmazonSeller", "#D2C", "#EcommerceTips", "#AmazonFBA", "#SellerTips", "#OnlineBusiness", "#AmazonPPC", "#ProductListing", "#APlusContent", "#SellerBuddy", "#AmazonIndia", "#D2CBrands", "#StartupIndia", "#BusinessTips", "#AmazonSelling", "#EcommerceIndia", "#DigitalCommerce", "#SmallBusiness", "#EntrepreneurLife", "#AmazonSuccess"]
  },
  "topic": "5 mistakes new Amazon sellers make",
  "event_context": null
}
```

---

#### `POST /api/social/generate/all`

Full pipeline — generates content for ALL 3 platforms + timing recommendations in a single call. This is the "one-click" endpoint for weekly content creation.

**Query Parameters:**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | Yes | — | Content topic |
| `brand` | string | No | "SellerBuddy" | Brand name |
| `event_context` | string | No | null | Event context for all platforms |

**Response:**
```json
{
  "timing": {
    "recommendations": [ ... ],
    "date_range": "2026-04-06 to 2026-04-13",
    "news_sentiment": "normal",
    "crisis_active": false
  },
  "facebook": {
    "variants": [ ... ],
    "topic": "...",
    "event_context": null
  },
  "linkedin": {
    "text_post": { ... },
    "poll": { ... },
    "topic": "...",
    "event_context": null
  },
  "instagram": {
    "reel_script": { ... },
    "caption": { ... },
    "topic": "...",
    "event_context": null
  }
}
```

---

### News Sentiment

---

#### `GET /api/social/news/sentiment`

Check current news sentiment in India. Uses NewsAPI to fetch top 20 headlines, then gpt-3.5-turbo classifies them for crisis detection (war, natural disaster, national mourning, terrorist attack, major political crisis). If `NEWS_API_KEY` is not set, gracefully returns "normal" with a warning.

**Response (normal):**
```json
{
  "urgency": "normal",
  "crisis_active": false,
  "reason": "No active crisis detected in current headlines",
  "headlines_checked": 20,
  "top_headlines": [
    "India's GDP grows 7.2% in Q4",
    "New startup policy announced by PM",
    "IPL 2026: Mumbai Indians win thriller",
    "Monsoon expected early this year",
    "Amazon India expands to tier-3 cities"
  ]
}
```

**Response (crisis detected):**
```json
{
  "urgency": "pause",
  "crisis_active": true,
  "reason": "Major flooding in multiple states with significant casualties — insensitive to post promotional content",
  "headlines_checked": 20,
  "top_headlines": [
    "Devastating floods hit Gujarat, 50+ dead",
    "Army deployed for flood rescue operations",
    "PM declares national disaster",
    "Thousands stranded in flood-hit regions",
    "Relief camps set up across 5 states"
  ]
}
```

**Crisis criteria (what triggers a BLOCK):**
- Active war or military conflict involving India
- Major natural disaster (earthquake, flood, cyclone) with significant casualties
- National mourning (death of major leader)
- Major political crisis affecting daily life
- Terrorist attack

---

### Engagement Analytics

---

#### `POST /api/social/engagement/log`

After a post is published and you have performance data, log the engagement metrics here. This data feeds the self-improving timing engine (Step 5 of the scoring algorithm). The engine needs at least 10 data points per time slot before it starts influencing scores.

**Request Body:**
```json
{
  "platform": "instagram",
  "published_at": "2026-04-06T19:00:00",
  "post_type": "reel_script",
  "event_context": "Ram Navami",
  "metrics": {
    "impressions": 5200,
    "likes": 340,
    "comments": 28,
    "shares": 15,
    "saves": 42,
    "reach": 4800
  }
}
```

**Fields:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `platform` | string | Yes | — | "facebook", "linkedin", or "instagram" |
| `published_at` | datetime | Yes | — | When the post was published |
| `post_type` | string | Yes | — | "facebook_post", "linkedin_text_post", "reel_script", etc. |
| `event_context` | string | No | null | Related event (e.g., "Diwali") |
| `metrics.impressions` | int | No | 0 | Total impressions |
| `metrics.likes` | int | No | 0 | Total likes |
| `metrics.comments` | int | No | 0 | Total comments |
| `metrics.shares` | int | No | 0 | Total shares |
| `metrics.saves` | int | No | 0 | Total saves |
| `metrics.reach` | int | No | 0 | Unique reach |

**Response:**
```json
{
  "status": "logged"
}
```

---

#### `GET /api/social/analytics/best-times/{platform}`

Returns the historically best-performing time slots based on logged engagement data. Requires at least 3 data points per slot to return results. Engagement rate = (likes + comments + shares + saves) / reach.

**Path Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `platform` | string | `facebook`, `linkedin`, or `instagram` |

**Response:**
```json
{
  "platform": "instagram",
  "best_times": [
    {
      "day": "wednesday",
      "hour": 19,
      "avg_engagement_rate": 0.0885,
      "data_points": 12
    },
    {
      "day": "friday",
      "hour": 18,
      "avg_engagement_rate": 0.0742,
      "data_points": 8
    },
    {
      "day": "sunday",
      "hour": 11,
      "avg_engagement_rate": 0.0698,
      "data_points": 5
    }
  ]
}
```

---

#### `GET /api/social/analytics/weekly-report?week_start=2026-03-30`

Engagement summary for a week compared to the previous week. Shows total posts, average engagement rate, best performing post, platform breakdown, and week-over-week change.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `week_start` | date | Current week's Monday | Start of the week (YYYY-MM-DD) |

**Response:**
```json
{
  "week_start": "2026-03-30",
  "total_posts": 12,
  "avg_engagement_rate": 0.0654,
  "best_performing_post": {
    "platform": "instagram",
    "published_at": "2026-04-01T19:00:00",
    "post_type": "reel_script",
    "event_context": null,
    "metrics": {
      "impressions": 12400,
      "likes": 890,
      "comments": 67,
      "shares": 45,
      "saves": 120,
      "reach": 11200
    }
  },
  "platform_breakdown": {
    "facebook": {
      "impressions": 8200,
      "likes": 520,
      "comments": 38,
      "shares": 22,
      "saves": 15,
      "reach": 7100
    },
    "linkedin": {
      "impressions": 4500,
      "likes": 280,
      "comments": 45,
      "shares": 30,
      "saves": 0,
      "reach": 3800
    },
    "instagram": {
      "impressions": 12400,
      "likes": 890,
      "comments": 67,
      "shares": 45,
      "saves": 120,
      "reach": 11200
    }
  },
  "vs_previous_week": "+23.1% engagement"
}
```

---

### Decision & Action Logging (Agent Transparency)

Every agent decision and content generation is automatically logged so you can audit: what post was made, on which platform, at what date/time, and what rationale the agents used.

---

#### `GET /api/social/logs/decisions`

Query the decision audit trail. Every time the timing engine scores slots, a generator creates content, or a crisis is detected — it's logged here with full rationale.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `date_start` | date | null | Filter from this date (YYYY-MM-DD) |
| `date_end` | date | null | Filter until this date |
| `platform` | string | null | Filter by platform |
| `decision_type` | string | null | One of: `timing_recommendation`, `crisis_override`, `content_generation`, `post_published`, `engagement_logged` |
| `agent_name` | string | null | Filter by agent: `timing_engine`, `facebook_generator`, `linkedin_post_generator`, `instagram_generator`, `engagement_service` |
| `limit` | int | 50 | Max results |

**Response:**
```json
{
  "decisions": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "timestamp": "2026-04-06T14:32:00",
      "decision_type": "content_generation",
      "platform": null,
      "agent_name": "facebook_generator",
      "action": "Generated 3 Facebook post variants",
      "rationale": "Topic: Amazon PPC tips, Tone: conversational, Event: Diwali",
      "input_summary": {
        "topic": "How to optimize Amazon PPC campaigns during festive season",
        "tone": "conversational",
        "event_context": "Diwali",
        "num_variants": 3
      },
      "output_summary": {
        "variant_count": 3,
        "preview": "Diwali is coming and so are the BIG sales! Here's what smart sellers..."
      },
      "event_context": "Diwali",
      "news_context": null
    }
  ],
  "count": 15
}
```

---

#### `GET /api/social/logs/posts`

Query the post publication log. Every generated post is logged with its platform, content preview, timing score, and rationale.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `date_start` | date | null | Filter from this date |
| `date_end` | date | null | Filter until this date |
| `platform` | string | null | Filter by platform |
| `post_type` | string | null | Filter by type: `facebook_post`, `linkedin_text_post`, `reel_script` |
| `limit` | int | 50 | Max results |

**Response:**
```json
{
  "posts": [
    {
      "id": "d4e5f6a7-b8c9-0123-defg-hij456789012",
      "timestamp": "2026-04-06T14:32:01",
      "platform": "facebook",
      "post_type": "facebook_post",
      "content_preview": "Diwali is coming and so are the BIG sales! Here's what smart sellers are doing to maximize their PPC returns this festive season...",
      "timing_score": 0.0,
      "timing_rationale": "Generated on demand",
      "event_context": "Diwali",
      "decision_log_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
  ],
  "count": 8
}
```

---

#### `GET /api/social/logs/decisions/{id}`

Full audit trail for a single decision — shows the decision AND all posts that were created as a result of it. This links the "why" (decision) to the "what" (posts).

**Path Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `id` | string | Decision UUID |

**Response:**
```json
{
  "decision": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-04-06T14:32:00",
    "decision_type": "content_generation",
    "agent_name": "facebook_generator",
    "action": "Generated 3 Facebook post variants",
    "rationale": "Topic: Amazon PPC tips, Tone: conversational, Event: Diwali",
    "input_summary": { ... },
    "output_summary": { ... },
    "event_context": "Diwali",
    "news_context": null
  },
  "linked_posts": [
    {
      "id": "d4e5f6a7...",
      "platform": "facebook",
      "post_type": "facebook_post",
      "content_preview": "Diwali is coming and so are the BIG sales!...",
      "decision_log_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    {
      "id": "d4e5f6a8...",
      "platform": "facebook",
      "post_type": "facebook_post",
      "content_preview": "Festive season is the BEST time to scale your Amazon PPC...",
      "decision_log_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    {
      "id": "d4e5f6a9...",
      "platform": "facebook",
      "post_type": "facebook_post",
      "content_preview": "PPC during Diwali? Here's the secret...",
      "decision_log_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
  ],
  "total_linked_posts": 3
}
```

---

#### `GET /api/social/logs/summary`

Dashboard overview — total decisions, total posts, breakdowns by type and platform, and the 10 most recent decisions and posts. Great for a quick status check.

**Response:**
```json
{
  "total_decisions": 42,
  "total_posts": 67,
  "decisions_by_type": {
    "content_generation": 25,
    "timing_recommendation": 12,
    "engagement_logged": 5
  },
  "posts_by_platform": {
    "facebook": 30,
    "linkedin": 15,
    "instagram": 22
  },
  "recent_decisions": [ ... ],
  "recent_posts": [ ... ]
}
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Separate agent** (not extending content-writer-agent) | Timing intelligence is a different concern; follows 1-agent-per-container pattern |
| **Static JSON for calendar** | Changes once/year, reviewable in git, no extra infra needed |
| **NewsAPI over Google Trends** | Clean REST API, free tier sufficient (100 req/day), graceful degradation |
| **Recommend timing, don't actually post** | Returns datetime recommendations; human/frontend decides when to publish |
| **gpt-3.5 for FB/LinkedIn, gpt-4 for Instagram Reels** | Matches existing model tiering pattern; Reels need more creative depth |
| **JSON file for logs** (not a database) | Append-only, no extra infra, sufficient for ~10-15 posts/week volume; can migrate to SQLite later |
| **Engagement feedback requires >= 10 data points** | Prevents early noise from skewing recommendations |
| **JSON-file logging** (not a logging framework) | Append-only JSON files for decisions and posts, queryable via API, full audit trail |

---

## Testing

```bash
# 1. Start the service
docker compose up social-media-agent --build

# 2. Health check
curl http://localhost:8005/health

# 3. Upcoming events
curl "http://localhost:8005/api/social/calendar/events?days_ahead=60"

# 4. Timing recommendation (around Diwali — should return "boost")
curl -X POST http://localhost:8005/api/social/timing/recommend \
  -H "Content-Type: application/json" \
  -d '{"platforms":["facebook","instagram"],"date_start":"2026-11-01","date_end":"2026-11-07","slots_per_platform":2}'

# 5. Should I post now?
curl http://localhost:8005/api/social/timing/should-post-now/instagram

# 6. Generate Facebook posts
curl -X POST http://localhost:8005/api/social/generate/facebook \
  -H "Content-Type: application/json" \
  -d '{"topic":"5 tips for new Amazon sellers","event_context":"Diwali"}'

# 7. Generate LinkedIn post + poll
curl -X POST http://localhost:8005/api/social/generate/linkedin \
  -H "Content-Type: application/json" \
  -d '{"topic":"Why A+ Content matters for D2C brands","include_poll":true}'

# 8. Generate Instagram Reel
curl -X POST http://localhost:8005/api/social/generate/instagram \
  -H "Content-Type: application/json" \
  -d '{"topic":"Amazon listing mistakes to avoid","reel_duration":30}'

# 9. Full pipeline (all platforms + timing)
curl -X POST "http://localhost:8005/api/social/generate/all?topic=Amazon+PPC+tips&event_context=Diwali"

# 10. Check decision logs
curl http://localhost:8005/api/social/logs/decisions

# 11. Check post logs
curl http://localhost:8005/api/social/logs/posts

# 12. Dashboard summary
curl http://localhost:8005/api/social/logs/summary

# 13. Swagger UI
open http://localhost:8005/docs
```
