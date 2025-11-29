#!/bin/bash
# Startup script for Railway deployment
# This script handles migrations and seeding with proper error handling

set -e  # Exit on error

echo "========================================"
echo "Starting MMT Campaign Suite Deployment"
echo "========================================"
echo ""

# Run migrations
echo "[1/4] Running database migrations..."
if python manage.py migrate --noinput; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migration failed! Check database configuration."
    echo "Attempting to continue anyway..."
fi
echo ""

# Seed media outlets (idempotent - uses update_or_create)
echo "[2/4] Seeding media outlets..."
if python manage.py seed_media_outlets; then
    echo "✓ Media outlets seeded successfully"
else
    echo "✗ Media outlets seeding failed"
    echo "This is non-critical, continuing..."
fi
echo ""

# Load bingo phrases (clears and reloads)
echo "[3/4] Loading bingo phrases..."
if python manage.py load_budget_phrases; then
    echo "✓ Bingo phrases loaded successfully"
else
    echo "✗ Bingo phrases loading failed"
    echo "This is non-critical, continuing..."
fi
echo ""

# Collect static files (in case build didn't run)
echo "[4/4] Collecting static files..."
if python manage.py collectstatic --noinput; then
    echo "✓ Static files collected"
else
    echo "✗ Static file collection failed"
    echo "This may cause issues with CSS/JS..."
fi
echo ""

echo "========================================"
echo "Startup tasks complete, launching server"
echo "========================================"
echo ""

# Start the ASGI server
exec daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application
