#!/usr/bin/env python3
"""
Streamlit runner for the RAG System.
Use this script to launch the application with proper configuration.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    # Get the path to the app.py file
    app_path = Path(__file__).parent / "app.py"
    
    # Run streamlit with the app
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_path),
        "--server.address", "localhost",
        "--server.port", "8502",
        "--theme.base", "light"
    ]
    
    print("Starting RAG System...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nShutting down RAG System...")
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()