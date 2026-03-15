<?php

namespace Drupal\selleragent_api\Controller;

use Drupal\Core\Controller\ControllerBase;
use Symfony\Component\HttpFoundation\JsonResponse;

/**
 * Returns blog post data via REST API.
 */
class BlogController extends ControllerBase {

  /**
   * Returns all published blog posts sorted by weight.
   */
  public function getAll(): JsonResponse {
    $data = $this->loadContentByType('blog_post', 'field_blog_weight');
    $response = new JsonResponse($data);
    $response->headers->set('Cache-Control', 'public, max-age=300');
    return $response;
  }

  /**
   * Returns a single blog post by node ID.
   */
  public function getOne(string $nid): JsonResponse {
    try {
      $storage = $this->entityTypeManager()->getStorage('node');
      $node = $storage->load($nid);

      if (!$node || $node->bundle() !== 'blog_post' || !$node->isPublished()) {
        return new JsonResponse(['error' => 'Blog post not found'], 404);
      }

      $item = ['id' => $node->id(), 'title' => $node->getTitle()];
      foreach ($node->getFields() as $field_name => $field) {
        if (str_starts_with($field_name, 'field_')) {
          $item[$field_name] = $field->value ?? $field->getString();
        }
      }

      // Build SEO metadata.
      $site_config = $this->config('system.site');
      $site_name = $site_config->get('name');
      $summary = $node->hasField('field_blog_summary') ? $node->get('field_blog_summary')->value ?? '' : '';
      $image = $node->hasField('field_blog_image') ? $node->get('field_blog_image')->getString() : '';
      $author = $node->hasField('field_blog_author') ? $node->get('field_blog_author')->value ?? '' : '';
      $date = $node->hasField('field_blog_date') ? $node->get('field_blog_date')->value ?? '' : '';
      $category = $node->hasField('field_blog_category') ? $node->get('field_blog_category')->value ?? '' : '';

      $item['seo'] = [
        'title' => $node->getTitle() . ' | ' . $site_name . ' Blog',
        'description' => $summary,
        'og_title' => $node->getTitle(),
        'og_description' => $summary,
        'og_type' => 'article',
        'og_image' => $image,
        'og_site_name' => $site_name,
        'twitter_card' => 'summary_large_image',
        'article_author' => $author,
        'article_published_time' => $date,
        'article_section' => $category,
      ];

      $response = new JsonResponse($item);
      $response->headers->set('Cache-Control', 'public, max-age=300');
      return $response;
    }
    catch (\Exception $e) {
      return new JsonResponse(['error' => 'Blog post not found'], 404);
    }
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

}
