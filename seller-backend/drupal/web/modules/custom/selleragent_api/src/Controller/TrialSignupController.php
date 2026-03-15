<?php

namespace Drupal\selleragent_api\Controller;

use Drupal\Core\Controller\ControllerBase;
use Drupal\user\Entity\User;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;

/**
 * Handles trial signup form submissions from the decoupled frontend.
 */
class TrialSignupController extends ControllerBase {

  /**
   * Processes a trial signup request.
   */
  public function signup(Request $request): JsonResponse {
    $content = json_decode($request->getContent(), TRUE);

    if (empty($content['name']) || empty($content['email'])) {
      return new JsonResponse([
        'success' => FALSE,
        'message' => 'Name and email are required.',
      ], 400);
    }

    $name = trim($content['name']);
    $email = trim($content['email']);
    $store_url = trim($content['storeUrl'] ?? '');

    // Check if email already exists.
    $existing = user_load_by_mail($email);
    if ($existing) {
      return new JsonResponse([
        'success' => FALSE,
        'message' => 'An account with this email already exists.',
      ], 409);
    }

    try {
      $user = User::create([
        'name' => $email,
        'mail' => $email,
        'status' => 1,
        'field_full_name' => $name,
        'field_amazon_store_url' => $store_url ? ['uri' => $store_url] : [],
        'field_trial_status' => 'active',
        'field_trial_started' => time(),
      ]);

      // Assign trial_user role.
      $user->addRole('trial_user');
      $user->save();

      return new JsonResponse([
        'success' => TRUE,
        'message' => 'Welcome aboard! Your free trial has started.',
        'user_id' => $user->id(),
      ], 201);
    }
    catch (\Exception $e) {
      $this->getLogger('selleragent_api')->error('Trial signup failed: @message', [
        '@message' => $e->getMessage(),
      ]);

      return new JsonResponse([
        'success' => FALSE,
        'message' => 'Something went wrong. Please try again.',
      ], 500);
    }
  }

}
