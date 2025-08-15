#!/bin/bash
set -e
# Use Oryx venv if present
if [ -d "antenv" ]; then . antenv/bin/activate; fi
python run.py
