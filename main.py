import sys
import os

# Add the backend directory to sys.path so all relative imports inside backend/ resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Now import app - this works because 'backend' is on sys.path, so 'main' refers to backend/main.py
from main import app
