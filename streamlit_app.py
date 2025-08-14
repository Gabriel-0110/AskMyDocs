"""
Main Streamlit application for AskMyDocs RAG System.
Entry point for Streamlit Community Cloud deployment.
"""

import sys
from pathlib import Path
import streamlit as st

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Load environment variables for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # In production, secrets are handled by Streamlit Cloud

# Set page config first (must be at top level for Streamlit Cloud)
st.set_page_config(
    page_title="AskMyDocs - AI Document Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Gabriel-0110/AskMyDocs',
        'Report a bug': 'https://github.com/Gabriel-0110/AskMyDocs/issues',
        'About': "# AskMyDocs\nAI-powered document Q&A system built with Streamlit, OpenAI, and Supabase."
    }
)

# Import and run the Streamlit UI directly
try:
    from src.ui.streamlit_app import RAGStreamlitApp
    
    # Create and run the app
    app = RAGStreamlitApp()
    app.run()
    
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.info("Make sure all dependencies are installed and the project structure is correct.")
except Exception as e:
    st.error(f"Application error: {e}")
    st.info("Please check the logs for more details.")
