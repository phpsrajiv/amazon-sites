FROM drupal:11-php8.3-apache

# Install additional PHP extensions and utilities
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    libpng-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    libwebp-dev \
    libzip-dev \
    mariadb-client \
    && docker-php-ext-configure gd --with-freetype --with-jpeg --with-webp \
    && docker-php-ext-install -j$(nproc) gd opcache zip pdo_mysql \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable Apache mod_rewrite
RUN a2enmod rewrite headers

# Increase PHP memory limit and execution time
RUN echo 'memory_limit = 512M' > /usr/local/etc/php/conf.d/drupal.ini \
    && echo 'max_execution_time = 300' >> /usr/local/etc/php/conf.d/drupal.ini \
    && echo 'upload_max_filesize = 64M' >> /usr/local/etc/php/conf.d/drupal.ini \
    && echo 'post_max_size = 64M' >> /usr/local/etc/php/conf.d/drupal.ini

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /opt/drupal

# Copy the Drupal project
COPY drupal/composer.json drupal/composer.lock ./
RUN composer install --no-dev --optimize-autoloader --no-interaction

# Copy the rest of the Drupal project files
COPY drupal/ ./

# Set proper permissions
RUN chown -R www-data:www-data /opt/drupal/web/sites/default \
    && mkdir -p /opt/drupal/web/sites/default/files \
    && chmod -R 775 /opt/drupal/web/sites/default/files

# Copy custom settings
COPY config/settings.php /opt/drupal/web/sites/default/settings.php
COPY config/services.yml /opt/drupal/web/sites/default/services.yml

# Set proper ownership
RUN chown -R www-data:www-data /opt/drupal

EXPOSE 80
