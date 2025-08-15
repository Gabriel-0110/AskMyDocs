#!/usr/bin/env bash
set -Eeuo pipefail

# Azure sets $PORT; default to 8000 if running locally
PORT="${PORT:-8000}"
HOST="0.0.0.0"
WORKERS="${WEB_CONCURRENCY:-2}"
TIMEOUT="${WEB_TIMEOUT:-120}"

# Optional override:
#   APP_MODULE="module:app" (e.g., "app:app", "main:app", "mysite.wsgi:application")
#   APP_SERVER="uvicorn" to force uvicorn for ASGI apps; defaults to gunicorn
APP_MODULE="${APP_MODULE:-}"
APP_SERVER="${APP_SERVER:-gunicorn}"

if [[ -n "$APP_MODULE" ]]; then
  if [[ "$APP_SERVER" == "uvicorn" ]]; then
    exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --workers "$WORKERS"
  else
    exec gunicorn "$APP_MODULE" --bind "$HOST:$PORT" --workers "$WORKERS" --threads 2 --timeout "$TIMEOUT" --log-level info
  fi
fi

# --- Auto-detect common layouts ---
if [[ -f "streamlit_app.py" ]]; then
  # Streamlit
  exec python -m streamlit run streamlit_app.py --server.port="$PORT" --server.address="$HOST"
elif [[ -f "manage.py" ]]; then
  # Django (set DJANGO_SETTINGS_MODULE if your project isn't "mysite")
  export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-mysite.settings}"
  python manage.py collectstatic --noinput || true
  exec gunicorn "${DJANGO_WSGI_MODULE:-mysite.wsgi:application}" --bind "$HOST:$PORT" --workers "$WORKERS" --timeout "$TIMEOUT" --log-level info
elif [[ -f "app.py" ]]; then
  # Flask or FastAPI with 'app' in app.py
  exec gunicorn "app:app" --bind "$HOST:$PORT" --workers "$WORKERS" --threads 2 --timeout "$TIMEOUT" --log-level info
elif [[ -f "main.py" ]]; then
  # FastAPI with 'app' in main.py
  exec uvicorn main:app --host "$HOST" --port "$PORT" --workers "$WORKERS"
else
  echo "❌ Could not determine app entry point.
Set APP_MODULE='module:app' in App Service > Configuration (e.g., 'AskMyDocs.api:app')."
  sleep 5
  exit 1
fi
