<?php

/**
 * @file
 * SellerBuddy - Complete Drupal content architecture setup.
 *
 * Run with: drush php:script scripts/setup-content-architecture.php
 */

use Drupal\node\Entity\NodeType;
use Drupal\field\Entity\FieldStorageConfig;
use Drupal\field\Entity\FieldConfig;
use Drupal\taxonomy\Entity\Vocabulary;
use Drupal\taxonomy\Entity\Term;
use Drupal\block_content\Entity\BlockContentType;
use Drupal\media\Entity\MediaType;
use Drupal\image\Entity\ImageStyle;
use Drupal\image\ImageStyleInterface;
use Drupal\system\Entity\Menu;
use Drupal\menu_link_content\Entity\MenuLinkContent;
use Drupal\user\Entity\Role;

// ============================================================
// HELPER FUNCTIONS
// ============================================================

function sa_create_content_type(string $id, string $label, string $description): void {
  if (NodeType::load($id)) {
    echo "  [skip] Content type '$id' already exists.\n";
    return;
  }
  $type = NodeType::create([
    'type' => $id,
    'name' => $label,
    'description' => $description,
    'display_submitted' => FALSE,
  ]);
  $type->save();
  // Create default form and view display.
  \Drupal::service('entity_display.repository')->getFormDisplay('node', $id)->save();
  \Drupal::service('entity_display.repository')->getViewDisplay('node', $id)->save();
  echo "  [ok] Created content type '$id'.\n";
}

function sa_create_field_storage(string $entity_type, string $field_name, string $type, array $settings = []): void {
  if (FieldStorageConfig::loadByName($entity_type, $field_name)) {
    return; // Already exists.
  }
  $config = [
    'field_name' => $field_name,
    'entity_type' => $entity_type,
    'type' => $type,
    'cardinality' => 1,
  ];
  if (!empty($settings)) {
    $config['settings'] = $settings;
  }
  FieldStorageConfig::create($config)->save();
}

function sa_create_field_instance(string $entity_type, string $bundle, string $field_name, string $label, array $settings = [], bool $required = FALSE): void {
  if (FieldConfig::loadByName($entity_type, $bundle, $field_name)) {
    return; // Already exists.
  }
  $config = [
    'field_name' => $field_name,
    'entity_type' => $entity_type,
    'bundle' => $bundle,
    'label' => $label,
    'required' => $required,
  ];
  if (!empty($settings)) {
    $config['settings'] = $settings;
  }
  FieldConfig::create($config)->save();
}

function sa_add_text_field(string $entity_type, string $bundle, string $field_name, string $label, bool $required = FALSE): void {
  sa_create_field_storage($entity_type, $field_name, 'string');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label, [], $required);
}

function sa_add_text_long_field(string $entity_type, string $bundle, string $field_name, string $label, bool $required = FALSE): void {
  sa_create_field_storage($entity_type, $field_name, 'string_long');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label, [], $required);
}

function sa_add_integer_field(string $entity_type, string $bundle, string $field_name, string $label, bool $required = FALSE): void {
  sa_create_field_storage($entity_type, $field_name, 'integer');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label, [], $required);
}

function sa_add_decimal_field(string $entity_type, string $bundle, string $field_name, string $label, bool $required = FALSE): void {
  sa_create_field_storage($entity_type, $field_name, 'decimal');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label, [], $required);
}

function sa_add_boolean_field(string $entity_type, string $bundle, string $field_name, string $label): void {
  sa_create_field_storage($entity_type, $field_name, 'boolean');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label);
}

function sa_add_link_field(string $entity_type, string $bundle, string $field_name, string $label): void {
  sa_create_field_storage($entity_type, $field_name, 'link');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label);
}

function sa_add_list_string_field(string $entity_type, string $bundle, string $field_name, string $label, array $allowed_values, bool $required = FALSE): void {
  sa_create_field_storage($entity_type, $field_name, 'list_string', [
    'allowed_values' => $allowed_values,
  ]);
  sa_create_field_instance($entity_type, $bundle, $field_name, $label, [], $required);
}

function sa_add_entity_reference_field(string $entity_type, string $bundle, string $field_name, string $label, string $target_type, array $target_bundles = []): void {
  sa_create_field_storage($entity_type, $field_name, 'entity_reference', [
    'target_type' => $target_type,
  ]);
  $handler_settings = [];
  if (!empty($target_bundles)) {
    $handler_settings['target_bundles'] = array_combine($target_bundles, $target_bundles);
  }
  sa_create_field_instance($entity_type, $bundle, $field_name, $label, [
    'handler' => 'default',
    'handler_settings' => $handler_settings,
  ]);
}

function sa_add_timestamp_field(string $entity_type, string $bundle, string $field_name, string $label): void {
  sa_create_field_storage($entity_type, $field_name, 'timestamp');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label);
}

function sa_add_file_field(string $entity_type, string $bundle, string $field_name, string $label, array $extensions = ['txt']): void {
  sa_create_field_storage($entity_type, $field_name, 'file');
  sa_create_field_instance($entity_type, $bundle, $field_name, $label, [
    'file_extensions' => implode(' ', $extensions),
  ]);
}

// ============================================================
// 1. CONTENT TYPES
// ============================================================

echo "\n=== 1. CREATING CONTENT TYPES ===\n";

// 1.1 Landing Page
sa_create_content_type('landing_page', 'Landing Page', 'Main page node that ties all sections together.');
sa_add_text_long_field('node', 'landing_page', 'field_meta_description', 'Meta Description');
sa_add_entity_reference_field('node', 'landing_page', 'field_og_image', 'OG Image', 'media', ['image']);

// 1.2 Hero Slide
sa_create_content_type('hero_slide', 'Hero Carousel Slide', 'Individual slides for the hero image carousel.');
sa_add_text_field('node', 'hero_slide', 'field_slide_tag', 'Slide Tag', TRUE);
sa_add_text_long_field('node', 'hero_slide', 'field_slide_description', 'Slide Description', TRUE);
sa_add_entity_reference_field('node', 'hero_slide', 'field_slide_image', 'Slide Image', 'media', ['image']);
sa_add_integer_field('node', 'hero_slide', 'field_slide_weight', 'Sort Order');

// 1.3 Stat Card
sa_create_content_type('stat_card', 'Statistics Card', 'Trust/metrics cards displayed under the hero.');
sa_add_text_field('node', 'stat_card', 'field_stat_value', 'Value', TRUE);
sa_add_text_field('node', 'stat_card', 'field_stat_prefix', 'Prefix');
sa_add_text_field('node', 'stat_card', 'field_stat_suffix', 'Suffix');
sa_add_text_field('node', 'stat_card', 'field_stat_icon', 'Icon');
sa_add_integer_field('node', 'stat_card', 'field_stat_weight', 'Sort Order');

// 1.4 Pain Point
sa_create_content_type('pain_point', 'Problem / Pain Point', 'Cards in the Problems section.');
sa_add_text_long_field('node', 'pain_point', 'field_pain_description', 'Description', TRUE);
sa_add_text_field('node', 'pain_point', 'field_pain_icon', 'Icon');
sa_add_integer_field('node', 'pain_point', 'field_pain_weight', 'Sort Order');

// 1.5 Feature
sa_create_content_type('feature', 'Feature', 'Feature cards displayed in the features section.');
sa_add_text_long_field('node', 'feature', 'field_feature_description', 'Description', TRUE);
sa_add_text_long_field('node', 'feature', 'field_feature_bullets', 'Bullet Points (pipe-separated)');
sa_add_text_field('node', 'feature', 'field_feature_icon', 'Icon');
sa_add_list_string_field('node', 'feature', 'field_feature_category', 'Category', [
  'core' => 'Core',
  'advanced' => 'Advanced',
]);
sa_add_integer_field('node', 'feature', 'field_feature_weight', 'Sort Order');

// 1.6 Audience Type
sa_create_content_type('audience_type', 'Audience / Persona', '"Built for Every Amazon Business" audience cards.');
sa_add_text_long_field('node', 'audience_type', 'field_audience_description', 'Description', TRUE);
sa_add_text_field('node', 'audience_type', 'field_audience_icon', 'Icon');
sa_add_integer_field('node', 'audience_type', 'field_audience_weight', 'Sort Order');

// 1.7 Onboarding Step
sa_create_content_type('onboarding_step', 'How It Works Step', 'Steps in the How it Works section.');
sa_add_integer_field('node', 'onboarding_step', 'field_step_number', 'Step Number', TRUE);
sa_add_text_long_field('node', 'onboarding_step', 'field_step_description', 'Description', TRUE);
sa_add_text_field('node', 'onboarding_step', 'field_step_icon', 'Icon');

// 1.8 Testimonial
sa_create_content_type('testimonial', 'Testimonial', 'Customer testimonials/reviews.');
sa_add_text_long_field('node', 'testimonial', 'field_testimonial_body', 'Testimonial Text', TRUE);
sa_add_text_field('node', 'testimonial', 'field_testimonial_author', 'Author Name', TRUE);
sa_add_text_field('node', 'testimonial', 'field_testimonial_role', 'Author Role');
sa_add_text_field('node', 'testimonial', 'field_testimonial_company', 'Company');
sa_add_entity_reference_field('node', 'testimonial', 'field_testimonial_avatar', 'Avatar', 'media', ['image']);
sa_add_integer_field('node', 'testimonial', 'field_testimonial_rating', 'Star Rating (1-5)');
sa_add_integer_field('node', 'testimonial', 'field_testimonial_weight', 'Sort Order');

// 1.9 Pricing Plan
sa_create_content_type('pricing_plan', 'Pricing Plan', 'Pricing tier cards.');
sa_add_text_field('node', 'pricing_plan', 'field_plan_subtitle', 'Subtitle', TRUE);
sa_add_decimal_field('node', 'pricing_plan', 'field_plan_price', 'Monthly Price', TRUE);
sa_add_text_field('node', 'pricing_plan', 'field_plan_currency', 'Currency Symbol');
sa_add_text_field('node', 'pricing_plan', 'field_plan_billing_period', 'Billing Period');
sa_add_text_long_field('node', 'pricing_plan', 'field_plan_features', 'Features (pipe-separated)');
sa_add_text_field('node', 'pricing_plan', 'field_plan_cta_text', 'CTA Button Text');
sa_add_link_field('node', 'pricing_plan', 'field_plan_cta_url', 'CTA Button URL');
sa_add_boolean_field('node', 'pricing_plan', 'field_plan_highlighted', 'Highlighted (Most Popular)');
sa_add_text_field('node', 'pricing_plan', 'field_plan_badge', 'Badge Text');
sa_add_integer_field('node', 'pricing_plan', 'field_plan_weight', 'Sort Order');

// 1.10 Result Metric
sa_create_content_type('result_metric', 'Results / Proof Metric', 'Metrics in the Proven Results strip.');
sa_add_text_field('node', 'result_metric', 'field_metric_value', 'Value', TRUE);
sa_add_text_field('node', 'result_metric', 'field_metric_icon', 'Icon');
sa_add_integer_field('node', 'result_metric', 'field_metric_weight', 'Sort Order');

// 1.11 CTA Section
sa_create_content_type('cta_section', 'Call to Action Section', 'Reusable CTA blocks (hero CTA, final CTA).');
sa_add_text_long_field('node', 'cta_section', 'field_cta_subheading', 'Subheading');
sa_add_text_field('node', 'cta_section', 'field_cta_badge', 'Badge Text');
sa_add_text_field('node', 'cta_section', 'field_cta_primary_text', 'Primary Button Text');
sa_add_link_field('node', 'cta_section', 'field_cta_primary_url', 'Primary Button URL');
sa_add_text_field('node', 'cta_section', 'field_cta_secondary_text', 'Secondary Button Text');
sa_add_link_field('node', 'cta_section', 'field_cta_secondary_url', 'Secondary Button URL');

echo "  Content types done.\n";

// ============================================================
// 2. CUSTOM BLOCK TYPES
// ============================================================

echo "\n=== 2. CREATING BLOCK TYPES ===\n";

$block_types = [
  'trust_badge_block' => 'Trust Badge Block',
  'section_header_block' => 'Section Header Block',
  'dashboard_mockup_block' => 'Dashboard Mockup Block',
  'setup_step_block' => 'Setup Step Block',
];

foreach ($block_types as $id => $label) {
  if (BlockContentType::load($id)) {
    echo "  [skip] Block type '$id' already exists.\n";
    continue;
  }
  BlockContentType::create([
    'id' => $id,
    'label' => $label,
    'revision' => TRUE,
  ])->save();
  // Create default displays.
  \Drupal::service('entity_display.repository')->getFormDisplay('block_content', $id)->save();
  \Drupal::service('entity_display.repository')->getViewDisplay('block_content', $id)->save();
  echo "  [ok] Created block type '$id'.\n";
}

// Trust Badge fields
sa_add_text_field('block_content', 'trust_badge_block', 'field_badge_icon', 'Icon');
sa_add_text_field('block_content', 'trust_badge_block', 'field_badge_text', 'Badge Text');

// Section Header fields
sa_add_text_field('block_content', 'section_header_block', 'field_section_tag', 'Section Tag');
sa_add_text_field('block_content', 'section_header_block', 'field_section_heading', 'Heading');
sa_add_text_long_field('block_content', 'section_header_block', 'field_section_subheading', 'Subheading');

// Dashboard Mockup fields
sa_add_text_field('block_content', 'dashboard_mockup_block', 'field_mockup_acos_label', 'ACoS Label');
sa_add_text_field('block_content', 'dashboard_mockup_block', 'field_mockup_acos_value', 'ACoS Value');
sa_add_text_long_field('block_content', 'dashboard_mockup_block', 'field_mockup_actions', 'Autopilot Actions (JSON)');
sa_add_text_long_field('block_content', 'dashboard_mockup_block', 'field_mockup_chart_data', 'Chart Data (JSON)');
sa_add_text_field('block_content', 'dashboard_mockup_block', 'field_mockup_chat_query', 'Chat Query');
sa_add_text_long_field('block_content', 'dashboard_mockup_block', 'field_mockup_chat_answer', 'Chat Answer');

// Setup Step fields
sa_add_text_field('block_content', 'setup_step_block', 'field_setup_feature_name', 'Feature Name');
sa_add_text_field('block_content', 'setup_step_block', 'field_setup_feature_stat', 'Feature Stat');
sa_add_text_field('block_content', 'setup_step_block', 'field_setup_feature_icon', 'Icon');
sa_add_boolean_field('block_content', 'setup_step_block', 'field_setup_live_badge', 'Show LIVE Badge');
sa_add_integer_field('block_content', 'setup_step_block', 'field_setup_weight', 'Sort Order');

echo "  Block types done.\n";

// ============================================================
// 3. MEDIA TYPES
// ============================================================

echo "\n=== 3. CREATING MEDIA TYPES ===\n";

// Icon media type
if (!MediaType::load('icon')) {
  $icon_type = MediaType::create([
    'id' => 'icon',
    'label' => 'Icon (SVG)',
    'description' => 'SVG icon files for frontend mapping.',
    'source' => 'file',
    'source_configuration' => [
      'source_field' => 'field_media_file',
    ],
  ]);
  $icon_type->save();

  // Create source field for icon.
  sa_create_field_storage('media', 'field_media_file', 'file');
  sa_create_field_instance('media', 'icon', 'field_media_file', 'SVG File', [
    'file_extensions' => 'svg',
  ]);
  // Create default displays.
  \Drupal::service('entity_display.repository')->getFormDisplay('media', 'icon')->save();
  \Drupal::service('entity_display.repository')->getViewDisplay('media', 'icon')->save();

  sa_add_text_field('media', 'icon', 'field_icon_identifier', 'Identifier');
  echo "  [ok] Created media type 'icon'.\n";
}
else {
  echo "  [skip] Media type 'icon' already exists.\n";
}

// Brand Asset media type
if (!MediaType::load('brand_asset')) {
  $brand_type = MediaType::create([
    'id' => 'brand_asset',
    'label' => 'Brand Asset',
    'description' => 'Logo, favicon, and brand image files.',
    'source' => 'file',
    'source_configuration' => [
      'source_field' => 'field_media_brand_file',
    ],
  ]);
  $brand_type->save();

  sa_create_field_storage('media', 'field_media_brand_file', 'file');
  sa_create_field_instance('media', 'brand_asset', 'field_media_brand_file', 'Brand File', [
    'file_extensions' => 'png jpg jpeg svg gif webp ico',
  ]);
  \Drupal::service('entity_display.repository')->getFormDisplay('media', 'brand_asset')->save();
  \Drupal::service('entity_display.repository')->getViewDisplay('media', 'brand_asset')->save();

  sa_add_list_string_field('media', 'brand_asset', 'field_brand_type', 'Asset Type', [
    'logo' => 'Logo',
    'favicon' => 'Favicon',
    'og_image' => 'OG Image',
  ]);
  sa_add_list_string_field('media', 'brand_asset', 'field_brand_variant', 'Variant', [
    'light' => 'Light',
    'dark' => 'Dark',
    'icon_only' => 'Icon Only',
  ]);
  echo "  [ok] Created media type 'brand_asset'.\n";
}
else {
  echo "  [skip] Media type 'brand_asset' already exists.\n";
}

echo "  Media types done.\n";

// ============================================================
// 4. TAXONOMY VOCABULARIES
// ============================================================

echo "\n=== 4. CREATING TAXONOMY VOCABULARIES ===\n";

$vocabularies = [
  'feature_category' => [
    'label' => 'Feature Category',
    'terms' => ['Core Features', 'Advanced Features', 'AI-Powered', 'Reporting'],
  ],
  'audience_segment' => [
    'label' => 'Audience Segment',
    'terms' => ['Individual Sellers', 'Brands', 'Agencies'],
  ],
  'pricing_tier' => [
    'label' => 'Pricing Tier',
    'terms' => ['Starter', 'Pro', 'Agency'],
  ],
];

foreach ($vocabularies as $vid => $config) {
  if (!Vocabulary::load($vid)) {
    Vocabulary::create([
      'vid' => $vid,
      'name' => $config['label'],
    ])->save();
    echo "  [ok] Created vocabulary '$vid'.\n";
  }
  else {
    echo "  [skip] Vocabulary '$vid' already exists.\n";
  }

  // Create terms.
  $weight = 0;
  foreach ($config['terms'] as $term_name) {
    $existing = \Drupal::entityTypeManager()
      ->getStorage('taxonomy_term')
      ->loadByProperties(['vid' => $vid, 'name' => $term_name]);
    if (empty($existing)) {
      Term::create([
        'vid' => $vid,
        'name' => $term_name,
        'weight' => $weight,
      ])->save();
      echo "    [ok] Created term '$term_name'.\n";
    }
    $weight++;
  }
}

echo "  Taxonomies done.\n";

// ============================================================
// 5. USER PROFILE FIELDS
// ============================================================

echo "\n=== 5. ADDING USER PROFILE FIELDS ===\n";

sa_add_text_field('user', 'user', 'field_full_name', 'Full Name');
sa_add_link_field('user', 'user', 'field_amazon_store_url', 'Amazon Store URL');
sa_add_list_string_field('user', 'user', 'field_trial_status', 'Trial Status', [
  'pending' => 'Pending',
  'active' => 'Active',
  'expired' => 'Expired',
]);
sa_add_timestamp_field('user', 'user', 'field_trial_started', 'Trial Started');
sa_add_entity_reference_field('user', 'user', 'field_user_type', 'User Type', 'taxonomy_term', ['audience_segment']);
sa_add_text_field('user', 'user', 'field_company_name', 'Company Name');

echo "  User profile fields done.\n";

// ============================================================
// 6. MENUS AND MENU LINKS
// ============================================================

echo "\n=== 6. CREATING MENUS ===\n";

$menus = [
  'footer-product' => 'Footer - Product',
  'footer-company' => 'Footer - Company',
  'footer-legal' => 'Footer - Legal',
];

foreach ($menus as $id => $label) {
  if (!Menu::load($id)) {
    Menu::create([
      'id' => $id,
      'label' => $label,
    ])->save();
    echo "  [ok] Created menu '$id'.\n";
  }
  else {
    echo "  [skip] Menu '$id' already exists.\n";
  }
}

// Main navigation links (using existing 'main' menu)
$menu_items = [
  'main' => [
    ['title' => 'Features', 'uri' => 'internal:#features', 'weight' => 1],
    ['title' => 'How it Works', 'uri' => 'internal:#how-it-works', 'weight' => 2],
    ['title' => 'Testimonials', 'uri' => 'internal:#testimonials', 'weight' => 3],
    ['title' => 'Pricing', 'uri' => 'internal:#pricing', 'weight' => 4],
  ],
  'footer-product' => [
    ['title' => 'Features', 'uri' => 'internal:/features', 'weight' => 1],
    ['title' => 'Pricing', 'uri' => 'internal:/pricing', 'weight' => 2],
    ['title' => 'Case Studies', 'uri' => 'internal:/case-studies', 'weight' => 3],
    ['title' => 'API Docs', 'uri' => 'internal:/api-docs', 'weight' => 4],
  ],
  'footer-company' => [
    ['title' => 'About Us', 'uri' => 'internal:/about', 'weight' => 1],
    ['title' => 'Blog', 'uri' => 'internal:/blog', 'weight' => 2],
    ['title' => 'Careers', 'uri' => 'internal:/careers', 'weight' => 3],
    ['title' => 'Contact Support', 'uri' => 'internal:/contact', 'weight' => 4],
  ],
  'footer-legal' => [
    ['title' => 'Privacy Policy', 'uri' => 'internal:/privacy-policy', 'weight' => 1],
    ['title' => 'Terms of Service', 'uri' => 'internal:/terms-of-service', 'weight' => 2],
  ],
];

foreach ($menu_items as $menu_name => $items) {
  // Check if menu already has links.
  $existing = \Drupal::entityTypeManager()
    ->getStorage('menu_link_content')
    ->loadByProperties(['menu_name' => $menu_name]);
  if (!empty($existing)) {
    echo "  [skip] Menu '$menu_name' already has links.\n";
    continue;
  }
  foreach ($items as $item) {
    MenuLinkContent::create([
      'title' => $item['title'],
      'link' => ['uri' => $item['uri']],
      'menu_name' => $menu_name,
      'weight' => $item['weight'],
      'expanded' => FALSE,
    ])->save();
  }
  echo "  [ok] Created links in menu '$menu_name'.\n";
}

echo "  Menus done.\n";

// ============================================================
// 7. IMAGE STYLES
// ============================================================

echo "\n=== 7. CREATING IMAGE STYLES ===\n";

$image_styles = [
  'hero_slide' => [
    'label' => 'Hero Slide (1400x600)',
    'effect' => 'image_scale_and_crop',
    'data' => ['width' => 1400, 'height' => 600],
  ],
  'hero_slide_mobile' => [
    'label' => 'Hero Slide Mobile (800x500)',
    'effect' => 'image_scale_and_crop',
    'data' => ['width' => 800, 'height' => 500],
  ],
  'testimonial_avatar' => [
    'label' => 'Testimonial Avatar (80x80)',
    'effect' => 'image_scale_and_crop',
    'data' => ['width' => 80, 'height' => 80],
  ],
  'og_image' => [
    'label' => 'OG Image (1200x630)',
    'effect' => 'image_scale_and_crop',
    'data' => ['width' => 1200, 'height' => 630],
  ],
  'sa_thumbnail' => [
    'label' => 'SA Thumbnail (150x150)',
    'effect' => 'image_scale_and_crop',
    'data' => ['width' => 150, 'height' => 150],
  ],
  'brand_logo' => [
    'label' => 'Brand Logo (200w)',
    'effect' => 'image_scale',
    'data' => ['width' => 200, 'height' => NULL],
  ],
];

foreach ($image_styles as $id => $config) {
  if (ImageStyle::load($id)) {
    echo "  [skip] Image style '$id' already exists.\n";
    continue;
  }
  $style = ImageStyle::create([
    'name' => $id,
    'label' => $config['label'],
  ]);
  $style->addImageEffect([
    'id' => $config['effect'],
    'data' => $config['data'],
  ]);
  $style->save();
  echo "  [ok] Created image style '$id'.\n";
}

echo "  Image styles done.\n";

// ============================================================
// 8. USER ROLES
// ============================================================

echo "\n=== 8. CREATING USER ROLES ===\n";

$roles = [
  'trial_user' => 'Trial User',
  'content_editor' => 'Content Editor',
  'site_admin' => 'Site Admin',
];

foreach ($roles as $rid => $label) {
  if (Role::load($rid)) {
    echo "  [skip] Role '$rid' already exists.\n";
    continue;
  }
  $role = Role::create(['id' => $rid, 'label' => $label]);
  $role->save();
  echo "  [ok] Created role '$rid'.\n";
}

// Grant permissions to content_editor.
$content_editor = Role::load('content_editor');
if ($content_editor) {
  $editor_perms = [
    'access content',
    'access content overview',
    'administer nodes',
    'access media overview',
    'create media',
    'update any media',
    'delete any media',
  ];
  // Add CRUD permissions for all custom content types.
  $custom_types = [
    'landing_page', 'hero_slide', 'stat_card', 'pain_point', 'feature',
    'audience_type', 'onboarding_step', 'testimonial', 'pricing_plan',
    'result_metric', 'cta_section',
  ];
  foreach ($custom_types as $ct) {
    $editor_perms[] = "create $ct content";
    $editor_perms[] = "edit any $ct content";
    $editor_perms[] = "delete any $ct content";
  }
  foreach ($editor_perms as $perm) {
    $content_editor->grantPermission($perm);
  }
  $content_editor->save();
  echo "  [ok] Granted permissions to 'content_editor'.\n";
}

// Grant permissions to site_admin.
$site_admin = Role::load('site_admin');
if ($site_admin) {
  $admin_perms = [
    'access content',
    'administer nodes',
    'administer content types',
    'administer users',
    'administer site configuration',
    'access content overview',
    'administer taxonomy',
    'access media overview',
    'create media',
    'update any media',
    'delete any media',
    'administer menu',
    'administer blocks',
  ];
  foreach ($admin_perms as $perm) {
    $site_admin->grantPermission($perm);
  }
  $site_admin->save();
  echo "  [ok] Granted permissions to 'site_admin'.\n";
}

// Grant trial_user basic permissions.
$trial_user = Role::load('trial_user');
if ($trial_user) {
  $trial_user->grantPermission('access content');
  $trial_user->save();
  echo "  [ok] Granted permissions to 'trial_user'.\n";
}

echo "  Roles done.\n";

// ============================================================
// DONE
// ============================================================

echo "\n=============================================\n";
echo "  SellerBuddy Content Architecture Setup  \n";
echo "  COMPLETE                                   \n";
echo "=============================================\n\n";
echo "Summary:\n";
echo "  - 11 content types created\n";
echo "  - 4 block types created\n";
echo "  - 2 custom media types created\n";
echo "  - 3 taxonomy vocabularies with terms\n";
echo "  - 6 user profile fields added\n";
echo "  - 4 menus with links created\n";
echo "  - 6 image styles created\n";
echo "  - 3 user roles with permissions\n";
echo "\nNext: Run 'drush config:export' to export config.\n";
