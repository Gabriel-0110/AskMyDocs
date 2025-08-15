#!/usr/bin/env bash
set -euo pipefail
set -x  # <-- debug: prints each command so you see it in container logs

# Ensure vendored deps (if present) are on sys.path
export PYTHONPATH="/home/site/wwwroot/.python_packages/lib/site-packages:${PYTHONPATH:-}"

PORT="${PORT:-8000}"
HOST="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true

# Find the app file wherever it is in the package
if [ -f "src/ui/streamlit_app.py" ]; then
  TARGET="src/ui/streamlit_app.py"
elif [ -f "streamlit_app.py" ]; then
  TARGET="streamlit_app.py"
else
  echo "❌ streamlit_app.py not found. Listing tree for debugging:"
  find . -maxdepth 3 -type f -name "streamlit_app.py" -print
  exit 1
fi

python -V
python -m pip show streamlit || true
ls -la "$(dirname "$TARGET")"

exec python -m streamlit run "$TARGET" --server.address "$HOST" --server.port "$PORT"
