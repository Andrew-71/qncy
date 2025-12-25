#!/bin/sh

# Stop on error
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z $QNCY_DB_URI $DATABASE_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Applying database migrations..."
python manage.py migrate
python manage.py createcachetable

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
