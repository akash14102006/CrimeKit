#!/bin/sh
# CrimeKit Backend Startup Script
# Handles initialization and server start

set -e

echo "=== CrimeKit Backend Startup ==="
echo "Environment: ${APP_ENV:-development}"
echo "Debug: ${APP_DEBUG:-false}"
echo "Log Level: ${APP_LOG_LEVEL:-info}"

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
i=1
while [ "$i" -le 30 ]; do
    if python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
result = s.connect_ex(('${POSTGRES_HOST:-postgres}', ${POSTGRES_PORT:-5432}))
s.close()
exit(0 if result == 0 else 1)
" 2>/dev/null; then
        echo "PostgreSQL is ready"
        break
    fi
    echo "  PostgreSQL not ready, retrying in 2s... ($i/30)"
    sleep 2
    i=$((i + 1))
done

# Wait for Redis
echo "Waiting for Redis..."
i=1
while [ "$i" -le 15 ]; do
    if python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
result = s.connect_ex(('${REDIS_HOST:-redis}', ${REDIS_PORT:-6379}))
s.close()
exit(0 if result == 0 else 1)
" 2>/dev/null; then
        echo "Redis is ready"
        break
    fi
    echo "  Redis not ready, retrying in 2s... ($i/15)"
    sleep 2
    i=$((i + 1))
done

# Initialize database
echo "Initializing database..."
python -c "
from app.database import configure_database, init_db
configure_database()
init_db()
print('Database initialized')
"

# Start the application
echo "Starting CrimeKit backend..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${BACKEND_PORT:-8000} \
    --workers ${UVICORN_WORKERS:-2} \
    --log-level ${APP_LOG_LEVEL:-info} \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips='*'
