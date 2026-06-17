#!/bin/bash
set -e

BASE_DIR="/root/task"

echo "[run] Checking Docker availability..."
if ! command -v docker >/dev/null 2>&1; then
  echo "[run] ERROR: Docker is not available on this host."
  exit 1
fi

echo "[run] Changing to project directory: ${BASE_DIR}"
cd "${BASE_DIR}"

echo "[run] Building and starting the triage agent stack..."
docker compose up -d --build

echo "[run] Waiting for Redis to become healthy..."
for i in $(seq 1 15); do
  if docker compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo "[run] Redis is reachable."
    break
  fi
  sleep 2
done

echo "[run] Waiting for the agent application to start..."
for i in $(seq 1 15); do
  if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "[run] Agent application is reachable."
    break
  fi
  sleep 2
done

echo "[run] Current container status:"
docker compose ps

echo "[run] Stack is up. Endpoint available at http://127.0.0.1:8000"

