#!/bin/bash
set -e
if [ -d "antenv" ]; then . antenv/bin/activate; fi
python run.py
