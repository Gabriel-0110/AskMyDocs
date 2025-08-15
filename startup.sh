#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
HOST="0.0.0.0"

# detect where streamlit app actually is
if [ -f "streamlit_app.py" ]; then
  TARGET="streamlit_app.py"
elif [ -f "src/ui/streamlit_app.py" ]; then
  TARGET="src/ui/streamlit_app.py"
elif [ -f "AskMyDocs/streamlit_app.py" ]; then
  TARGET="AskMyDocs/streamlit_app.py"
else
  echo "❌ Could not find streamlit_app.py at repo root, src/ui, or AskMyDocs/"
  echo "Here are some top-level files for debugging:"
  ls -la
  echo "Searching up to 3 levels for streamlit_app.py..."
  find . -maxdepth 3 -name streamlit_app.py -print || true
  sleep 5
  exit 1
fi

exec python -m streamlit run "$TARGET" --server.address "$HOST" --server.port "$PORT"
