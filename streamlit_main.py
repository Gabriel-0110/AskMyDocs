#!/usr/bin/env python3
"""Main entry point for the RAG System Streamlit app."""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def main():
    """Run the Streamlit application."""
    try:
        from src.ui.streamlit_app import main as app_main

        # Run the Streamlit app
        app_main()

    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please make sure you have installed all dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting the application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
