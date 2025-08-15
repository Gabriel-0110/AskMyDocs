#!/bin/bash
set -e

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install dependencies using uv
uv pip install -r requirements.txt

# Start Streamlit
streamlit run app.py --server.port=8000 --server.address=0.0.0.0
