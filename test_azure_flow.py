import os
import sys
import streamlit as st

# Set page config FIRST (before any other Streamlit commands)
st.set_page_config(
    page_title="Azure Flow Test • AskMyDocs", 
    page_icon="🧪", 
    layout="wide"
)

# Add src/ui to Python path so imports work
sys.path.insert(0, "src/ui")
sys.path.insert(0, "src")

# Force Azure mode for complete testing
os.environ["AUTH_MODE"] = "azure"
os.environ["WEBSITE_SITE_NAME"] = "test-app"

# Page selection in sidebar
st.sidebar.title("🧪 Azure Mode Test")
page = st.sidebar.selectbox(
    "Choose page to test:",
    ["Login Page", "Main App", "Logout Page"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Current Mode:** Azure (EasyAuth enabled)")
st.sidebar.markdown("**Environment Variables:**")
st.sidebar.code(f"AUTH_MODE={os.getenv('AUTH_MODE')}")
st.sidebar.code(f"WEBSITE_SITE_NAME={os.getenv('WEBSITE_SITE_NAME')}")

# Helper function to read file and remove set_page_config lines
def load_page_content(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove set_page_config lines to avoid conflicts
    lines = content.split('\n')
    filtered_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if 'st.set_page_config(' in line:
            # Skip this line and continue until we find the closing parenthesis
            skip_next = True
            continue
        elif skip_next:
            if ')' in line and not line.strip().startswith('#'):
                skip_next = False
            continue
        else:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)

# Display selected page
if page == "Login Page":
    st.title("🔐 Testing Login Page")
    st.info("This page shows the Azure login providers and auto-redirect logic.")
    content = load_page_content("src/ui/login.py")
    exec(content)

elif page == "Main App":
    st.title("📚 Testing Main App") 
    st.info("This page shows the main RAG system with authentication guard.")
    content = load_page_content("src/ui/streamlit_app.py")
    exec(content)

elif page == "Logout Page":
    st.title("🚪 Testing Logout Page")
    st.info("This page shows the logout confirmation with proper navigation.")
    content = load_page_content("src/ui/logout.py")
    exec(content)