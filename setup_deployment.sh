#!/bin/bash
# Pre-deployment script for Railway
# Runs during the release phase before the web process starts

echo "==> Starting pre-deployment setup..."

# Wait for database to be ready (with timeout)
echo "==> Checking database connectivity..."
MAX_RETRIES=10
RETRY_COUNT=0
DB_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; then
        DB_READY=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting for database... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ "$DB_READY" = false ]; then
    echo "ERROR: Database not available after $MAX_RETRIES attempts"
    echo "Attempting to continue anyway..."
fi

echo "  Database check complete"

# Run migrations
echo "==> Running migrations..."
if python manage.py migrate --noinput; then
    echo "  Migrations completed successfully"
else
    echo "  WARNING: Migration command failed, continuing..."
fi

# Seed media outlets (idempotent - uses update_or_create)
echo "==> Seeding media outlets..."
if python manage.py seed_media_outlets; then
    echo "  Media outlets seeded successfully"
else
    echo "  WARNING: Media outlet seeding failed, continuing..."
fi

# Load bingo phrases
echo "==> Loading budget phrases..."
if python manage.py load_budget_phrases; then
    echo "  Budget phrases loaded successfully"
else
    echo "  WARNING: Budget phrases loading failed, continuing..."
fi

echo "==> Pre-deployment setup complete!"
exit 0
