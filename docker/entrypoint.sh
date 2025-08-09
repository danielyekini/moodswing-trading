set -euo pipefail

python - <<'PY'
import os, time, psycopg2
url = os.environ.get('DATABASE_URL')
while True:
    try:
        psycopg2.connect(url).close()
        break
    except Exception:
        print('Waiting for database...', flush=True)
        time.sleep(1)
PY

alembic upgrade head
exec uvicorn moodswing_trading.main:app --host 0.0.0.0 --port 8000 --workers 2