# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SellerBuddy — a SaaS platform automating Amazon Seller Central tasks for D2C brands in India. Drupal 11 CMS backend + React 19 SPA frontend + 5 Python/FastAPI AI agent microservices + an MCP server that exposes all agents as Claude tools.

## Architecture

```
docker-compose.yml orchestrates everything on selleragent-network:

MariaDB (:3306) → Drupal 11 (:8080) ← React Frontend (:3000)
                       ↑ JSON:API
        ┌──────────────┼──────────────────────────────┐
   SEO Agent     Content Writer    Video Script    Video Generator    Social Media
    (:8001)        (:8002)           (:8003)          (:8004)           (:8005)
        └──────────────┴──────────────────────────────┘
                       ↑ stdio
                   MCP Server (mcp-server/server.py)
```

All AI agents follow the same structure: `ai-agents/<name>/` with `Dockerfile`, `requirements.txt`, `src/main.py`, `src/agents/`, `src/models/`, `src/services/`.

## Build & Run Commands

```bash
# Full stack
docker compose up -d
docker compose down

# Single agent (with rebuild)
docker compose up social-media-agent --build
docker compose up seo-agent --build

# Drupal
docker exec selleragent-drupal drush cr          # cache rebuild
docker exec selleragent-drupal drush cex -y      # config export

# Frontend
cd seller-frontend && npm run dev                # Vite dev server (port 3000)
cd seller-frontend && npm run build

# MCP server (local, not containerized)
cd mcp-server && pip install -e . && python server.py
```

No test framework, linter, or CI pipeline is configured.

## Key Patterns

**Lazy singletons** — Every `main.py` uses `_service = None` globals with `get_service()` factory functions that instantiate on first call. New services must follow this pattern.

**Model tiering** — `OPENAI_MODEL` (gpt-4-turbo-preview) for generation/creative tasks, `OPENAI_FAST_MODEL` (gpt-3.5-turbo) for classification/simpler tasks. Set via env vars.

**LLM response parsing** — All agents use `_strip_fences()` regex to remove markdown code fences from LLM JSON output, then `json.loads()`. Use `SystemMessage`/`HumanMessage` directly (not `ChatPromptTemplate`).

**Drupal integration** — Agents push content via JSON:API with basic auth. Each agent has its own `DrupalClient` in `src/services/drupal_client.py`. Inside Docker, Drupal is at `http://drupal:80`.

**Agent logging** — Social Media Agent uses append-only JSON files (`data/decision_log.json`, `data/post_log.json`, `data/engagement_log.json`) for audit trail. Every agent action logs via `agent_logger.log_decision()`.

**Graceful degradation** — Inter-agent HTTP calls (e.g., Social Media → SEO Agent) must handle connection errors, timeouts, and return `None`/`[]` with a warning rather than failing.

**Docker volume mounts** — `src/` directories are mounted for hot-reload during development. Changes to Python files take effect without rebuilding.

## Service Details

| Service | Port | Key Endpoints |
|---------|------|---------------|
| SEO Agent | 8001 | `POST /api/seo/weekly-run`, `POST /api/seo/generate-outline`, `POST /api/seo/push-to-drupal` |
| Content Writer | 8002 | `POST /api/content/write-blog`, `/linkedin-carousel`, `/tweet-thread`, `/full-pipeline` |
| Video Script | 8003 | `POST /api/video/youtube-script`, `/shorts-hooks` |
| Video Generator | 8004 | `POST /api/video/generate` (async job), `GET /api/video/job/{id}/status` |
| Social Media | 8005 | `POST /api/social/generate/weekly-content`, `/facebook`, `/linkedin`, `/instagram`, timing + calendar + engagement + logging endpoints |

## Environment Variables

Copy `.env.example` to `.env` and add:
- `OPENAI_API_KEY` — required by SEO, Content Writer, Video Script, Social Media agents
- `GOOGLE_GENAI_API_KEY` + `GOOGLE_APPLICATION_CREDENTIALS` — Video Generator (Veo)
- `ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID` — Video Generator (TTS)
- `GSC_SERVICE_ACCOUNT_JSON` — SEO Agent (Google Search Console)
- `NEWS_API_KEY` — Social Media Agent (crisis detection)

## Drupal Backend

Custom modules in `seller-backend/web/modules/custom/`:
- `selleragent_core` — route access, core hooks
- `selleragent_api` — REST API endpoints
- `selleragent_trial` — trial signup
- `selleragent_migrate` — content seeding

Setup scripts: `seller-backend/scripts/install-drupal.sh`, `seed-content.php`, `setup-content-architecture.php`

## Frontend

React 19 + Vite + Tailwind + shadcn/ui with wouter for routing. Vite proxies `/api`, `/user`, `/session` to Drupal. Source in `seller-frontend/`.

## MCP Tools: code-review-graph

This project has a knowledge graph. Use code-review-graph MCP tools BEFORE Grep/Glob/Read for exploring the codebase. The graph gives structural context (callers, dependents, test coverage).

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes (risk-scored) |
| `get_review_context` | Need source snippets for review |
| `get_impact_radius` | Understanding blast radius of a change |
| `query_graph` | Tracing callers, callees, imports, tests |
| `semantic_search_nodes` | Finding functions/classes by keyword |
| `get_architecture_overview` | High-level codebase structure |

Fall back to Grep/Glob/Read only when the graph doesn't cover what you need.
