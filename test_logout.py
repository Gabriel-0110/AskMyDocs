import os
import sys

# Add src/ui to Python path so imports work
sys.path.insert(0, "src/ui")
sys.path.insert(0, "src")

# Force Azure mode to see logout functionality
os.environ["AUTH_MODE"] = "azure"

# Now import and run the logout page with proper encoding
with open("src/ui/logout.py", "r", encoding="utf-8") as f:
    exec(f.read())