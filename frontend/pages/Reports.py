# frontend/pages/Reports.py
import streamlit as st
import requests
import sys
from pathlib import Path
from config import BACKEND_URL

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_frontend_logging
import logging

# Setup logging
setup_frontend_logging()
logger = logging.getLogger(__name__)

# BACKEND_URL = "http://127.0.0.1:8000"

st.title("📊 Interview Reports")

logger.info("=" * 70)
logger.info("Reports page loaded")
logger.info("=" * 70)


logger.info(f"Using backend: {BACKEND_URL}")

session_id = st.text_input("Enter Session ID to view report")

if st.button("📄 Fetch Report"):
    logger.info(f"Fetch Report button clicked for session: {session_id}")
    
    if not session_id:
        st.error("⚠️ Enter a valid session ID")
        logger.warning("No session ID provided")
    else:
        logger.info(f"Fetching report for session: {session_id}")
        
        with st.spinner("Generating report..."):
            try:
                res = requests.get(f"{BACKEND_URL}/report", params={"session_id": session_id}, timeout=60)
                
                if res.status_code == 200:
                    report = res.json()
                    logger.info("Report fetched successfully")
                    
                    st.subheader("📈 Interview Report")
                    
                    # Display report
                    report_data = report.get("report", {})
                    
                    if isinstance(report_data, dict):
                        if "strengths" in report_data:
                            st.markdown("### 💪 Strengths")
                            st.write(report_data.get("strengths", "N/A"))
                        
                        if "weaknesses" in report_data:
                            st.markdown("### ⚠️ Weaknesses")
                            st.write(report_data.get("weaknesses", "N/A"))
                        
                        if "recommendations" in report_data:
                            st.markdown("### 📋 Recommendations")
                            st.write(report_data.get("recommendations", "N/A"))
                    else:
                        st.markdown(str(report_data))
                    
                    # Display detailed answers
                    st.markdown("---")
                    st.subheader("📝 Detailed Answers")
                    
                    for idx, ans in enumerate(report.get("answers", []), 1):
                        with st.expander(f"Question {idx}"):
                            st.markdown(f"**Q:** {ans['question']}")
                            st.markdown(f"**A:** {ans['answer']}")
                            st.markdown(f"**Eval:** {ans['evaluation']}")
                    
                    logger.info(f"Displayed report with {len(report.get('answers', []))} answers")
                else:
                    logger.error(f"Failed to fetch report: {res.status_code}")
                    st.error(f"❌ Failed to fetch report: {res.status_code}")
            
            except Exception as e:
                logger.error(f"Error fetching report: {str(e)}", exc_info=True)
                st.error(f"❌ Error: {str(e)}")

logger.info("Reports page rendered")