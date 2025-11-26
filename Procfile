release: python manage.py migrate && python manage.py seed_media_outlets && python manage.py load_budget_phrases
web: daphne -b 0.0.0.0 -p $PORT config.asgi:application
worker: celery -A config worker --loglevel=info
