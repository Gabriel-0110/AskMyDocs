#!/usr/bin/env bash
set -euo pipefail
export STREAMLIT_SERVER_HEADLESS=true
PORT="${PORT:-8000}"
exec python -m streamlit run src/ui/streamlit_app.py \
  --server.address 0.0.0.0 \
  --server.port "$PORT"
