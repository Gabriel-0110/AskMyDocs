#!/bin/bash
set -e

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install dependencies using uv
uv pip install -r requirements.txt

# Start your app
python run.py
