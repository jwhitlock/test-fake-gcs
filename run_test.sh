#!/bin/bash
set -e  # Stop on first failing command

echo "Stopping any previous runs..."
docker-compose down

echo "Building images..."
docker-compose build server
docker-compose build client

echo "Running the test..."
docker-compose run --rm client

docker-compose stop
