#!/bin/bash

echo "Building and starting containers..."
docker compose up -d --build

echo "Waiting for services to stabilize..."
sleep 5

container_name=$(docker compose ps -q web | head -n1)

if [ -z "$container_name" ]; then
    echo "Error: Web container not found!"
    exit 1
fi

echo "Running post-deploy tasks on $container_name..."

docker exec $container_name python manage.py fill_db 100

echo "Generating initial sidebar..."
docker exec $container_name python manage.py createcachetable
docker exec $container_name python manage.py generate_sidebar

echo "Deployment complete! Application is running on port 8000."
