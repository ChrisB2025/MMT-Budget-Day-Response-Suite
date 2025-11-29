#!/bin/bash
# Startup script for Railway deployment
# Simplified to avoid hanging - migrations can be run manually if needed

echo "========================================"
echo "Starting MMT Campaign Suite"
echo "========================================"

# Skip migrations/seeding to avoid hangs - run these manually if needed:
# railway run python manage.py migrate --noinput
# railway run python manage.py seed_media_outlets
# railway run python manage.py load_budget_phrases

echo "Starting Daphne ASGI server..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application
