# frontend/Home.py
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import logging_config
sys.path.insert(0, str(Path(__file__).parent))

from logging_config import setup_frontend_logging
import logging

# Setup logging
setup_frontend_logging()
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="QuestAI - Interview Assistant", 
    page_icon="🤖", 
    layout="wide"
)

logger.info("=" * 70)
logger.info("Home page loaded")
logger.info("=" * 70)


st.set_page_config(
    page_title="QuestAI - Interview Assistant", 
    page_icon="🤖", 
    layout="wide"
)

logger.info("Home page loaded")

st.title("🤖 QuestAI")
st.subheader("Your AI-powered Interview Partner")

st.markdown("""
Welcome to **QuestAI**!  
This platform simulates interviews with **multi-agent AI**.

You can try two modes:

- 🎓 **Teach Mode** – Guided practice with retries and coaching after feedback.  
- 🧑‍💼 **Experience Mode** – Realistic mock interview simulation.  
- 📊 **Match Score** – Check how well your resume matches the job.
- 📊 **Reports** – View a structured report of your performance.  

👉 Use the left sidebar to navigate between modes.
""")

# Check backend status
st.markdown("---")
st.subheader("Backend Status")

try:
    import requests
    from config import BACKEND_URL as DEFAULT_BACKEND_URL
    BACKEND_URL = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL)
    
    if st.button("Check Backend"):
        logger.info(f"Checking backend at: {BACKEND_URL}")
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Backend is running!")
                st.json(data)
                logger.info("Backend health check successful")
            else:
                st.error(f"❌ Backend returned status: {response.status_code}")
                logger.error(f"Backend health check failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Cannot connect to backend: {str(e)}")
            logger.error(f"Backend connection failed: {str(e)}")
except Exception as e:
    st.warning(f"Cannot check backend status: {e}")

logger.info("Home page rendered successfully")