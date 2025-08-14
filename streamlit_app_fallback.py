"""
Self-contained RAG Streamlit App for deployment.
All dependencies are installed inline.
"""

import streamlit as st
import sys
import subprocess
from pathlib import Path

# Force install packages if they don't exist
def ensure_package(package_name, import_name=None):
    """Ensure a package is installed, install if not."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        st.info(f"Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            __import__(import_name)
            return True
        except Exception as e:
            st.error(f"Failed to install {package_name}: {e}")
            return False

# Page config
st.set_page_config(
    page_title="AskMyDocs - AI Document Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📚 AskMyDocs - AI Document Q&A")

# Try to ensure all packages are available
required_packages = [
    ("tiktoken", "tiktoken"),
    ("openai", "openai"),
    ("supabase", "supabase"),
    ("python-dotenv", "dotenv"),
    ("PyPDF2", "PyPDF2")
]

st.info("🔧 Checking and installing dependencies...")

all_packages_ok = True
for package_name, import_name in required_packages:
    if not ensure_package(package_name, import_name):
        all_packages_ok = False

if all_packages_ok:
    st.success("✅ All packages are available!")
    
    # Now try to import and run the main app
    try:
        # Add project paths
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "src"))
        
        # Load environment
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass
            
        # Import the main app
        from src.ui.streamlit_app import RAGStreamlitApp
        
        # Run the app
        app = RAGStreamlitApp()
        app.run()
        
    except Exception as e:
        st.error(f"❌ Error running application: {e}")
        
        # Fallback simple interface
        st.markdown("---")
        st.markdown("## 🔧 Fallback Mode")
        st.info("The main application couldn't load. Here's a basic interface:")
        
        user_question = st.text_input("Ask a question about your documents:")
        if user_question:
            st.info("⏳ This feature requires the full application to be loaded.")
            st.markdown("Please check the error messages above and try redeploying.")

else:
    st.error("❌ Some required packages could not be installed.")
    st.info("Please check your deployment environment and requirements.txt file.")
