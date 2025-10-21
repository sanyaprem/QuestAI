# frontend/pages/Reports.py
import streamlit as st
import requests
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_frontend_logging
from config import BACKEND_URL
import logging

setup_frontend_logging()
logger = logging.getLogger(__name__)

st.title("📊 Interview Reports")

logger.info("=" * 70)
logger.info("Reports page loaded")
logger.info(f"Using backend: {BACKEND_URL}")
logger.info("=" * 70)

# Initialize session history in session state
if "session_history" not in st.session_state:
    st.session_state.session_history = []

# Check if we just completed an interview
if "session_id" in st.session_state and st.session_state.session_id:
    current_session = st.session_state.session_id
    
    # Add to history if not already there
    if current_session not in st.session_state.session_history:
        st.session_state.session_history.append(current_session)
        logger.info(f"Added session to history: {current_session}")

# Show options
st.markdown("""
View your interview reports in two ways:

1. **Recent Sessions** - Click on a recent interview session
2. **Manual Entry** - Enter a session ID if you have it saved
""")

st.markdown("---")

# Option 1: Recent Sessions
st.subheader("📋 Recent Interview Sessions")

if st.session_state.session_history:
    st.info(f"Found {len(st.session_state.session_history)} recent session(s)")
    
    for idx, session_id in enumerate(reversed(st.session_state.session_history), 1):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text(f"Session {idx}: {session_id}")
        
        with col2:
            if st.button(f"📄 View", key=f"view_{session_id}"):
                logger.info(f"Viewing report for session: {session_id}")
                
                with st.spinner("Fetching report..."):
                    try:
                        res = requests.get(
                            f"{BACKEND_URL}/report",
                            params={"session_id": session_id},
                            timeout=60
                        )
                        
                        if res.status_code == 200:
                            report = res.json()
                            logger.info("Report fetched successfully")
                            
                            # Display report
                            st.success("✅ Report Retrieved!")
                            
                            report_data = report.get("report", {})
                            
                            st.markdown("### 📈 Interview Report")
                            
                            if isinstance(report_data, dict):
                                if "strengths" in report_data:
                                    with st.expander("💪 Strengths", expanded=True):
                                        strengths = report_data.get("strengths", "N/A")
                                        if isinstance(strengths, list):
                                            for strength in strengths:
                                                st.success(f"✓ {strength}")
                                        else:
                                            st.write(strengths)
                                
                                if "weaknesses" in report_data:
                                    with st.expander("⚠️ Weaknesses"):
                                        weaknesses = report_data.get("weaknesses", "N/A")
                                        if isinstance(weaknesses, list):
                                            for weakness in weaknesses:
                                                st.warning(f"• {weakness}")
                                        else:
                                            st.write(weaknesses)
                                
                                if "recommendations" in report_data:
                                    with st.expander("📋 Recommendations"):
                                        recommendations = report_data.get("recommendations", "N/A")
                                        if isinstance(recommendations, list):
                                            for rec in recommendations:
                                                st.info(f"→ {rec}")
                                        else:
                                            st.write(recommendations)
                            else:
                                st.markdown(str(report_data))
                            
                            # Detailed answers
                            st.markdown("---")
                            st.markdown("### 📝 Detailed Answers")
                            
                            for idx, ans in enumerate(report.get("answers", []), 1):
                                with st.expander(f"Question {idx}"):
                                    st.markdown(f"**Q:** {ans['question']}")
                                    st.markdown(f"**A:** {ans['answer']}")
                                    st.markdown(f"**Eval:** {ans['evaluation']}")
                            
                            logger.info(f"Report displayed for session: {session_id}")
                        else:
                            st.error(f"❌ Failed: {res.status_code}")
                            logger.error(f"Failed to fetch report: {res.status_code}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        logger.error(f"Error: {str(e)}", exc_info=True)
else:
    st.warning("No recent sessions found. Complete an interview first!")
    st.info("💡 After completing an interview, come back here to view your report.")

st.markdown("---")

# Option 2: Manual Entry
st.subheader("🔍 Manual Session ID Entry")

with st.form("manual_session_form"):
    manual_session_id = st.text_input(
        "Enter Session ID",
        placeholder="e.g., a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        help="Paste your session ID here if you saved it"
    )
    
    submitted = st.form_submit_button("📄 Fetch Report", use_container_width=True)
    
    if submitted:
        if not manual_session_id:
            st.error("⚠️ Please enter a session ID")
        else:
            logger.info(f"Manual fetch for session: {manual_session_id}")
            
            with st.spinner("Fetching report..."):
                try:
                    res = requests.get(
                        f"{BACKEND_URL}/report",
                        params={"session_id": manual_session_id},
                        timeout=60
                    )
                    
                    if res.status_code == 200:
                        report = res.json()
                        logger.info("Report fetched successfully")
                        
                        # Add to history
                        if manual_session_id not in st.session_state.session_history:
                            st.session_state.session_history.append(manual_session_id)
                        
                        st.success("✅ Report Retrieved!")
                        
                        # Display report (same as above)
                        report_data = report.get("report", {})
                        
                        st.markdown("### 📈 Interview Report")
                        
                        if isinstance(report_data, dict):
                            if "strengths" in report_data:
                                with st.expander("💪 Strengths", expanded=True):
                                    st.write(report_data.get("strengths", "N/A"))
                            
                            if "weaknesses" in report_data:
                                with st.expander("⚠️ Weaknesses"):
                                    st.write(report_data.get("weaknesses", "N/A"))
                            
                            if "recommendations" in report_data:
                                with st.expander("📋 Recommendations"):
                                    st.write(report_data.get("recommendations", "N/A"))
                        else:
                            st.markdown(str(report_data))
                        
                        st.markdown("---")
                        st.markdown("### 📝 Detailed Answers")
                        
                        for idx, ans in enumerate(report.get("answers", []), 1):
                            with st.expander(f"Question {idx}"):
                                st.markdown(f"**Q:** {ans['question']}")
                                st.markdown(f"**A:** {ans['answer']}")
                                st.markdown(f"**Eval:** {ans['evaluation']}")
                        
                        logger.info(f"Report displayed")
                    else:
                        st.error(f"❌ Session not found or report unavailable")
                        logger.error(f"Failed: {res.status_code}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Error: {str(e)}", exc_info=True)

# Clear history option
st.markdown("---")
if st.session_state.session_history:
    if st.button("🗑️ Clear Session History"):
        st.session_state.session_history = []
        st.success("Session history cleared")
        logger.info("Session history cleared")
        st.rerun()

logger.info("Reports page rendered")