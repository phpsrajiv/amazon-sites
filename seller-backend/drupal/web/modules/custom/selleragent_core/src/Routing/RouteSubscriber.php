<?php

declare(strict_types=1);

namespace Drupal\selleragent_core\Routing;

use Drupal\Core\Routing\RouteSubscriberBase;
use Symfony\Component\Routing\RouteCollection;

/**
 * Restricts node canonical route to admin roles only.
 *
 * Blocks direct browsing of /node/{nid} for anonymous and non-admin users.
 * Content remains accessible via JSON:API and custom API endpoints since
 * those load nodes programmatically via entity queries, not routes.
 */
class RouteSubscriber extends RouteSubscriberBase {

  /**
   * {@inheritdoc}
   */
  protected function alterRoutes(RouteCollection $collection): void {
    if ($route = $collection->get('entity.node.canonical')) {
      $requirements = $route->getRequirements();
      unset($requirements['_entity_access']);
      $requirements['_role'] = 'administrator+site_admin+content_editor';
      $route->setRequirements($requirements);
    }
  }

}
