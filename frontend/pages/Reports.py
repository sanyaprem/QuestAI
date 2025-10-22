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
    initial_sidebar_state="collapsed"
)

# ------------------------------ CSS STYLING ------------------------------
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

/* Global reset */
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

/* App background */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* Center main content */
.main .block-container, div.block-container, main[role="main"] > div {
    max-width: 1150px !important;
    margin: 0 auto !important;
    padding: 2rem 2rem 5rem !important;
}

/* Header */
.header-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem 2rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 35px rgba(102, 126, 234, 0.3);
}

.header-title {
    color: white;
    font-size: 2.6rem;
    font-weight: 800;
    margin-bottom: 0.6rem;
}

.header-subtitle {
    color: #e0e7ff;
    font-size: 1.15rem;
    font-weight: 400;
}

/* Section container */
.section-container {
    background: #1e293b;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 25px rgba(0,0,0,0.25);
    margin: 2rem 0;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Section title */
.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 1rem;
    border-left: 4px solid #667eea;
    padding-left: 1rem;
}

/* Session card base style */
.session-card {
    width: 100%;
    background: #1e293b;
    padding: 1.25rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.25rem;
    box-shadow: 0 3px 12px rgba(0,0,0,0.3);
    border-left: 4px solid #667eea;
    transition: all 0.28s ease;
}

/* We'll display session-card as a 2-col grid: content | actions */
.session-card-inner {
    display: grid;
    grid-template-columns: 1fr 300px;
    column-gap: 20px;
    align-items: start;
}

/* Left content */
.session-title {
    margin: 0 0 6px 0;
    color: #f1f5f9;
    font-weight: 700;
}
.session-id {
    font-family: monospace;
    color: #94a3b8;
    font-size: 0.9rem;
    word-break: break-all;
    margin-top: 6px;
    display: none; /* hide by default - prevents layout stretching */
}

/* Right actions wrapper - stacked vertically */
.session-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: flex-end;
    justify-content: flex-start;
}

/* Streamlit button style override in actions area */
.session-actions .stButton > button {
    max-width: 220px;
    width: 220px;
    padding: 10px 16px;
    border-radius: 10px;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 6px 18px rgba(102,126,234,0.25);
}

/* Success/info boxes in actions area */
.session-actions .stSuccess,
.session-actions .stInfo,
.session-actions .stWarning {
    width: 220px !important;
    max-width: 220px !important;
    text-align: left !important;
    padding: 12px !important;
    border-radius: 10px !important;
    box-sizing: border-box !important;
    align-self: flex-start !important;
}

/* Summary + question layout */
.centered-heading {
    text-align: center;
    color: #f1f5f9;
    font-weight: 800;
    margin: 2.25rem 0 1rem;
    font-size: 1.9rem;
}

/* Report summary columns */
.report-summary {
    width: 100%;
    margin-top: 1rem;
}
.report-summary .stSuccess,
.report-summary .stWarning,
.report-summary .stInfo {
    width: 100% !important;
    max-width: 100% !important;
}

/* question header */
.question-header {
    color: #667eea;
    font-size: 1.15rem;
    font-weight: 700;
    margin: 1.25rem 0 0.75rem;
    padding: 0.75rem;
    background: rgba(102,126,234,0.07);
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

/* Hide empty rounded placeholders Streamlit sometimes renders */
div[data-testid="stHorizontalBlock"] > div:empty,
div[data-testid="stVerticalBlock"] > div:empty,
div.element-container > div:empty {
    display: none !important;
}

/* ---------- Overrides for Streamlit generated column flexing inside session-card ---------- */
/* Apply only inside session-card-inner - this is resilient to Streamlit's 'st-emotion-cache-...' classes */
.session-card-inner [data-testid="stColumn"]:first-child {
    flex: 0 0 70% !important;
    width: 70% !important;
    align-self: center !important;
    height: auto !important;
}
.session-card-inner [data-testid="stColumn"]:last-child {
    flex: 0 0 25% !important;
    width: 25% !important;
    align-self: center !important;
    height: auto !important;
}

/* If Streamlit injects wrapper divs, hide any large vertical block inside session-card */
.session-card .stVerticalBlock, .session-card .stHorizontalBlock, .session-card .stMarkdown {
    max-height: none !important;
}

/* Responsive */
@media (max-width: 900px) {
    .session-card-inner {
        grid-template-columns: 1fr !important;
        gap: 12px;
        text-align: center;
    }
    .session-actions .stButton > button,
    .session-actions .stSuccess,
    .session-actions .stInfo,
    .session-actions .stWarning {
        width: 100% !important;
        max-width: 100% !important;
        align-self: center !important;
    }
}

/* small visual polish */
.session-card:hover {
    transform: translateY(-3px);
    background: #273548;
    box-shadow: 0 8px 22px rgba(102,126,234,0.12);
}
</style>
''', unsafe_allow_html=True)

logger.info("=" * 70)
logger.info("Reports page loaded")
logger.info(f"Using backend: {BACKEND_URL}")
logger.info("=" * 70)

# ------------------------------ PAGE HEADER ------------------------------
st.markdown('''
<div class="header-card">
    <h1 class="header-title">📊 Interview Reports</h1>
    <p class="header-subtitle">Review your past interview performances and track your progress</p>
</div>
''', unsafe_allow_html=True)

# Initialize session history
if "session_history" not in st.session_state:
    st.session_state.session_history = []

# If we have a current session id saved elsewhere, include it
if "session_id" in st.session_state and st.session_state.session_id:
    current_session = st.session_state.session_id
    if current_session not in st.session_state.session_history:
        st.session_state.session_history.append(current_session)
        logger.info(f"Added session to history: {current_session}")

# ------------------------------ RECENT SESSIONS ------------------------------
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown('<h3 class="section-title">📋 Recent Interview Sessions</h3>', unsafe_allow_html=True)

if st.session_state.session_history:
    st.success(f"✓ Found **{len(st.session_state.session_history)}** recent session(s)")

    # iterate through sessions
    for idx, session_id in enumerate(reversed(st.session_state.session_history), 1):
        # session card wrapper
        st.markdown('<div class="session-card">', unsafe_allow_html=True)
        # inner grid that separates left content and right actions
        st.markdown('<div class="session-card-inner">', unsafe_allow_html=True)

        # Left column: title (we deliberately DO NOT render the long session-id here to prevent layout stretch)
        st.markdown(f'''
            <div>
                <h3 class="session-title">📁 Session {idx}</h3>
                <!-- session-id intentionally omitted to avoid layout issues -->
            </div>
        ''', unsafe_allow_html=True)

        # Right column: actions (button + status)
        # We'll render a container and place the Streamlit button inside it
        st.markdown('<div class="session-actions">', unsafe_allow_html=True)
        # Use a unique key per session button
        if st.button("📄 View Report", key=f"view_{session_id}", help=f"View report for {session_id}", use_container_width=False):
            logger.info(f"Clicked view report for session: {session_id}")
            with st.spinner("📥 Fetching report..."):
                try:
                    res = requests.get(
                        f"{BACKEND_URL}/report",
                        params={"session_id": session_id},
                        timeout=60
                    )
                    if res.status_code == 200:
                        st.session_state[f"report_{session_id}"] = res.json()
                        st.session_state["viewing_report"] = session_id
                        logger.info(f"Saved report in session_state for: {session_id}")
                        # rerun so rendering happens in full-width area below
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to fetch report: Status {res.status_code}")
                        logger.error(f"Failed to fetch report: {res.status_code}")
                except Exception as e:
                    st.error(f"❌ Error fetching report: {str(e)}")
                    logger.error(f"Error fetching report: {e}", exc_info=True)

        # show a success box if we have a stored report for this session
        if f"report_{session_id}" in st.session_state:
            st.success("✅ Report Retrieved Successfully!")
        # close actions container
        st.markdown('</div>', unsafe_allow_html=True)

        # close inner and card wrappers
        st.markdown('</div>', unsafe_allow_html=True)
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

# ------------------------------ DISPLAY THE SELECTED REPORT (FULL WIDTH) ------------------------------
if "viewing_report" in st.session_state and st.session_state["viewing_report"]:
    viewing_id = st.session_state["viewing_report"]
    report_obj = st.session_state.get(f"report_{viewing_id}", None)

    if report_obj is None:
        st.error("❌ Report data not found.")
    else:
        report_data = report_obj.get("report", {})

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<h2 class="centered-heading">📈 Interview Summary</h2>', unsafe_allow_html=True)

        # full-width report summary - three columns
        st.markdown('<div class="report-summary">', unsafe_allow_html=True)
        sum_col1, sum_col2, sum_col3 = st.columns(3)
        with sum_col1:
            st.markdown("#### 💪 Strengths")
            strengths = report_data.get("strengths", [])
            if isinstance(strengths, list) and strengths:
                for s in strengths:
                    st.success(f"✓ {s}")
            else:
                st.info("No strengths data available")
        with sum_col2:
            st.markdown("#### ⚠️ Areas to Improve")
            weaknesses = report_data.get("weaknesses", [])
            if isinstance(weaknesses, list) and weaknesses:
                for w in weaknesses:
                    st.warning(f"• {w}")
            else:
                st.info("No weaknesses data available")
        with sum_col3:
            st.markdown("#### 📋 Recommendations")
            recommendations = report_data.get("recommendations", [])
            if isinstance(recommendations, list) and recommendations:
                for r in recommendations:
                    st.info(f"→ {r}")
            else:
                st.info("No recommendations available")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<h2 class="centered-heading">📝 Detailed Q&A Review</h2>', unsafe_allow_html=True)

        for i, ans in enumerate(report_obj.get("answers", []), 1):
            st.markdown(f'<div class="question-header">Question {i}</div>', unsafe_allow_html=True)
            st.info(ans.get('question', 'No question text'))
            with st.expander("💬 View Answer"):
                st.text(ans.get('answer', 'No answer'))
            st.markdown("**📊 Evaluation:**")
            eval_data = ans.get('evaluation', {})
            if isinstance(eval_data, dict):
                eval_col1, eval_col2 = st.columns([1, 4])
                with eval_col1:
                    st.metric("Score", f"{eval_data.get('score', 'N/A')}/10")
                with eval_col2:
                    st.markdown(f"**Feedback:** {eval_data.get('feedback', 'No feedback')}")
                    for rec in eval_data.get('recommendations', []):
                        st.write(f"- {rec}")
            else:
                st.write(eval_data)

        # Download button / Close report (keeps fetched report in session_state unless user closes)
        st.markdown("<hr>", unsafe_allow_html=True)
        download_report = f"QuestAI Interview Report\nSession ID: {viewing_id}\n\n"
        download_report += str(report_data) + "\n\nDetailed Answers:\n"
        for idx_d, ans in enumerate(report_obj.get("answers", []), 1):
            download_report += f"\nQ{idx_d}: {ans.get('question', '')}\n"
            download_report += f"A{idx_d}: {ans.get('answer', '')}\n"
            download_report += f"Eval: {ans.get('evaluation', '')}\n"

        st.download_button(
            label="📥 Download Full Report",
            data=download_report,
            file_name=f"report_{viewing_id[:8]}.txt",
            mime="text/plain",
            use_container_width=False
        )

        if st.button("Close Report", key=f"close_{viewing_id}"):
            st.session_state["viewing_report"] = None
            # optionally keep report in session_state for future quick view
            st.rerun()

logger.info("Reports page rendered")
