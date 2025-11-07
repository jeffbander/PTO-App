import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Flask app
from app import app

# Export for Vercel
# Vercel will use this as the WSGI application
application = app
