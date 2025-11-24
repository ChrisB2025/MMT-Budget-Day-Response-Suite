release: python manage.py migrate && python manage.py fix_site_config && python manage.py seed_media_outlets
web: daphne -b 0.0.0.0 -p $PORT config.asgi:application
worker: celery -A config worker --loglevel=info
