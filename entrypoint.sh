#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Seed reference data (courses + study levels)
echo "Seeding reference data..."
python manage.py seed_reference_data

# Collect static files (optional, uncomment if needed)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
# python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || true

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 3
