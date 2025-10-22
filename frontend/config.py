# frontend/config.py
"""
Frontend configuration
Automatically uses correct backend URL based on environment
"""

import os
import streamlit as st
import socket

def is_local_environment():
    """Check if running in local environment"""
    try:
        # Try to connect to localhost:8000
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        return result == 0
    except:
        return False

def get_backend_url():
    """
    Get backend URL based on environment.
    
    Priority:
    1. Environment variable (highest priority)
    2. Local backend if detected (http://127.0.0.1:8000)
    3. Streamlit secrets (for deployed frontend)
    4. Default to production Render URL
    """
    
    # 1. Try environment variable FIRST (highest priority)
    url = os.getenv('BACKEND_URL')
    if url:
        print(f"✅ Using backend from environment variable: {url}")
        return url
    
    # 2. Check if local backend is running
    if is_local_environment():
        url = "http://127.0.0.1:8000"
        print(f"✅ Detected local backend running: {url}")
        return url
    
    # 3. Try Streamlit secrets (for deployed frontend)
    try:
        if hasattr(st, 'secrets') and 'BACKEND_URL' in st.secrets:
            url = st.secrets['BACKEND_URL']
            print(f"✅ Using backend from Streamlit secrets: {url}")
            return url
    except:
        pass
    
    # 4. Default to production Render URL
    url = "https://questai-backend-ga8s.onrender.com"
    print(f"✅ Using default production backend: {url}")
    return url

# Main backend URL
BACKEND_URL = get_backend_url()

# For local development, you can override by setting environment variable:
# set BACKEND_URL=http://127.0.0.1:8000  (Windows)
# export BACKEND_URL=http://127.0.0.1:8000  (Linux/Mac)