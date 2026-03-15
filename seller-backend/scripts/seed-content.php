<?php

/**
 * @file
 * Seeds all Drupal content from the React frontend data.
 *
 * Run with: drush php:script seed-content.php
 */

use Drupal\node\Entity\Node;
use Drupal\block_content\Entity\BlockContent;

echo "\n=============================================\n";
echo "  SellerAgent AI — Seeding Content           \n";
echo "=============================================\n\n";

// ============================================================
// 1. HERO SLIDES
// ============================================================
echo "=== 1. HERO SLIDES ===\n";

$slides = [
  [
    'title' => 'Ship Smarter. Sell More.',
    'field_slide_tag' => 'Amazon Fulfillment',
    'field_slide_description' => 'AI-driven inventory and fulfillment insights keep you ahead of demand.',
    'field_slide_weight' => 0,
  ],
  [
    'title' => 'Data That Drives Decisions.',
    'field_slide_tag' => 'Real-Time Analytics',
    'field_slide_description' => 'Crystal-clear dashboards with SKU-level insights and live campaign performance.',
    'field_slide_weight' => 1,
  ],
  [
    'title' => 'Ads That Optimize Themselves.',
    'field_slide_tag' => 'PPC Autopilot',
    'field_slide_description' => 'Let AI adjust bids, pause waste, and scale winners — 24/7, automatically.',
    'field_slide_weight' => 2,
  ],
];

foreach ($slides as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'hero_slide', 'title' => $data['title']]);
  if (!empty($existing)) {
    echo "  [skip] '{$data['title']}'\n";
    continue;
  }
  $node = Node::create(['type' => 'hero_slide', 'status' => 1] + $data);
  $node->save();
  echo "  [ok] Created hero slide: '{$data['title']}'\n";
}

// ============================================================
// 2. STAT CARDS
// ============================================================
echo "\n=== 2. STAT CARDS ===\n";

$stats = [
  ['title' => 'Sellers Trust Us', 'field_stat_value' => '12,000+', 'field_stat_prefix' => '', 'field_stat_suffix' => '', 'field_stat_icon' => 'users', 'field_stat_weight' => 0],
  ['title' => 'Ad Spend Managed', 'field_stat_value' => '$5.4B+', 'field_stat_prefix' => '', 'field_stat_suffix' => '', 'field_stat_icon' => 'trending-up', 'field_stat_weight' => 1],
  ['title' => 'Avg. Revenue Increase', 'field_stat_value' => '218%', 'field_stat_prefix' => '', 'field_stat_suffix' => '', 'field_stat_icon' => 'bar-chart', 'field_stat_weight' => 2],
  ['title' => 'Saved Per Week', 'field_stat_value' => '10hrs', 'field_stat_prefix' => '', 'field_stat_suffix' => '', 'field_stat_icon' => 'clock', 'field_stat_weight' => 3],
];

foreach ($stats as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'stat_card', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'stat_card', 'status' => 1] + $data)->save();
  echo "  [ok] Created stat card: '{$data['title']}'\n";
}

// ============================================================
// 3. PAIN POINTS
// ============================================================
echo "\n=== 3. PAIN POINTS ===\n";

$pain_points = [
  ['title' => 'Ad Spend Going to Waste', 'field_pain_description' => 'PPC campaigns bleed money daily without real-time AI bid adjustments and budget reallocation.', 'field_pain_icon' => 'trending-down', 'field_pain_weight' => 0],
  ['title' => 'Manual Keyword Research', 'field_pain_description' => 'Hours wasted searching for winning keywords while competitors are already capturing that traffic.', 'field_pain_icon' => 'search-x', 'field_pain_weight' => 1],
  ['title' => 'Poor Listing Performance', 'field_pain_description' => 'Weak titles, bullets, and descriptions cost you ranking, visibility, and conversions.', 'field_pain_icon' => 'alert-triangle', 'field_pain_weight' => 2],
  ['title' => 'No Time to Optimize', 'field_pain_description' => 'Managing bids, campaigns, and listings manually is a full-time job — you need a co-pilot.', 'field_pain_icon' => 'clock', 'field_pain_weight' => 3],
];

foreach ($pain_points as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'pain_point', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'pain_point', 'status' => 1] + $data)->save();
  echo "  [ok] Created pain point: '{$data['title']}'\n";
}

// ============================================================
// 4. FEATURES
// ============================================================
echo "\n=== 4. FEATURES ===\n";

$features = [
  [
    'title' => 'Autopilot Campaign Engine',
    'field_feature_description' => 'Our AI optimization engine adjusts bids, reallocates budgets, and fixes underperformance — automatically, every single day.',
    'field_feature_bullets' => 'Daily bid & budget adjustments|Pauses wasteful keywords|Works 24/7 with learning-based improvements',
    'field_feature_icon' => 'zap',
    'field_feature_category' => 'core',
    'field_feature_weight' => 0,
  ],
  [
    'title' => 'Agentic AI Chatbot',
    'field_feature_description' => 'Ask campaign questions, get data-backed answers, and trigger real actions — all through natural language chat.',
    'field_feature_bullets' => '"Why is my ACoS high?" — Get live answers|"Pause bad keywords" — AI executes instantly|"Launch campaign for top 5 ASINs" — Done in chat',
    'field_feature_icon' => 'brain-circuit',
    'field_feature_category' => 'core',
    'field_feature_weight' => 1,
  ],
  [
    'title' => 'AI Listing Builder',
    'field_feature_description' => 'Create perfectly optimized product listings with titles, bullets, and descriptions tuned for Amazon\'s A9 algorithm.',
    'field_feature_bullets' => 'SEO-optimized titles & bullets|A+ content generation|Competitor-aware copywriting',
    'field_feature_icon' => 'pen-tool',
    'field_feature_category' => 'core',
    'field_feature_weight' => 2,
  ],
  [
    'title' => 'Keyword Intelligence',
    'field_feature_description' => 'Discover high-converting keywords your competitors are missing and rank your products faster across all categories.',
    'field_feature_bullets' => 'Search volume & trend data|Competitor keyword gaps|Negative keyword suggestions',
    'field_feature_icon' => 'key',
    'field_feature_category' => 'advanced',
    'field_feature_weight' => 3,
  ],
  [
    'title' => 'Advanced Reporting',
    'field_feature_description' => 'Crystal-clear, real-time dashboards with SKU-level insights, agency white-label reports, and bulk actions.',
    'field_feature_bullets' => 'SKU-level profit analytics|White-labeled client reports|Bulk campaign management',
    'field_feature_icon' => 'bar-chart-3',
    'field_feature_category' => 'advanced',
    'field_feature_weight' => 4,
  ],
  [
    'title' => 'Dayparting & Scheduling',
    'field_feature_description' => 'Run ads smarter by automatically adjusting budgets and bids based on peak shopping hours and your best-performing times.',
    'field_feature_bullets' => 'Hour-by-hour bid scheduling|Peak-hour budget boosts|Automatic off-peak savings',
    'field_feature_icon' => 'clock',
    'field_feature_category' => 'advanced',
    'field_feature_weight' => 5,
  ],
];

foreach ($features as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'feature', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'feature', 'status' => 1] + $data)->save();
  echo "  [ok] Created feature: '{$data['title']}'\n";
}

// ============================================================
// 5. AUDIENCE TYPES
// ============================================================
echo "\n=== 5. AUDIENCE TYPES ===\n";

$audiences = [
  ['title' => 'For Sellers', 'field_audience_description' => 'You focus on your products. We\'ll take care of your ads — automatically, 24/7, with zero guesswork.', 'field_audience_icon' => 'sparkles', 'field_audience_weight' => 0],
  ['title' => 'For Brands', 'field_audience_description' => 'You need visibility, structure, and ROI. Our AI gives you all three with brand-level campaign control.', 'field_audience_icon' => 'target', 'field_audience_weight' => 1],
  ['title' => 'For Agencies', 'field_audience_description' => 'Clients get better results and your team gets its time back. Multi-account dashboards, white-label reports, bulk actions.', 'field_audience_icon' => 'users', 'field_audience_weight' => 2],
];

foreach ($audiences as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'audience_type', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'audience_type', 'status' => 1] + $data)->save();
  echo "  [ok] Created audience type: '{$data['title']}'\n";
}

// ============================================================
// 6. ONBOARDING STEPS
// ============================================================
echo "\n=== 6. ONBOARDING STEPS ===\n";

$steps = [
  ['title' => 'Connect Your Amazon Store', 'field_step_number' => 1, 'field_step_description' => 'Sync your Amazon Ads account in 60 seconds. Secure. Seamless. No complex setup, no learning curve.', 'field_step_icon' => 'link-2'],
  ['title' => 'Set Goals & Let AI Optimize', 'field_step_number' => 2, 'field_step_description' => 'Select your budget and ACoS targets. Our Autopilot Engine tailors campaigns and adjusts bids every day.', 'field_step_icon' => 'bar-chart-3'],
  ['title' => 'Watch Revenue Grow', 'field_step_number' => 3, 'field_step_description' => 'AI scales winning campaigns, pauses wasteful keywords, and reallocates budget — on autopilot, 24/7.', 'field_step_icon' => 'rocket'],
];

foreach ($steps as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'onboarding_step', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'onboarding_step', 'status' => 1] + $data)->save();
  echo "  [ok] Created onboarding step: '{$data['title']}'\n";
}

// ============================================================
// 7. TESTIMONIALS
// ============================================================
echo "\n=== 7. TESTIMONIALS ===\n";

$testimonials = [
  [
    'title' => 'Cerin Pathrose Review',
    'field_testimonial_body' => 'I have been using SellerAgent AI for more than a year. I am in love with their AI tool that helps us continuously grow on Amazon. Their autopilot alone is worth every dollar!',
    'field_testimonial_author' => 'Cerin Pathrose',
    'field_testimonial_role' => 'Deputy Manager',
    'field_testimonial_company' => 'Nitta Gelatin India Ltd.',
    'field_testimonial_rating' => 5,
    'field_testimonial_weight' => 0,
  ],
  [
    'title' => 'Natesan Chandrasekaran Review',
    'field_testimonial_body' => 'Ever since SellerAgent AI started managing our ads, we\'ve had a great improvement in sales. Ad spend is now controlled and orders are generating much more than when we were running ads ourselves.',
    'field_testimonial_author' => 'Natesan Chandrasekaran',
    'field_testimonial_role' => 'Founder',
    'field_testimonial_company' => 'The Slime Space',
    'field_testimonial_rating' => 5,
    'field_testimonial_weight' => 1,
  ],
  [
    'title' => 'Jahanvi Bhalla Review',
    'field_testimonial_body' => 'Very good service and it has helped me boost my Amazon sales tremendously. It\'s been a productive collaboration and I\'ve already renewed my subscription. Highly recommend!',
    'field_testimonial_author' => 'Jahanvi Bhalla',
    'field_testimonial_role' => 'Founder',
    'field_testimonial_company' => 'FloofYou Pet Care & Supplies',
    'field_testimonial_rating' => 5,
    'field_testimonial_weight' => 2,
  ],
];

foreach ($testimonials as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'testimonial', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'testimonial', 'status' => 1] + $data)->save();
  echo "  [ok] Created testimonial: '{$data['title']}'\n";
}

// ============================================================
// 8. PRICING PLANS
// ============================================================
echo "\n=== 8. PRICING PLANS ===\n";

$plans = [
  [
    'title' => 'Starter',
    'field_plan_subtitle' => 'Perfect for individual sellers',
    'field_plan_price' => '29.00',
    'field_plan_currency' => '$',
    'field_plan_billing_period' => '/mo',
    'field_plan_features' => '5 products / ASINs|AI Listing Builder|Keyword Research|Basic Autopilot Campaigns|Standard Reporting',
    'field_plan_cta_text' => 'Start Free Trial',
    'field_plan_highlighted' => FALSE,
    'field_plan_badge' => '',
    'field_plan_weight' => 0,
  ],
  [
    'title' => 'Pro',
    'field_plan_subtitle' => 'For growing brands & power sellers',
    'field_plan_price' => '79.00',
    'field_plan_currency' => '$',
    'field_plan_billing_period' => '/mo',
    'field_plan_features' => '25 products / ASINs|Everything in Starter|A+ Content Generation|Full Autopilot Engine + Dayparting|Competitor Analysis|Agentic AI Chatbot',
    'field_plan_cta_text' => 'Start Free Trial',
    'field_plan_highlighted' => TRUE,
    'field_plan_badge' => 'Most Popular',
    'field_plan_weight' => 1,
  ],
  [
    'title' => 'Agency',
    'field_plan_subtitle' => 'For agencies managing multiple clients',
    'field_plan_price' => '199.00',
    'field_plan_currency' => '$',
    'field_plan_billing_period' => '/mo',
    'field_plan_features' => 'Unlimited ASINs & accounts|Everything in Pro|Multi-account dashboard|White-labeled client reports|Bulk campaign actions|Priority support + API access',
    'field_plan_cta_text' => 'Start Free Trial',
    'field_plan_highlighted' => FALSE,
    'field_plan_badge' => '',
    'field_plan_weight' => 2,
  ],
];

foreach ($plans as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'pricing_plan', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'pricing_plan', 'status' => 1] + $data)->save();
  echo "  [ok] Created pricing plan: '{$data['title']}'\n";
}

// ============================================================
// 9. RESULT METRICS
// ============================================================
echo "\n=== 9. RESULT METRICS ===\n";

$metrics = [
  ['title' => 'Average Revenue Increase', 'field_metric_value' => '218%', 'field_metric_icon' => 'trending-up', 'field_metric_weight' => 0],
  ['title' => 'Average Order Increase', 'field_metric_value' => '269%', 'field_metric_icon' => 'bar-chart', 'field_metric_weight' => 1],
  ['title' => 'Saved Per Week', 'field_metric_value' => '10hrs', 'field_metric_icon' => 'clock', 'field_metric_weight' => 2],
  ['title' => 'Average ACoS Reduction', 'field_metric_value' => '-38%', 'field_metric_icon' => 'trending-down', 'field_metric_weight' => 3],
];

foreach ($metrics as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'result_metric', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'result_metric', 'status' => 1] + $data)->save();
  echo "  [ok] Created result metric: '{$data['title']}'\n";
}

// ============================================================
// 10. CTA SECTIONS
// ============================================================
echo "\n=== 10. CTA SECTIONS ===\n";

$ctas = [
  [
    'title' => 'Hero CTA',
    'field_cta_subheading' => 'Run, optimize, and scale your Amazon campaigns with AI-powered precision, agentic AI, real-time optimizations, and crystal-clear reporting — so you never waste a dollar or a second.',
    'field_cta_badge' => 'Now with Agentic AI — Ask, Analyze & Act in one chat',
    'field_cta_primary_text' => 'Get a Free Audit Report',
    'field_cta_secondary_text' => 'Request a Demo',
  ],
  [
    'title' => 'Final CTA',
    'field_cta_subheading' => 'Join thousands of sellers who stopped guessing and started growing. Book a free audit today — no commitment, no credit card.',
    'field_cta_badge' => 'Verified by Amazon · Trusted by 12,000+ Sellers',
    'field_cta_primary_text' => 'Get a Free Audit Report',
    'field_cta_secondary_text' => 'Request a Demo',
  ],
];

foreach ($ctas as $data) {
  $existing = \Drupal::entityTypeManager()->getStorage('node')
    ->loadByProperties(['type' => 'cta_section', 'title' => $data['title']]);
  if (!empty($existing)) { echo "  [skip] '{$data['title']}'\n"; continue; }
  Node::create(['type' => 'cta_section', 'status' => 1] + $data)->save();
  echo "  [ok] Created CTA section: '{$data['title']}'\n";
}

// ============================================================
// 11. LANDING PAGE (master node)
// ============================================================
echo "\n=== 11. LANDING PAGE ===\n";

$existing = \Drupal::entityTypeManager()->getStorage('node')
  ->loadByProperties(['type' => 'landing_page', 'title' => 'SellerAgent AI - Home']);
if (empty($existing)) {
  Node::create([
    'type' => 'landing_page',
    'title' => 'SellerAgent AI - Home',
    'field_meta_description' => 'Supercharge your Amazon business with AI-powered ad optimization, autopilot campaigns, agentic AI chatbot, and advanced reporting. Trusted by 12,000+ sellers.',
    'status' => 1,
  ])->save();
  echo "  [ok] Created landing page.\n";
} else {
  echo "  [skip] Landing page already exists.\n";
}

// ============================================================
// 12. BLOCK CONTENT
// ============================================================
echo "\n=== 12. BLOCK CONTENT ===\n";

// Trust badges
$trust_badges = [
  ['field_badge_icon' => 'shield-check', 'field_badge_text' => 'Verified by Amazon'],
  ['field_badge_icon' => 'zap', 'field_badge_text' => 'Setup in 60 seconds'],
  ['field_badge_icon' => 'trending-up', 'field_badge_text' => 'Trusted by 12,000+ sellers'],
];

foreach ($trust_badges as $i => $data) {
  $info = $data['field_badge_text'];
  $existing = \Drupal::entityTypeManager()->getStorage('block_content')
    ->loadByProperties(['type' => 'trust_badge_block', 'info' => "Trust Badge: $info"]);
  if (!empty($existing)) { echo "  [skip] Trust badge: '$info'\n"; continue; }
  BlockContent::create([
    'type' => 'trust_badge_block',
    'info' => "Trust Badge: $info",
  ] + $data)->save();
  echo "  [ok] Created trust badge: '$info'\n";
}

// Section headers
$headers = [
  [
    'info' => 'Section: Problems',
    'field_section_tag' => '',
    'field_section_heading' => 'Running Amazon Ads Shouldn\'t Feel Like a Gamble.',
    'field_section_subheading' => 'Without intelligent automation, you\'re constantly fighting algorithms, overspending on ads, and losing ground to competitors who have AI working for them.',
  ],
  [
    'info' => 'Section: Easy Setup',
    'field_section_tag' => 'Meet SellerAgent AI — Your Amazon Ads Co-Pilot',
    'field_section_heading' => 'Easy Setup. Instant Results.',
    'field_section_subheading' => 'Get started without tech headaches. Connect your Amazon account, set your goals, and let SellerAgent AI do the heavy lifting — no complex setup, no learning curve.',
  ],
  [
    'info' => 'Section: Features',
    'field_section_tag' => '',
    'field_section_heading' => 'Everything You Need to Dominate Amazon Ads',
    'field_section_subheading' => 'A complete AI-powered suite built specifically for Amazon sellers, brands, and agencies who want real results — not just dashboards.',
  ],
  [
    'info' => 'Section: Audience',
    'field_section_tag' => '',
    'field_section_heading' => 'Built for Every Amazon Business',
    'field_section_subheading' => 'From 1 store to 100 — SellerAgent AI fits your workflow.',
  ],
  [
    'info' => 'Section: Results',
    'field_section_tag' => '',
    'field_section_heading' => 'Proven Results from Businesses Like Yours',
    'field_section_subheading' => '',
  ],
  [
    'info' => 'Section: How It Works',
    'field_section_tag' => '',
    'field_section_heading' => 'Get Started in 3 Simple Steps',
    'field_section_subheading' => 'No tech headaches. No learning curve. Just results.',
  ],
  [
    'info' => 'Section: Testimonials',
    'field_section_tag' => '',
    'field_section_heading' => 'Trusted by 12,000+ Happy Sellers, Brands & Agencies',
    'field_section_subheading' => 'Verified by Amazon · Real results, real sellers',
  ],
  [
    'info' => 'Section: Pricing',
    'field_section_tag' => '',
    'field_section_heading' => 'Simple, Transparent Pricing',
    'field_section_subheading' => 'Start free. Scale as you grow. No hidden fees.',
  ],
];

foreach ($headers as $data) {
  $info = $data['info'];
  $existing = \Drupal::entityTypeManager()->getStorage('block_content')
    ->loadByProperties(['type' => 'section_header_block', 'info' => $info]);
  if (!empty($existing)) { echo "  [skip] Section header: '$info'\n"; continue; }
  BlockContent::create([
    'type' => 'section_header_block',
  ] + $data)->save();
  echo "  [ok] Created section header: '$info'\n";
}

// Dashboard mockup
$existing = \Drupal::entityTypeManager()->getStorage('block_content')
  ->loadByProperties(['type' => 'dashboard_mockup_block', 'info' => 'Hero Dashboard Mockup']);
if (empty($existing)) {
  BlockContent::create([
    'type' => 'dashboard_mockup_block',
    'info' => 'Hero Dashboard Mockup',
    'field_mockup_acos_label' => 'ACoS Improvement',
    'field_mockup_acos_value' => '-38%',
    'field_mockup_actions' => json_encode([
      ['label' => 'Bid adjustments', 'value' => '1,284'],
      ['label' => 'Keywords paused', 'value' => '47'],
      ['label' => 'Budget reallocated', 'value' => '$842'],
      ['label' => 'Ad spend saved', 'value' => '$312'],
    ]),
    'field_mockup_chart_data' => json_encode([
      ['name' => 'Mon', 'score' => 45],
      ['name' => 'Tue', 'score' => 52],
      ['name' => 'Wed', 'score' => 67],
      ['name' => 'Thu', 'score' => 70],
      ['name' => 'Fri', 'score' => 82],
      ['name' => 'Sat', 'score' => 91],
      ['name' => 'Sun', 'score' => 98],
    ]),
    'field_mockup_chat_query' => 'Why is my ACoS high on ASIN B08XYZ?',
    'field_mockup_chat_answer' => 'High bids on 3 broad keywords. Pausing now...',
  ])->save();
  echo "  [ok] Created dashboard mockup block.\n";
} else {
  echo "  [skip] Dashboard mockup already exists.\n";
}

// Setup step blocks
$setup_steps = [
  ['info' => 'Setup: Autopilot Engine', 'field_setup_feature_name' => 'Autopilot Engine', 'field_setup_feature_stat' => '1,284 bid adjustments today', 'field_setup_feature_icon' => 'zap', 'field_setup_live_badge' => TRUE, 'field_setup_weight' => 0],
  ['info' => 'Setup: Budget Reallocator', 'field_setup_feature_name' => 'Budget Reallocator', 'field_setup_feature_stat' => 'Moved $842 to top ASINs', 'field_setup_feature_icon' => 'bar-chart-3', 'field_setup_live_badge' => FALSE, 'field_setup_weight' => 1],
  ['info' => 'Setup: Agentic AI Chat', 'field_setup_feature_name' => 'Agentic AI Chat', 'field_setup_feature_stat' => '47 wasteful keywords paused', 'field_setup_feature_icon' => 'brain-circuit', 'field_setup_live_badge' => FALSE, 'field_setup_weight' => 2],
  ['info' => 'Setup: Agency Dashboard', 'field_setup_feature_name' => 'Agency Dashboard', 'field_setup_feature_stat' => '12 client accounts synced', 'field_setup_feature_icon' => 'users', 'field_setup_live_badge' => FALSE, 'field_setup_weight' => 3],
];

foreach ($setup_steps as $data) {
  $info = $data['info'];
  $existing = \Drupal::entityTypeManager()->getStorage('block_content')
    ->loadByProperties(['type' => 'setup_step_block', 'info' => $info]);
  if (!empty($existing)) { echo "  [skip] Setup step: '$info'\n"; continue; }
  BlockContent::create([
    'type' => 'setup_step_block',
  ] + $data)->save();
  echo "  [ok] Created setup step: '$info'\n";
}

// ============================================================
// DONE
// ============================================================

// Count everything
$counts = [];
$node_types = ['hero_slide', 'stat_card', 'pain_point', 'feature', 'audience_type', 'onboarding_step', 'testimonial', 'pricing_plan', 'result_metric', 'cta_section', 'landing_page'];
foreach ($node_types as $type) {
  $count = \Drupal::entityTypeManager()->getStorage('node')->getQuery()
    ->condition('type', $type)->accessCheck(FALSE)->count()->execute();
  $counts[$type] = $count;
}
$block_count = \Drupal::entityTypeManager()->getStorage('block_content')->getQuery()
  ->accessCheck(FALSE)->count()->execute();

echo "\n=============================================\n";
echo "  CONTENT SEEDING COMPLETE                   \n";
echo "=============================================\n\n";
echo "Node counts:\n";
foreach ($counts as $type => $count) {
  echo "  $type: $count\n";
}
echo "  block_content: $block_count\n";
echo "\nTotal nodes: " . array_sum($counts) . "\n";
echo "Total blocks: $block_count\n";
