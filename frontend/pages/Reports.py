# frontend/pages/Reports.py
import streamlit as st
import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_frontend_logging
from config import BACKEND_URL
import logging

setup_frontend_logging()
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Reports - QuestAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    .header-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #e0e7ff;
        font-size: 1.2rem;
        font-weight: 300;
    }
    
    .session-card {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .session-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        background: #273548;
    }
    
    .session-id {
        font-family: 'Consolas', monospace;
        color: #94a3b8;
        font-size: 0.9rem;
    }
    
    .section-container {
        background: #1e293b;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        background: #1e293b;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Global dark mode */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #cbd5e1 !important;
    }
    
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        color: #86efac !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        color: #fbbf24 !important;
    }
    
    .stInfo {
        background: rgba(102, 126, 234, 0.1) !important;
        color: #a5b4fc !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    
    h4 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
</style>
''', unsafe_allow_html=True)

logger.info("=" * 70)
logger.info("Reports page loaded")
logger.info(f"Using backend: {BACKEND_URL}")
logger.info("=" * 70)

# Page Header
st.markdown('''
<div class="header-card">
    <h1 class="header-title">📊 Interview Reports</h1>
    <p class="header-subtitle">Review your past interview performances and track your progress</p>
</div>
''', unsafe_allow_html=True)

# Initialize session history
if "session_history" not in st.session_state:
    st.session_state.session_history = []

# Check if we just completed an interview
if "session_id" in st.session_state and st.session_state.session_id:
    current_session = st.session_state.session_id
    if current_session not in st.session_state.session_history:
        st.session_state.session_history.append(current_session)
        logger.info(f"Added session to history: {current_session}")

# ===== RECENT SESSIONS =====
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<h3 class="section-title">📋 Recent Interview Sessions</h3>', unsafe_allow_html=True)

if st.session_state.session_history:
    st.success(f"✓ Found **{len(st.session_state.session_history)}** recent session(s)")
    
    for idx, session_id in enumerate(reversed(st.session_state.session_history), 1):
        st.markdown('<div class="session-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"**Session {idx}**")
        
        with col2:
            st.markdown(f'<div class="session-id">{session_id}</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button(f"📄 View Report", key=f"view_{session_id}", use_container_width=True):
                logger.info(f"Viewing report for session: {session_id}")
                
                with st.spinner("📥 Fetching report..."):
                    try:
                        res = requests.get(
                            f"{BACKEND_URL}/report",
                            params={"session_id": session_id},
                            timeout=60
                        )
                        
                        if res.status_code == 200:
                            report = res.json()
                            logger.info("Report fetched successfully")
                            
                            # Display full report
                            st.markdown("---")
                            st.success("✅ Report Retrieved Successfully!")
                            
                            report_data = report.get("report", {})
                            
                            # Summary Section
                            st.markdown("---")
                            st.markdown("### 📈 Interview Summary")
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            if isinstance(report_data, dict):
                                sum_col1, sum_col2, sum_col3 = st.columns(3)
                                
                                with sum_col1:
                                    st.markdown("#### 💪 Strengths")
                                    strengths = report_data.get("strengths", [])
                                    if isinstance(strengths, list) and strengths:
                                        for strength in strengths:
                                            st.success(f"✓ {strength}")
                                    elif strengths:
                                        st.write(strengths)
                                    else:
                                        st.info("No strengths data available")
                                
                                with sum_col2:
                                    st.markdown("#### ⚠️ Areas to Improve")
                                    weaknesses = report_data.get("weaknesses", [])
                                    if isinstance(weaknesses, list) and weaknesses:
                                        for weakness in weaknesses:
                                            st.warning(f"• {weakness}")
                                    elif weaknesses:
                                        st.write(weaknesses)
                                    else:
                                        st.info("No weaknesses data available")
                                
                                with sum_col3:
                                    st.markdown("#### 📋 Recommendations")
                                    recommendations = report_data.get("recommendations", [])
                                    if isinstance(recommendations, list) and recommendations:
                                        for rec in recommendations:
                                            st.info(f"→ {rec}")
                                    elif recommendations:
                                        st.write(recommendations)
                                    else:
                                        st.info("No recommendations available")
                            else:
                                st.markdown(str(report_data))
                            
                            # Detailed answers
                            st.markdown("---")
                            st.markdown("### 📝 Detailed Q&A Review")
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            for idx_q, ans in enumerate(report.get("answers", []), 1):
                                st.markdown(f"#### Question {idx_q}")
                                
                                st.markdown("**❓ Question:**")
                                st.info(ans['question'])
                                
                                st.markdown("**💬 Your Answer:**")
                                with st.expander("View Answer", expanded=False):
                                    st.text(ans['answer'])
                                
                                st.markdown("**📊 Evaluation:**")
                                eval_data = ans['evaluation']
                                if isinstance(eval_data, dict):
                                    eval_col1, eval_col2 = st.columns([1, 4])
                                    with eval_col1:
                                        score = eval_data.get('score', 'N/A')
                                        st.metric("Score", f"{score}/10")
                                    with eval_col2:
                                        feedback = eval_data.get('feedback', 'No feedback')
                                        st.markdown(f"**Feedback:** {feedback}")
                                        
                                        if eval_data.get('recommendations'):
                                            st.markdown("**💡 Recommendations:**")
                                            for rec in eval_data['recommendations']:
                                                st.write(f"- {rec}")
                                else:
                                    st.write(eval_data)
                                
                                st.markdown("---")
                            
                            # Download option
                            download_report = f'''
QuestAI Interview Report
========================
Session ID: {session_id}

{report_data if isinstance(report_data, str) else str(report_data)}

Detailed Answers:
'''
                            for idx_d, ans in enumerate(report.get("answers", []), 1):
                                download_report += f"\n\nQ{idx_d}: {ans['question']}\n"
                                download_report += f"A{idx_d}: {ans['answer']}\n"
                                download_report += f"Eval: {ans['evaluation']}\n"
                            
                            st.download_button(
                                label="📥 Download Full Report",
                                data=download_report,
                                file_name=f"report_{session_id[:8]}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                            logger.info(f"Report displayed for session: {session_id}")
                        else:
                            st.error(f"❌ Failed to fetch report: Status {res.status_code}")
                            logger.error(f"Failed to fetch report: {res.status_code}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        logger.error(f"Error: {str(e)}", exc_info=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Empty state
    st.markdown('''
    <div class="empty-state">
        <div class="empty-icon">📭</div>
        <h3 style="color: #64748b; margin-bottom: 0.5rem;">No Recent Sessions Found</h3>
        <p style="color: #94a3b8; margin-bottom: 1.5rem;">
            Complete an interview to see your reports here
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    col_e1, col_e2, col_e3 = st.columns([1, 2, 1])
    
    with col_e2:
        st.markdown("**Start an interview now:**")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🎓 Teach Mode", use_container_width=True):
                st.switch_page("pages/1_Teach_Mode.py")
        
        with col_btn2:
            if st.button("💼 Experience Mode", use_container_width=True):
                st.switch_page("pages/2_Experience_Mode.py")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ===== HISTORY MANAGEMENT =====
if st.session_state.session_history:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns([3, 1])
    
    with col_h1:
        st.markdown(f"**Session History:** {len(st.session_state.session_history)} session(s) stored")
    
    with col_h2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.session_history = []
            st.success("✅ Session history cleared")
            logger.info("Session history cleared")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

logger.info("Reports page rendered")