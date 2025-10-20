# frontend/pages/3_Match_Score.py
import streamlit as st
import requests
import sys
from pathlib import Path
from PyPDF2 import PdfReader
from config import BACKEND_URL

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_frontend_logging
import logging

# Setup logging
setup_frontend_logging()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Resume–Job Match Analyzer", page_icon="📊", layout="wide")

st.title("📊 Resume–Job Match Analyzer")
st.markdown("Upload your resume and the job description to check how well you match the role.")

# BACKEND_URL = "http://127.0.0.1:8000"

logger.info("=" * 70)
logger.info("Match Score page loaded")
logger.info("=" * 70)

logger.info(f"Using backend: {BACKEND_URL}")

# Helper to extract text
def extract_text(file):
    """Extract text from PDF or TXT file"""
    if file is None:
        return ""
    
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return "\n".join([page.extract_text() for page in reader.pages])
        elif file.type == "text/plain":
            return file.read().decode("utf-8")
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        st.error(f"Error reading file: {str(e)}")
    
    return ""

# File Upload Section
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("📄 Upload Resume", type=["pdf", "txt"])

with col2:
    jd_file = st.file_uploader("📑 Upload Job Description", type=["pdf", "txt"])

st.markdown("---")

# Match Score Button
if st.button("🔍 Check Match Score", use_container_width=True):
    logger.info("Check Match Score button clicked")
    
    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)

    if not resume_text or not jd_text:
        st.error("⚠️ Please upload both a resume and job description.")
        logger.warning("Missing resume or JD")
    else:
        logger.info("Calculating match score...")
        
        with st.spinner("Analyzing match score... ⏳"):
            try:
                res = requests.post(f"{BACKEND_URL}/match_score", json={
                    "resume_text": resume_text,
                    "jd_text": jd_text
                }, timeout=60)

                if res.status_code == 200:
                    result = res.json()
                    logger.info(f"Match score received: {result.get('match_percent', 'N/A')}%")

                    # Display Match Score
                    st.subheader("✅ Results")
                    st.metric("Match Score", f"{result.get('match_percent', 0)} %")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 💪 Strengths")
                        for s in result.get("strengths", []):
                            st.success(f"- {s}")

                    with col2:
                        st.markdown("### ⚠️ Gaps / Improvements")
                        for g in result.get("gaps", []):
                            st.warning(f"- {g}")
                else:
                    logger.error(f"Backend error: {res.status_code}")
                    st.error(f"❌ Error from backend: {res.text}")
            
            except Exception as e:
                logger.error(f"Error: {str(e)}", exc_info=True)
                st.error(f"❌ Error: {str(e)}")

logger.info("Match Score page rendered")