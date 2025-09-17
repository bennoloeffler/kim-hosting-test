#!/bin/sh
set -e

echo "Starting FastAPI application..."
echo "Environment: Production"
echo "Port: ${PORT:-8080}"
echo "Host: ${HOST:-0.0.0.0}"

exec uvicorn backend:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8080}" \
    --workers 1 \
    --log-level info