from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class BingoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bingo'
    verbose_name = 'Bingo'

    def ready(self):
        """Initialize bingo phrases on app startup if they don't exist"""
        # Only run in the main process, not in reloader or worker processes
        import sys
        if 'runserver' not in sys.argv and 'manage.py' not in sys.argv[0]:
            try:
                from .models import BingoPhrase

                # Check if phrases exist
                phrase_count = BingoPhrase.objects.count()

                if phrase_count == 0:
                    logger.info("No bingo phrases found. Loading default phrases...")

                    # Import and run the load_budget_phrases command
                    from django.core.management import call_command
                    call_command('load_budget_phrases')

                    logger.info("Bingo phrases loaded successfully!")
                else:
                    logger.info(f"Bingo phrases already loaded ({phrase_count} phrases)")

            except Exception as e:
                logger.error(f"Error loading bingo phrases: {e}")
