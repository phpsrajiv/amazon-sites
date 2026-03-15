# SellerAgent AI - Drupal 11 Content Strategy

## Overview

This document outlines the complete Drupal 11 backend content architecture for the **SellerAgent AI** SaaS landing page. The frontend is a React (Vite) SPA that consumes content via Drupal's JSON:API. All page content, media, menus, and configuration will be managed through Drupal's admin UI and served as structured API responses.

---

## 1. Custom Content Types

### 1.1 `landing_page` (Landing Page)

The main page node that ties all sections together.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Page title (e.g., "SellerAgent AI - Home")      |
| `field_meta_description`   | Text (plain, long)  | SEO meta description                            |
| `field_og_image`           | Entity reference    | Media reference for Open Graph image            |

### 1.2 `hero_slide` (Hero Carousel Slide)

Individual slides for the hero image carousel.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Slide heading (e.g., "Ship Smarter. Sell More.")|
| `field_slide_tag`          | Text (plain)        | Badge/tag text (e.g., "AMAZON FULFILLMENT")     |
| `field_slide_description`  | Text (plain, long)  | Slide body text                                 |
| `field_slide_image`        | Entity reference    | Media (Image) reference                         |
| `field_slide_weight`       | Integer             | Sort order / weight                             |

### 1.3 `stat_card` (Statistics Card)

Trust/metrics cards displayed under the hero.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Stat label (e.g., "Sellers Served")             |
| `field_stat_value`         | Text (plain)        | Display value (e.g., "12,000+")                 |
| `field_stat_prefix`        | Text (plain)        | Optional prefix (e.g., "$")                     |
| `field_stat_suffix`        | Text (plain)        | Optional suffix (e.g., "+", "B+")               |
| `field_stat_icon`          | Text (plain)        | Icon identifier (e.g., "users", "trending-up")  |
| `field_stat_weight`        | Integer             | Sort order                                      |

### 1.4 `pain_point` (Problem / Pain Point)

Cards in the "Problems" section.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Problem title (e.g., "Ad Spend Waste")          |
| `field_pain_description`   | Text (plain, long)  | Problem description                             |
| `field_pain_icon`          | Text (plain)        | Icon identifier                                 |
| `field_pain_weight`        | Integer             | Sort order                                      |

### 1.5 `feature` (Feature)

Feature cards displayed in the features section.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Feature name (e.g., "Autopilot Campaign Engine")|
| `field_feature_description`| Text (plain, long)  | Feature body text                               |
| `field_feature_bullets`    | Text (plain, long)  | Pipe-separated bullet points                    |
| `field_feature_icon`       | Text (plain)        | Icon identifier                                 |
| `field_feature_category`   | List (text)         | Category: "core" or "advanced"                  |
| `field_feature_weight`     | Integer             | Sort order                                      |

### 1.6 `audience_type` (Audience / Persona)

"Built for Every Amazon Business" audience cards.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Audience label (e.g., "For Sellers")            |
| `field_audience_description`| Text (plain, long) | Audience benefit description                    |
| `field_audience_icon`      | Text (plain)        | Icon identifier                                 |
| `field_audience_weight`    | Integer             | Sort order                                      |

### 1.7 `onboarding_step` (How It Works Step)

Steps in the "How it Works" section.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Step title (e.g., "Connect Your Amazon Store")  |
| `field_step_number`        | Integer             | Step number (1, 2, 3)                           |
| `field_step_description`   | Text (plain, long)  | Step description                                |
| `field_step_icon`          | Text (plain)        | Icon identifier                                 |

### 1.8 `testimonial` (Testimonial)

Customer testimonials/reviews.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Review headline / quote summary                 |
| `field_testimonial_body`   | Text (plain, long)  | Full testimonial text                           |
| `field_testimonial_author` | Text (plain)        | Author name                                     |
| `field_testimonial_role`   | Text (plain)        | Author role (e.g., "Deputy Manager")            |
| `field_testimonial_company`| Text (plain)        | Company name                                    |
| `field_testimonial_avatar` | Entity reference    | Media (Image) reference for avatar              |
| `field_testimonial_rating` | Integer             | Star rating (1-5)                               |
| `field_testimonial_weight` | Integer             | Sort order                                      |

### 1.9 `pricing_plan` (Pricing Plan)

Pricing tier cards.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Plan name (e.g., "Starter", "Pro", "Agency")   |
| `field_plan_subtitle`      | Text (plain)        | Subtitle (e.g., "Perfect for individual sellers")|
| `field_plan_price`         | Decimal             | Monthly price (e.g., 29.00)                     |
| `field_plan_currency`      | Text (plain)        | Currency symbol (e.g., "$")                     |
| `field_plan_billing_period`| Text (plain)        | Billing period label (e.g., "/mo")              |
| `field_plan_features`      | Text (plain, long)  | Pipe-separated feature list                     |
| `field_plan_cta_text`      | Text (plain)        | CTA button text (e.g., "Start Free Trial")      |
| `field_plan_cta_url`       | Link                | CTA button URL                                  |
| `field_plan_highlighted`   | Boolean             | Whether this is the "MOST POPULAR" plan         |
| `field_plan_badge`         | Text (plain)        | Badge text (e.g., "MOST POPULAR")               |
| `field_plan_weight`        | Integer             | Sort order                                      |

### 1.10 `result_metric` (Results / Proof Metric)

Metrics in the "Proven Results" strip.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Metric label (e.g., "Revenue Increase")         |
| `field_metric_value`       | Text (plain)        | Display value (e.g., "218%")                    |
| `field_metric_icon`        | Text (plain)        | Icon identifier                                 |
| `field_metric_weight`      | Integer             | Sort order                                      |

### 1.11 `cta_section` (Call to Action Section)

Reusable CTA blocks (hero CTA, final CTA).

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | CTA heading                                     |
| `field_cta_subheading`     | Text (plain, long)  | CTA subheading / description                    |
| `field_cta_badge`          | Text (plain)        | Badge text above heading                        |
| `field_cta_primary_text`   | Text (plain)        | Primary button text                             |
| `field_cta_primary_url`    | Link                | Primary button URL                              |
| `field_cta_secondary_text` | Text (plain)        | Secondary button text                           |
| `field_cta_secondary_url`  | Link                | Secondary button URL                            |

### 1.12 `blog_post` (Blog Post)

Blog articles displayed on the `/blog` listing and individual post pages.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `title`                    | Text (core)         | Blog post title                                 |
| `field_blog_body`          | Text (formatted, long) | Full blog HTML content                       |
| `field_blog_summary`       | Text (plain, long)  | Short excerpt for listing cards                 |
| `field_blog_image`         | Text (plain)        | Featured image URL/path                         |
| `field_blog_author`        | Text (plain)        | Author name                                     |
| `field_blog_category`      | Text (plain)        | Category label (e.g., "PPC Strategy", "AI & Technology") |
| `field_blog_date`          | Text (plain)        | Display date string (e.g., "March 10, 2026")    |
| `field_blog_weight`        | Integer             | Sort order                                      |

---

## 2. Block Types (Custom Block Types)

### 2.1 `trust_badge_block`

Trust indicators shown near the hero section.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `field_badge_icon`         | Text (plain)        | Icon identifier                                 |
| `field_badge_text`         | Text (plain)        | Badge text (e.g., "Verified by Amazon")         |

### 2.2 `section_header_block`

Reusable section headers with tag + heading + subheading.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `field_section_tag`        | Text (plain)        | Section tag/badge text                          |
| `field_section_heading`    | Text (plain)        | Main heading                                    |
| `field_section_subheading` | Text (plain, long)  | Supporting text                                 |

### 2.3 `dashboard_mockup_block`

Data for the mock dashboard preview in hero area.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `field_mockup_acos_label`  | Text (plain)        | ACoS improvement label                          |
| `field_mockup_acos_value`  | Text (plain)        | ACoS improvement value                          |
| `field_mockup_actions`     | Text (plain, long)  | JSON string of autopilot action items            |
| `field_mockup_chart_data`  | Text (plain, long)  | JSON string of revenue chart data               |
| `field_mockup_chat_query`  | Text (plain)        | AI chat sample question                         |
| `field_mockup_chat_answer` | Text (plain, long)  | AI chat sample response                         |

### 2.4 `setup_step_block`

Feature highlight cards in the "Easy Setup" section sidebar.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `field_setup_feature_name` | Text (plain)        | Feature name (e.g., "Autopilot Engine")         |
| `field_setup_feature_stat` | Text (plain)        | Live stat text                                  |
| `field_setup_feature_icon` | Text (plain)        | Icon identifier                                 |
| `field_setup_live_badge`   | Boolean             | Show "LIVE" badge                               |
| `field_setup_weight`       | Integer             | Sort order                                      |

---

## 3. Media Types

### 3.1 `image` (Core - Image)
Standard Drupal image media type. Used for:
- Hero carousel slide backgrounds
- Testimonial author avatars
- OG/social sharing images

### 3.2 `icon` (Custom - SVG Icon)

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `field_icon_svg`           | File (svg)          | SVG file upload                                 |
| `field_icon_identifier`    | Text (plain)        | Machine name / identifier for frontend mapping  |

### 3.3 `brand_asset` (Custom - Brand Asset)

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `field_brand_file`         | File                | Logo, favicon, or brand image file              |
| `field_brand_type`         | List (text)         | Type: "logo", "favicon", "og_image"             |
| `field_brand_variant`      | List (text)         | Variant: "light", "dark", "icon_only"           |

---

## 4. Taxonomy Vocabularies

### 4.1 `feature_category`
Categorize features for filtering and grouping.
- Terms: `Core Features`, `Advanced Features`, `AI-Powered`, `Reporting`

### 4.2 `audience_type`
Target audience classification.
- Terms: `Individual Sellers`, `Brands`, `Agencies`

### 4.3 `pricing_tier`
Pricing tier labels for cross-referencing.
- Terms: `Starter`, `Pro`, `Agency`

---

## 5. User Profile Fields

These fields extend the default Drupal user entity for trial signups and admin users.

| Field Machine Name         | Field Type          | Description                                     |
|----------------------------|---------------------|-------------------------------------------------|
| `field_full_name`          | Text (plain)        | User's full name                                |
| `field_amazon_store_url`   | Link                | Amazon store URL (optional)                     |
| `field_trial_status`       | List (text)         | Trial status: "pending", "active", "expired"    |
| `field_trial_started`      | Timestamp           | Trial start date                                |
| `field_user_type`          | Entity reference    | Reference to `audience_type` taxonomy           |
| `field_company_name`       | Text (plain)        | Company/brand name                              |

---

## 6. Menu Structure

### 6.1 `main-navigation` (Main Navigation)
Header navigation links - anchor links for SPA smooth scrolling.

| Title          | Link / Path         | Weight |
|----------------|---------------------|--------|
| Features       | `#features`         | 1      |
| How it Works   | `#how-it-works`     | 2      |
| Testimonials   | `#testimonials`     | 3      |
| Pricing        | `#pricing`          | 4      |
| Blog           | `/blog`             | 5      |

### 6.2 `footer-product` (Footer - Product Column)

| Title          | Link / Path         | Weight |
|----------------|---------------------|--------|
| Features       | `/features`         | 1      |
| Pricing        | `/pricing`          | 2      |
| Case Studies   | `/case-studies`     | 3      |
| API Docs       | `/api-docs`         | 4      |

### 6.3 `footer-company` (Footer - Company Column)

| Title          | Link / Path         | Weight |
|----------------|---------------------|--------|
| About Us       | `/about`            | 1      |
| Blog           | `/blog`             | 2      |
| Careers        | `/careers`          | 3      |
| Contact Support| `/contact`          | 4      |

### 6.4 `footer-legal` (Footer - Legal Links)

| Title            | Link / Path         | Weight |
|------------------|---------------------|--------|
| Privacy Policy   | `/privacy-policy`   | 1      |
| Terms of Service | `/terms-of-service` | 2      |

---

## 7. Site Configuration (via Drupal Config)

### 7.1 `site_settings` (Custom Config Entity or Simple Config)

Global site settings managed via a custom settings form.

| Setting Key                  | Type     | Description                                |
|------------------------------|----------|--------------------------------------------|
| `site_name`                  | String   | "SellerAgent AI"                           |
| `site_tagline`               | String   | Site tagline / slogan                      |
| `copyright_text`             | String   | Footer copyright text                      |
| `copyright_year`             | String   | Copyright year                             |
| `social_twitter_url`         | String   | Twitter/X profile URL                      |
| `social_linkedin_url`        | String   | LinkedIn profile URL                       |
| `social_facebook_url`        | String   | Facebook page URL                          |
| `google_analytics_id`        | String   | GA tracking ID                             |

---

## 8. JSON:API Endpoints (Auto-generated)

Drupal's JSON:API module automatically exposes all content types. The React frontend will consume these endpoints:

| Resource                   | Endpoint                                        | Purpose                         |
|----------------------------|--------------------------------------------------|---------------------------------|
| Hero Slides                | `GET /jsonapi/node/hero_slide?sort=field_slide_weight` | Hero carousel data       |
| Stat Cards                 | `GET /jsonapi/node/stat_card?sort=field_stat_weight`   | Trust metrics            |
| Pain Points                | `GET /jsonapi/node/pain_point?sort=field_pain_weight`  | Problem cards            |
| Features                   | `GET /jsonapi/node/feature?sort=field_feature_weight`  | Feature cards            |
| Audience Types             | `GET /jsonapi/node/audience_type?sort=field_audience_weight` | Audience personas  |
| Onboarding Steps           | `GET /jsonapi/node/onboarding_step?sort=field_step_number`   | How it works steps |
| Testimonials               | `GET /jsonapi/node/testimonial?sort=field_testimonial_weight`| Customer reviews   |
| Pricing Plans              | `GET /jsonapi/node/pricing_plan?sort=field_plan_weight`      | Pricing tiers      |
| Result Metrics             | `GET /jsonapi/node/result_metric?sort=field_metric_weight`   | Proof metrics      |
| CTA Sections               | `GET /jsonapi/node/cta_section`                              | CTA blocks         |
| Main Menu                  | `GET /jsonapi/menu_items/main-navigation`                    | Header nav links   |
| Footer Menus               | `GET /jsonapi/menu_items/footer-product`                     | Footer links       |
| Trial Signup (custom)      | `POST /api/v1/trial-signup`                                  | Trial form submit  |
| Site Settings (custom)     | `GET /api/v1/site-settings`                                  | Global config      |

---

## 9. Contributed Modules

| Module                     | Purpose                                                     |
|----------------------------|-------------------------------------------------------------|
| `jsonapi`                  | Core module - REST API for decoupled frontend (core in D11) |
| `jsonapi_extras`           | Customize JSON:API resource names, field aliases, disable resources |
| `jsonapi_menu_items`       | Expose menu trees as JSON:API resources                     |
| `cors`                     | Cross-Origin Resource Sharing (configure via services.yml)  |
| `restui`                   | Admin UI to manage REST resources                           |
| `token`                    | Token replacement system (used by Pathauto, Metatag)        |
| `pathauto`                 | Automatic URL alias generation                              |
| `metatag`                  | SEO meta tags management                                    |
| `simple_sitemap`           | XML sitemap generation                                      |
| `admin_toolbar`            | Enhanced admin toolbar for content management               |
| `admin_toolbar_tools`      | Extra tools for admin toolbar                               |
| `field_group`              | Group fields in content edit forms for better UX             |
| `paragraphs`               | Flexible content composition (for future page builder)      |
| `webform`                  | Form builder for trial signup & contact forms                |
| `config_split`             | Split config between environments (dev, staging, prod)       |
| `environment_indicator`    | Visual indicator of current environment                     |
| `redirect`                 | URL redirect management                                     |
| `stage_file_proxy`         | Proxy remote files in dev environments                      |
| `smtp` or `symfony_mailer` | Email delivery configuration                                |
| `consumer_image_styles`    | Expose image styles via JSON:API                            |
| `next`                     | (Optional) Next.js / decoupled integration helpers          |
| `subrequests`              | Batch multiple JSON:API requests into one                   |
| `jsonapi_include`          | Automatically include related resources                     |
| `simple_oauth`             | OAuth2 for authenticated API access (trial signup, etc.)     |

---

## 10. Custom Modules

### 10.1 `selleragent_core`

Core custom module for site-wide functionality.

**Responsibilities:**
- Install/update hooks for content type creation
- Custom permissions
- Route access control (blocks direct `/node/{nid}` browsing for non-admin roles via `RouteSubscriber`)
- Event subscribers
- Service definitions

### 10.2 `selleragent_api`

Custom REST API endpoints beyond JSON:API.

**Endpoints:**
- `POST /api/v1/trial-signup` - Trial registration (creates user + sends welcome email)
- `GET /api/v1/site-settings` - Global site settings (name, social links, copyright)
- `GET /api/v1/landing-page` - Aggregated landing page data (all sections in one response)
- `GET /api/v1/blogs` - All published blog posts sorted by weight
- `GET /api/v1/blog/{nid}` - Single blog post by node ID

**Why custom endpoints?**
- The aggregated landing page endpoint reduces the frontend from ~10 API calls to 1
- Trial signup requires custom logic (user creation, email, validation)
- Site settings aren't standard nodes

### 10.3 `selleragent_trial`

Trial signup and management module.

**Responsibilities:**
- Trial signup form processing and validation
- User account creation with trial role
- Welcome email dispatch
- Trial expiry cron job
- Trial status tracking

### 10.4 `selleragent_migrate`

Content migration / seed data module.

**Responsibilities:**
- Migration YAML configs for seeding initial content
- Drush commands for importing/resetting demo content
- Default content for all content types (hero slides, features, pricing, etc.)

---

## 11. User Roles and Permissions

| Role             | Description                          | Key Permissions                              |
|------------------|--------------------------------------|----------------------------------------------|
| `anonymous`      | Unauthenticated visitors             | View published content via API/JSON:API only (direct `/node/{nid}` blocked) |
| `authenticated`  | Logged-in users                      | Basic profile access                         |
| `trial_user`     | Free trial users                     | Authenticated + trial dashboard access       |
| `content_editor` | Content management staff             | CRUD all content types, manage media         |
| `site_admin`     | Full site administration             | All content_editor + config, users, modules  |
| `administrator`  | Superadmin                           | Full access                                  |

---

## 12. Image Styles

| Style Name           | Machine Name            | Effects                              | Usage                    |
|----------------------|-------------------------|--------------------------------------|--------------------------|
| Hero Slide           | `hero_slide`            | Scale & crop 1400x600               | Hero carousel images     |
| Hero Slide Mobile    | `hero_slide_mobile`     | Scale & crop 800x500                | Hero carousel (mobile)   |
| Testimonial Avatar   | `testimonial_avatar`    | Scale & crop 80x80, circle          | Testimonial avatars      |
| OG Image             | `og_image`              | Scale & crop 1200x630               | Social sharing           |
| Thumbnail            | `thumbnail`             | Scale 150x150                        | Admin listings           |
| Brand Logo           | `brand_logo`            | Scale width 200                      | Header/footer logo       |

---

## 13. Views (Content Lists)

These Drupal Views serve as admin content management interfaces.

| View Name              | Path                      | Purpose                              |
|------------------------|---------------------------|--------------------------------------|
| Content Dashboard      | `/admin/content-dashboard`| Overview of all content by type      |
| Hero Slides Manager    | `/admin/hero-slides`      | Manage hero carousel slides          |
| Features Manager       | `/admin/features`         | Manage feature cards                 |
| Testimonials Manager   | `/admin/testimonials`     | Manage customer testimonials         |
| Pricing Plans Manager  | `/admin/pricing-plans`    | Manage pricing tiers                 |
| Trial Users            | `/admin/trial-users`      | View and manage trial signups        |

---

## 14. Content Workflow

### Publishing Workflow (using Content Moderation)
- **Draft** → Content is being created/edited
- **Review** → Content pending approval
- **Published** → Content is live and served via API
- **Archived** → Content removed from API but not deleted

---

## 15. CORS Configuration

File: `sites/default/services.yml`

```yaml
cors.config:
  enabled: true
  allowedHeaders:
    - 'content-type'
    - 'authorization'
    - 'x-csrf-token'
  allowedMethods:
    - 'GET'
    - 'POST'
    - 'OPTIONS'
  allowedOrigins:
    - 'http://localhost:3000'
    - 'https://selleragent.ai'
  exposedHeaders: true
  maxAge: 3600
  supportsCredentials: true
```

---

## 16. Caching Strategy

| Layer               | Technology              | TTL        | Purpose                           |
|---------------------|-------------------------|------------|------------------------------------|
| Drupal Page Cache   | Internal Page Cache     | 15 min     | Full page caching for anon users  |
| Drupal Dynamic Cache| Dynamic Page Cache      | Auto       | Cached render arrays              |
| JSON:API Cache      | Cache tags              | Auto       | Auto-invalidation on content save |
| Frontend Cache      | React Query             | 5 min      | Client-side stale-while-revalidate|
| CDN (Production)    | CloudFront / Cloudflare | 1 hour     | Edge caching for static assets    |

---

## 17. Environment Architecture

```
┌─────────────────────────────────────────────────┐
│                 Docker Compose                   │
├──────────────────┬──────────────────────────────┤
│                  │                              │
│  seller-frontend │       seller-backend         │
│  (React/Vite)    │       (Drupal 11)            │
│  Port: 3000      │       Port: 8080             │
│                  │                              │
│  Node 20 Alpine  │  PHP 8.3 + Apache            │
│                  │  MariaDB 11                  │
│                  │  Composer                     │
│                  │                              │
└──────────────────┴──────────────────────────────┘
```

---

## 18. Directory Structure (seller-backend)

```
seller-backend/
├── docker-compose.yml          # Unified Docker setup
├── Dockerfile.drupal           # Drupal container
├── Dockerfile.frontend         # Frontend container
├── drupal/                     # Drupal project root
│   ├── composer.json
│   ├── composer.lock
│   ├── web/
│   │   ├── modules/custom/
│   │   │   ├── selleragent_core/
│   │   │   ├── selleragent_api/
│   │   │   ├── selleragent_trial/
│   │   │   └── selleragent_migrate/
│   │   ├── themes/custom/
│   │   │   └── selleragent_admin/  (optional admin theme tweaks)
│   │   └── sites/default/
│   │       ├── settings.php
│   │       └── services.yml
│   └── config/sync/               # Exported Drupal config
├── mariadb/
│   └── init/                       # DB initialization scripts
└── .env                            # Environment variables
```

---

## 19. API Response Example

### Aggregated Landing Page Endpoint

`GET /api/v1/landing-page`

```json
{
  "hero_slides": [
    {
      "id": "1",
      "tag": "AMAZON FULFILLMENT",
      "heading": "Ship Smarter. Sell More.",
      "description": "AI-driven inventory and fulfillment insights...",
      "image_url": "/sites/default/files/hero-slide-1.jpg"
    }
  ],
  "stats": [
    { "label": "Sellers Served", "value": "12,000+", "icon": "users" }
  ],
  "pain_points": [...],
  "features": [...],
  "audience_types": [...],
  "onboarding_steps": [...],
  "testimonials": [...],
  "pricing_plans": [...],
  "result_metrics": [...],
  "cta_sections": [...],
  "menus": {
    "main_navigation": [...],
    "footer_product": [...],
    "footer_company": [...],
    "footer_legal": [...]
  },
  "site_settings": {
    "site_name": "SellerAgent AI",
    "copyright_text": "2026 SellerAgent AI. All rights reserved.",
    "social_links": {...}
  }
}
```

---

## 20. Implementation Priority

| Phase | Tasks                                                    | Priority |
|-------|----------------------------------------------------------|----------|
| 1     | Drupal install, Docker setup, JSON:API + CORS config     | Critical |
| 2     | Create all content types, fields, taxonomies             | Critical |
| 3     | Custom modules: `selleragent_core`, `selleragent_api`    | High     |
| 4     | Seed demo content via `selleragent_migrate`              | High     |
| 5     | Trial signup module (`selleragent_trial`)                | High     |
| 6     | Image styles, media types, Views admin dashboards        | Medium   |
| 7     | Content moderation workflow, roles, permissions          | Medium   |
| 8     | SEO (Metatag, Pathauto, Sitemap), caching optimization   | Low      |
| 9     | Frontend API integration (replace mocked data)           | High     |

---

## 21. Content Export (Single Content Sync)

All Drupal content has been exported successfully using the `single_content_sync` module. The zip contains **80 files** covering all content:

- **16 block_content** — trust badges (3), section headers (8), dashboard mockup (1), setup steps (4)
- **14 menu_link_content** — all menu links
- **40 nodes** — hero slides (3), stat cards (4), pain points (4), features (6), audience types (3), onboarding steps (3), testimonials (3), pricing plans (3), result metrics (4), CTA sections (2), landing page (1), blog posts (4)
- **10 taxonomy_terms** — feature categories (4), audience segments (3), pricing tiers (3)

The export is saved at:

- **Container**: `/opt/drupal/web/scs-export/content-bulk-export-15_03_2026-05_07.zip`
- **Host**: `/Users/rajiv/amazon-sites/seller-backend/drupal/scs-export/content-bulk-export-15_03_2026-05_07.zip`

This zip can be used to re-import all content on a fresh Drupal install using `drush content:import`.

---

## 22. SEO & Online Marketing

### 22.1 Drupal Modules Enabled

| Module | Purpose |
|--------|---------|
| `metatag` | Global meta tag management with token support |
| `metatag_open_graph` | Open Graph tags (og:title, og:description, og:image, etc.) |
| `metatag_twitter_cards` | Twitter Cards (twitter:card, twitter:title, twitter:image) |
| `simple_sitemap` | XML sitemap generation at `/sitemap.xml` |
| `pathauto` | Automatic URL alias patterns |

### 22.2 Metatag Defaults

- **Global**: Site name, default OG and Twitter Card tags using Drupal tokens
- **Node**: Article-specific OG type, title, summary, and image tokens
- **Front Page**: Homepage-specific title, description, and OG image

### 22.3 API SEO Data

Both the landing page and blog post API endpoints return an `seo` object:

**`/api/v1/landing-page`** returns:
```json
{
  "seo": {
    "title": "SellerAgent AI | AI-Powered Amazon Advertising Automation",
    "description": "...",
    "og_image": "/opengraph.jpg",
    "og_type": "website"
  }
}
```

**`/api/v1/blog/{nid}`** returns:
```json
{
  "seo": {
    "title": "Post Title | SellerAgent AI Blog",
    "description": "...",
    "og_title": "Post Title",
    "og_type": "article",
    "og_image": "...",
    "twitter_card": "summary_large_image",
    "article_author": "...",
    "article_published_time": "...",
    "article_section": "..."
  }
}
```

### 22.4 Frontend SEO (react-helmet-async)

- **`<HelmetProvider>`** wraps the app in `main.tsx`
- **`<SEO>` component** (`src/components/SEO.tsx`) renders `<Helmet>` with all meta tags, OG, Twitter Cards, canonical URL, and optional JSON-LD structured data
- Each page renders `<SEO>` with page-specific props:
  - **Home**: Organization JSON-LD, default OG tags
  - **Blog listing**: Blog-specific title and description
  - **Blog post**: Dynamic title, description, `og:type=article`, article metadata, BlogPosting JSON-LD
  - **Not Found**: `noindex` robots directive

### 22.5 Structured Data (JSON-LD)

- **Homepage**: `Organization` schema (name, url, logo, sameAs)
- **Blog posts**: `BlogPosting` schema (headline, author, datePublished, publisher, image, articleSection)

### 22.6 Additional SEO Files

| File | Purpose |
|------|---------|
| `public/robots.txt` | Allows all crawlers, links to sitemap |
| Vite proxy `/sitemap.xml` | Proxies sitemap requests to Drupal backend |

### 22.7 Google Tag Manager

- GTM placeholder added to `index.html` (commented out with `GTM-XXXXXXX`)
- `usePageTracking` hook (`src/hooks/use-page-tracking.ts`) pushes virtual pageview events to `window.dataLayer` on every SPA route change
- To activate: replace `GTM-XXXXXXX` with actual container ID and uncomment the script tags
