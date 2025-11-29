#!/bin/bash
set -e

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding media outlets..."
python manage.py seed_media_outlets

echo "==> Loading budget phrases..."
python manage.py load_budget_phrases

echo "==> Deployment setup complete!"
