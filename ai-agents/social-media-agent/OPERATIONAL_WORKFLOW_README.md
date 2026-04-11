## Operational Flow: Automatic vs Manual

### Automated (Cron-Scheduled) APIs

These APIs should run on a schedule without human intervention:

| # | API | Frequency | When | Purpose |
|---|-----|-----------|------|---------|
| 1 | `POST /api/social/timing/weekly-schedule` | Weekly | **Every Monday 6:00 AM IST** | Generate the week's posting calendar — best time slots for each platform for the next 7 days |
| 2 | `GET /api/social/news/sentiment` | 3x daily | **8:00 AM, 1:00 PM, 6:00 PM IST** | Check for crisis/negative sentiment before posting windows. If crisis detected, all scheduled posts should be held |
| 3 | `GET /api/social/timing/should-post-now/{platform}` | Before each post | **Triggered 30 min before each scheduled slot** | Final go/no-go check. Confirms the slot is still good (news might have changed since morning) |

**Typical automated weekly flow:**
```
Monday 6:00 AM  →  POST /api/social/timing/weekly-schedule
                    Returns 21 slots (7 days × 3 platforms)
                    Example: "Instagram Wed 7pm, LinkedIn Thu 9am, Facebook Fri 2pm"

Before each slot →  GET /api/social/news/sentiment
                    If crisis_active=true → SKIP this slot, notify team

30 min before   →  GET /api/social/timing/should-post-now/instagram
                    If should_post=true → proceed to publish
                    If should_post=false → defer to next recommended slot
```

---

### Semi-Automated (Triggered by Cron, but Requires Human Review)

These generate content that a human should review before publishing:

| # | API | Frequency | When | Purpose |
|---|-----|-----------|------|---------|
| 4 | `POST /api/social/generate/all` | Weekly | **Every Monday 7:00 AM IST** (after timing schedule is ready) | Generate content for all 3 platforms for the week's topics. Human reviews, edits if needed, approves for publishing |
| 5 | `POST /api/social/generate/facebook` | As needed | When a specific Facebook post needs regeneration or a new topic comes up mid-week | Generate Facebook-specific variants |
| 6 | `POST /api/social/generate/linkedin` | As needed | When a specific LinkedIn post needs regeneration | Generate LinkedIn post + poll |
| 7 | `POST /api/social/generate/instagram` | As needed | When a specific Reel script needs regeneration | Generate Reel script + caption |

**Suggested weekly content pipeline:**
```
Monday 6:00 AM  →  Cron: Generate weekly schedule (timing)
Monday 7:00 AM  →  Cron: Generate all content (POST /api/social/generate/all)
                    ↓
                    Content goes to a review queue (Drupal draft / Slack notification)
                    ↓
Monday-Tuesday  →  Human reviews & approves posts for the week
                    ↓
Wed-Sun         →  Posts go live at scheduled times (after should-post-now check)
```

---

### Manual APIs (Called by Human / Frontend)

These are on-demand APIs you call when you need them:

| # | API | When to Call | Who Calls |
|---|-----|-------------|-----------|
| 8 | `POST /api/social/calendar/events` | When you have a brand event, product launch, or custom sale to add | Marketing team / Admin |
| 9 | `GET /api/social/calendar/events?days_ahead=30` | When planning content for upcoming weeks | Content planner |
| 10 | `GET /api/social/calendar/year/2026` | Annual planning session | Marketing lead |
| 11 | `POST /api/social/timing/recommend` | When you want to find the best time for a specific campaign (e.g., "When should I post about my product launch next week?") | Content planner |
| 12 | `POST /api/social/engagement/log` | After each post is published and you have metrics (typically 24-48 hours post-publish) | Manual or via platform webhook |
| 13 | `GET /api/social/analytics/best-times/{platform}` | Monthly review to see which time slots are actually performing best | Marketing lead |
| 14 | `GET /api/social/analytics/weekly-report` | Weekly performance review | Marketing lead |
| 15 | `GET /api/social/logs/decisions` | When you want to understand why a certain post was generated or timing was recommended | Anyone auditing agent behaviour |
| 16 | `GET /api/social/logs/posts` | When you want to see what content was generated, on which platform, when | Content reviewer |
| 17 | `GET /api/social/logs/decisions/{id}` | When investigating a specific decision's full chain (decision → posts) | Debugging / Audit |
| 18 | `GET /api/social/logs/summary` | Quick dashboard check — how many decisions, posts, breakdown by platform | Daily check |

---

### The Complete Weekly Cycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MONDAY (Planning Day)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  6:00 AM [CRON]  POST /api/social/timing/weekly-schedule            │
│                  → Generates 21 posting slots for the week          │
│                                                                     │
│  7:00 AM [CRON]  POST /api/social/generate/all                     │
│                  → Generates Facebook + LinkedIn + Instagram        │
│                    content for 2-3 topics                           │
│                                                                     │
│  8:00 AM [CRON]  GET /api/social/news/sentiment                    │
│                  → Morning crisis check                             │
│                                                                     │
│  9:00 AM [HUMAN] Review generated content in Drupal drafts         │
│                  → Edit, approve, or regenerate specific posts      │
│                  → If a Facebook post needs rework:                 │
│                    POST /api/social/generate/facebook               │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                    TUESDAY - SUNDAY (Execution)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  8:00 AM  [CRON] GET /api/social/news/sentiment                    │
│  1:00 PM  [CRON] GET /api/social/news/sentiment                    │
│  6:00 PM  [CRON] GET /api/social/news/sentiment                    │
│                  → If crisis detected: pause all scheduled posts    │
│                                                                     │
│  Before each scheduled post:                                        │
│  [CRON]  GET /api/social/timing/should-post-now/{platform}         │
│          → Final go/no-go                                           │
│          → If YES: publish the approved content                     │
│          → If NO: defer to next slot                                │
│                                                                     │
│  After each published post (24-48 hrs later):                       │
│  [HUMAN] POST /api/social/engagement/log                           │
│          → Log impressions, likes, comments, shares, saves, reach  │
│          → This feeds Step 5 of the timing algorithm               │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                    FRIDAY (Weekly Review)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [HUMAN] GET /api/social/analytics/weekly-report                   │
│          → Compare this week vs last week                           │
│          → Check avg engagement rate, best performing post          │
│                                                                     │
│  [HUMAN] GET /api/social/analytics/best-times/{platform}           │
│          → Are real engagement patterns matching our timing recs?   │
│                                                                     │
│  [HUMAN] GET /api/social/logs/summary                              │
│          → Quick audit: how many decisions, posts, per platform     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Self-Improving Loop (Gets Smarter Over Time)

```
Week 1-4:   Timing based on static peak windows only (Steps 1-4)
            → Instagram 6-9pm, LinkedIn 8-10am, Facebook 1-4pm

Week 5+:    Engagement data accumulates (10+ data points per slot)
            → Step 5 kicks in
            → "Your audience actually engages more at 8pm than 7pm on Instagram"
            → Timing scores auto-adjust

Month 3+:   Enough data to see patterns
            → GET /api/social/analytics/best-times/instagram
            → Shows data-driven best times, may differ from defaults
            → System self-corrects without manual intervention
```

---

### What You Need to Set Up Next

1. **Cron jobs** — To automate the scheduled API calls (weekly schedule, content generation, news checks). This can be done via:
   - A simple cron container in Docker
   - An external scheduler (GitHub Actions, AWS EventBridge)
   - A frontend timer/scheduler

2. **Engagement logging pipeline** — Currently manual (`POST /api/social/engagement/log`). Future improvement: connect to Facebook Graph API / LinkedIn API / Instagram API to auto-pull metrics.

3. **Notification system** — When crisis is detected or content is ready for review, send a Slack/email notification.
