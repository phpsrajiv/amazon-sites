<?php

namespace Drupal\selleragent_api\Controller;

use Drupal\Core\Controller\ControllerBase;
use Symfony\Component\HttpFoundation\JsonResponse;

/**
 * Returns global site settings as JSON.
 */
class SiteSettingsController extends ControllerBase {

  /**
   * Returns site configuration settings.
   */
  public function getSettings(): JsonResponse {
    $site_config = $this->config('system.site');

    $data = [
      'site_name' => $site_config->get('name'),
      'site_slogan' => $site_config->get('slogan'),
      'copyright_text' => date('Y') . ' SellerBuddy. All rights reserved.',
    ];

    return new JsonResponse($data);
  }

}
