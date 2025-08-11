#!/bin/sh
set -eu

# Simple wait-for Postgres based on psql
if command -v psql >/dev/null 2>&1; then
  DB_URL="${DATABASE_URL:-}"
  DB_URL_NORM=$(printf '%s' "$DB_URL" | sed 's|postgresql+psycopg2://|postgresql://|')
  echo "Waiting for database with psql..."
  until PGPASSWORD=$(printf '%s' "$DB_URL_NORM" | sed 's|.*://\([^:]*\):\([^@]*\)@.*|\2|') \
      psql "$(printf '%s' "$DB_URL_NORM" | sed 's|://[^@]*@|://|' )" -c 'select 1' >/dev/null 2>&1; do
    echo "Waiting for database..."
    sleep 1
  done
fi

alembic upgrade head
UVICORN_WORKERS="${UVICORN_WORKERS:-1}"
exec uvicorn moodswing_trading.main:app --host 0.0.0.0 --port 8000 --workers "$UVICORN_WORKERS" --log-level info