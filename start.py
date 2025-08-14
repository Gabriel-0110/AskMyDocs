#!/usr/bin/env python3
"""
Simple starter script for the RAG System.
Alternative to run.py that directly imports and runs the Streamlit app.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the main app content  # noqa: E402
from app import main  # noqa: E402

if __name__ == "__main__":
    # This allows running with: streamlit run start.py
    main()
