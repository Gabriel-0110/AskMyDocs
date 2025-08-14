"""
Main application entry point for the RAG System.
Handles environment setup and launches the Streamlit UI.
"""

import os
import sys
from pathlib import Path
import logging

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
from config.settings import settings
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=settings.log_file
)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, settings.log_level))
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger(__name__)


def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        return False
    
    return True


def main():
    """Main function to start the application."""
    logger.info("Starting RAG System application")
    
    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed. Exiting.")
        sys.exit(1)
    
    logger.info("Environment validation passed")
    
    try:
        # Import and run the Streamlit app
        from src.ui.streamlit_app import main as streamlit_main
        streamlit_main()
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()