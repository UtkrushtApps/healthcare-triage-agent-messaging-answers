#!/bin/bash

BASE_DIR="/root/task"

echo "[kill] Changing to project directory: ${BASE_DIR}"
cd "${BASE_DIR}" || true

echo "[kill] Stopping and removing containers..."
docker compose down --remove-orphans || true

echo "[kill] Removing task-specific volumes..."
docker compose down --volumes || true
docker volume rm task_redis-data || true

echo "[kill] Removing task-specific networks..."
docker network rm task_default || true

echo "[kill] Removing task-specific images..."
docker image rm task-agent-app || true
docker rmi triage-agent-app || true

echo "[kill] Pruning leftover Docker resources..."
docker system prune -a --volumes -f || true

echo "[kill] Removing task directory..."
rm -rf /root/task || true

echo "Cleanup completed successfully!"

