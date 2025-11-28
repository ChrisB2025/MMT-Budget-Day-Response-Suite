"""App configuration for article_critique."""
from django.apps import AppConfig


class ArticleCritiqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.article_critique'
    verbose_name = 'Article Critique'
