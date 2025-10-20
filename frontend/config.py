# frontend/config.py
"""
Frontend configuration
Automatically uses correct backend URL based on environment
"""

import os
import streamlit as st

def get_backend_url():
    """
    Get backend URL based on environment.
    
    Priority:
    1. Streamlit secrets (for deployed frontend)
    2. Environment variable
    3. Default to production Render URL
    """
    
    # Try Streamlit secrets first (if frontend is also deployed)
    try:
        if hasattr(st, 'secrets') and 'BACKEND_URL' in st.secrets:
            url = st.secrets['BACKEND_URL']
            print(f"✅ Using backend from Streamlit secrets: {url}")
            return url
    except:
        pass
    
    # Try environment variable
    url = os.getenv('BACKEND_URL')
    if url:
        print(f"✅ Using backend from environment: {url}")
        return url
    
    # Default to production Render URL
    url = "https://questai-backend-ga8s.onrender.com"
    print(f"✅ Using default production backend: {url}")
    return url

# Main backend URL
BACKEND_URL = get_backend_url()

# For local development, you can override by setting environment variable:
# set BACKEND_URL=http://127.0.0.1:8000  (Windows)
# export BACKEND_URL=http://127.0.0.1:8000  (Linux/Mac)