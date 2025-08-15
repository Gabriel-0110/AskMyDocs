#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8000}"
exec python -m streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port "$PORT"
# This script starts a Streamlit application on the specified port.