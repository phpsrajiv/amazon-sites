#!/bin/bash
# SellerAgent AI - Drupal 11 Installation Script
# Run this after docker compose up to install Drupal site.

set -e

echo "==> Waiting for Drupal container to be ready..."
sleep 5

echo "==> Installing Drupal site..."
docker exec selleragent-drupal bash -c "
  cd /opt/drupal && \
  vendor/bin/drush site:install standard \
    --db-url=mysql://\${DRUPAL_DB_USER}:\${DRUPAL_DB_PASSWORD}@\${DRUPAL_DB_HOST}:\${DRUPAL_DB_PORT}/\${DRUPAL_DB_NAME} \
    --site-name='SellerAgent AI' \
    --account-name=admin \
    --account-pass=admin \
    --account-mail=admin@selleragent.ai \
    --no-interaction \
    -y
"

echo "==> Enabling contrib modules..."
docker exec selleragent-drupal bash -c "
  cd /opt/drupal && \
  vendor/bin/drush en -y \
    jsonapi \
    jsonapi_extras \
    jsonapi_menu_items \
    restui \
    token \
    pathauto \
    metatag \
    simple_sitemap \
    admin_toolbar \
    admin_toolbar_tools \
    field_group \
    paragraphs \
    config_split \
    redirect \
    consumer_image_styles \
    subrequests \
    jsonapi_include \
    simple_oauth \
    environment_indicator \
    stage_file_proxy \
    media \
    media_library
"

echo "==> Enabling custom modules..."
docker exec selleragent-drupal bash -c "
  cd /opt/drupal && \
  vendor/bin/drush en -y \
    selleragent_core \
    selleragent_api
"

echo "==> Clearing cache..."
docker exec selleragent-drupal bash -c "cd /opt/drupal && vendor/bin/drush cr"

echo ""
echo "============================================="
echo "  SellerAgent AI - Drupal 11 Installation    "
echo "============================================="
echo ""
echo "  Drupal Admin:  http://localhost:8080"
echo "  Username:      admin"
echo "  Password:      admin"
echo "  Frontend:      http://localhost:3000"
echo "  JSON:API:      http://localhost:8080/jsonapi"
echo ""
echo "============================================="
