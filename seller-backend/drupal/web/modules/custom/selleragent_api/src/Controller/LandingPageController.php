<?php

namespace Drupal\selleragent_api\Controller;

use Drupal\Core\Controller\ControllerBase;
use Symfony\Component\HttpFoundation\JsonResponse;

/**
 * Returns aggregated landing page data in a single API response.
 */
class LandingPageController extends ControllerBase {

  /**
   * Returns all landing page content sections.
   */
  public function getData(): JsonResponse {
    $data = [
      'hero_slides' => $this->loadContentByType('hero_slide', 'field_slide_weight'),
      'stats' => $this->loadContentByType('stat_card', 'field_stat_weight'),
      'pain_points' => $this->loadContentByType('pain_point', 'field_pain_weight'),
      'features' => $this->loadContentByType('feature', 'field_feature_weight'),
      'audience_types' => $this->loadContentByType('audience_type', 'field_audience_weight'),
      'onboarding_steps' => $this->loadContentByType('onboarding_step', 'field_step_number'),
      'testimonials' => $this->loadContentByType('testimonial', 'field_testimonial_weight'),
      'pricing_plans' => $this->loadContentByType('pricing_plan', 'field_plan_weight'),
      'result_metrics' => $this->loadContentByType('result_metric', 'field_metric_weight'),
      'cta_sections' => $this->loadContentByType('cta_section'),
      'site_settings' => $this->getSiteSettings(),
      'seo' => [
        'title' => 'SellerAgent AI | AI-Powered Amazon Advertising Automation',
        'description' => 'Automate your Amazon advertising with intelligent AI agents. Increase rankings, lower ACOS, and scale effortlessly.',
        'og_image' => '/opengraph.jpg',
        'og_type' => 'website',
      ],
    ];

    $response = new JsonResponse($data);
    $response->headers->set('Cache-Control', 'public, max-age=300');
    return $response;
  }

  /**
   * Loads published nodes of a given type sorted by a weight field.
   */
  protected function loadContentByType(string $type, ?string $sort_field = NULL): array {
    try {
      $storage = $this->entityTypeManager()->getStorage('node');
      $query = $storage->getQuery()
        ->condition('type', $type)
        ->condition('status', 1)
        ->accessCheck(TRUE);

      if ($sort_field) {
        $query->sort($sort_field, 'ASC');
      }

      $nids = $query->execute();
      if (empty($nids)) {
        return [];
      }

      $nodes = $storage->loadMultiple($nids);
      $items = [];

      foreach ($nodes as $node) {
        $item = ['id' => $node->id(), 'title' => $node->getTitle()];
        foreach ($node->getFields() as $field_name => $field) {
          if (str_starts_with($field_name, 'field_')) {
            $item[$field_name] = $field->value ?? $field->getString();
          }
        }
        $items[] = $item;
      }

      return $items;
    }
    catch (\Exception $e) {
      return [];
    }
  }

  /**
   * Returns global site settings.
   */
  protected function getSiteSettings(): array {
    $config = $this->config('system.site');
    return [
      'site_name' => $config->get('name'),
      'site_slogan' => $config->get('slogan'),
    ];
  }

}
