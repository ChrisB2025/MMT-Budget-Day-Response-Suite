"""
Django settings for budget_response_suite project.
Base settings shared across all environments.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application version
VERSION = '2.0.0'

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')

# Application definition
INSTALLED_APPS = [
    'daphne',  # Must be first for Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Keep for existing migrations

    # Django-allauth (keep installed for existing migrations, but not used)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.discord',

    # Third party
    'channels',

    # Local apps
    'apps.core',
    'apps.users',
    'apps.bingo',
    'apps.factcheck',
    'apps.rebuttal',
    'apps.media_complaints',
    'apps.social_critique',
    'apps.article_critique',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required for existing migrations
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.mmt_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgresql://budget_user:budget_pass@localhost:5432/budget_suite')
}

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Whitenoise configuration
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Channels configuration
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

# Check if Redis is available before configuring channel layers
def get_channel_layers():
    """
    Returns channel layer configuration with Redis if available,
    otherwise falls back to InMemoryChannelLayer.
    """
    try:
        import redis
        r = redis.from_url(REDIS_URL)
        r.ping()
        return {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    'hosts': [REDIS_URL],
                },
            },
        }
    except Exception:
        # Fallback to in-memory channel layer when Redis is unavailable
        return {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
            },
        }

CHANNEL_LAYERS = get_channel_layers()

# Celery configuration
# Use REDIS_URL as default to simplify Railway configuration - only one variable to update
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Anthropic Claude API
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')
CLAUDE_MODEL = env('CLAUDE_MODEL', default='claude-sonnet-4-20250514')
CLAUDE_MAX_TOKENS = env.int('CLAUDE_MAX_TOKENS', default=4000)

# Google Gemini API (for YouTube video transcript extraction)
GEMINI_API_KEY = env('GEMINI_API_KEY', default='')

# YouTube Data API (for fetching video captions)
YOUTUBE_API_KEY = env('YOUTUBE_API_KEY', default='')

# Login configuration
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'

# =============================================================================
# MMT Campaign Suite Configuration
# =============================================================================

# Discord community invite link
MMT_DISCORD_INVITE_URL = env('MMT_DISCORD_INVITE_URL', default='https://discord.gg/DXn9rxt9bh')

# Keystroke Kingdom educational app URL
KEYSTROKE_KINGDOM_URL = env('KEYSTROKE_KINGDOM_URL', default='https://keystroke.mmtaction.uk/')

# Site branding
MMT_SITE_NAME = 'MMT Campaign Suite'
MMT_SITE_TAGLINE = 'Track economic myths in real time, crowdsource fact checks, hold media accountable, and generate shareable MMT rebuttals.'

# Default hashtag for generated social content
MMT_DEFAULT_HASHTAG = '#mmt'

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# Django Sites Framework (required for existing migrations)
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
