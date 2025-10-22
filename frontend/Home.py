# frontend/Home.py
import streamlit as st
import sys
from pathlib import Path
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from logging_config import setup_frontend_logging
from config import BACKEND_URL
import logging

# Setup logging
setup_frontend_logging()
logger = logging.getLogger(__name__)

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="QuestAI - AI Interview Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

logger.info("=" * 70)
logger.info("Home page loaded")
logger.info(f"Backend URL: {BACKEND_URL}")
logger.info("=" * 70)

# Custom CSS for modern, attractive UI
st.markdown('''
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Global font */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background - Dark Mode */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Hero section */
    /* ---------- Strong hero centering (place at END of your CSS) ---------- */
    .hero-container {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;        /* center children horizontally */
        justify-content: center !important;    /* center vertically if height present */
        padding: 3rem 1.25rem 2.5rem !important;
        margin: 0 auto !important;
        width: 100% !important;
        max-width: 1100px !important;          /* container width for visual balance */
        box-sizing: border-box !important;
    }
    
    /* Title stays large but keep responsive bounds */
    .hero-title {
        font-size: 4.2rem !important;
        line-height: 1 !important;
        margin: 0.2rem 0 0.6rem !important;
        text-align: center !important;
    }
    
    /* Subtitle centered with slightly increased weight for legibility */
    .hero-subtitle {
        font-size: 1.6rem !important;
        color: #cbd5e1 !important;
        margin: 0 0 0.9rem !important;
        font-weight: 400 !important;
        text-align: center !important;
        letter-spacing: 0.25px !important;
    }
    
    /* Constrain and center the description precisely */
    .hero-description {
        font-size: 1.06rem !important;
        color: #a9b7d0 !important;
        max-width: 760px !important;           /* match visual width to title */
        width: 100% !important;
        margin: 0 auto 2.5rem !important;      /* centers horizontally */
        text-align: center !important;         /* center text lines */
        line-height: 1.75 !important;
        font-weight: 300 !important;
        padding: 0 1rem !important;            /* breathing space on narrow screens */
        box-sizing: border-box !important;
    }
    
    /* If Streamlit wraps your HTML in extra divs, catch them */
    .hero-container > div, 
    .hero-container .stMarkdown, 
    .hero-container .stMarkdown > div {
        width: 100% !important;
        max-width: 1100px !important;
        margin: 0 auto !important;
    }
    
    /* Mobile tweaks — keep everything centered and readable */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.6rem !important; }
        .hero-subtitle { font-size: 1.05rem !important; margin-bottom: 0.6rem !important; }
        .hero-description { 
            font-size: 0.98rem !important; 
            max-width: 92% !important; 
            margin-bottom: 1.8rem !important;
            line-height: 1.6 !important;
        }
    }


    
    /* Stats bar */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem auto;
        padding: 0 2rem;
        max-width: 1400px;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .stat-number {
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        display: block;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #cbd5e1;
        font-weight: 500;
    }
    
    /* Mode cards - Dark Mode */
    .mode-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 2.5rem 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        border: 2px solid rgba(255, 255, 255, 0.1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .mode-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .mode-card:hover::before {
        transform: scaleX(1);
    }
    
    .mode-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 30px 80px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
        background: #273548;
    }
    
    .mode-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    
    .mode-title {
        font-size: 2rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 1rem;
    }
    
    .mode-description {
        font-size: 1.05rem;
        color: #cbd5e1;
        line-height: 1.7;
        margin-bottom: 1.5rem;
    }
    
    .mode-features {
        text-align: left;
        margin: 1.5rem 0;
        padding-left: 0;
    }
    
    .mode-features li {
        color: #94a3b8;
        margin: 0.8rem 0;
        font-size: 0.95rem;
        list-style: none;
        padding-left: 1.5rem;
        position: relative;
    }
    
    .mode-features li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #667eea;
        font-weight: 800;
        font-size: 1.2rem;
    }
    
    /* Feature cards - Dark Mode */
    .feature-card {
        background: #1e293b;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2);
        background: #273548;
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.8rem;
    }
    
    .feature-description {
        font-size: 1rem;
        color: #cbd5e1;
        line-height: 1.6;
    }
    
/* Steps section - perfectly aligned like Step 01 */
.steps-container {
    max-width: 1200px;
    margin: 3rem auto;
    padding: 0 2rem;
    display: flex;
    flex-direction: column;
    gap: 2.5rem;
}

.step {
    display: flex;
    align-items: center;                /* vertically center number + card */
    justify-content: flex-start;
    gap: 2rem;
    position: relative;
    animation: slideIn 0.6s ease;
}

.step-number {
    font-size: 3.5rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.25);
    min-width: 90px;
    text-align: center;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 0;                      /* ensure number aligns to vertical center */
}

.step-content {
    flex: 1;
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 2rem 2.2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}

.step-content:hover {
    transform: translateY(-3px);
    border-color: rgba(102, 126, 234, 0.4);
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.25);
}

.step-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.step-description {
    color: #cbd5e1;
    line-height: 1.7;
    font-size: 1.05rem;
    margin: 0;
}

/* Responsive alignment */
@media (max-width: 900px) {
    .step {
        flex-direction: column;
        align-items: flex-start;
        text-align: left;
        gap: 1rem;
    }

    .step-number {
        font-size: 2.8rem;
        text-align: left;
        margin-bottom: 0.5rem;
        justify-content: flex-start;
    }

    .step-content {
        width: 100%;
        padding: 1.5rem;
    }
}

    /* Backend status - Dark Mode */
    .status-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 2rem auto;
        max-width: 800px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .hero-subtitle { font-size: 1.2rem; }
        .hero-description { font-size: 1rem; }
        .step { flex-direction: column; text-align: center; }
        .step-number { min-width: auto; }
        .mode-icon { font-size: 3rem; }
        .mode-title { font-size: 1.5rem; }
    }
    
    /* Global Streamlit widget dark mode overrides */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #cbd5e1 !important;
    }
    
    /* Success/Warning/Error/Info boxes dark mode */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1) !important;
        color: #86efac !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        color: #fbbf24 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        color: #fca5a5 !important;
    }
    
    .stInfo {
        background: rgba(102, 126, 234, 0.1) !important;
        color: #a5b4fc !important;
    }
    
    /* Expander dark mode */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #f1f5f9 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Metric labels */
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    
    /* Column backgrounds */
    [data-testid="column"] {
        background: transparent !important;
    }
    
    /* Custom button styling - Dark Mode */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
''', unsafe_allow_html=True)

# Hero Section
st.markdown('''
<div class="hero-container">
    <h1 class="hero-title">🎯 QuestAI</h1>
    <p class="hero-subtitle">Master Your Interview Skills with AI-Powered Practice</p>
    <p class="hero-description">
        Experience realistic technical interviews powered by advanced multi-agent AI. 
        Get instant feedback, improve your skills, and land your dream job with confidence.
    </p>
</div>
''', unsafe_allow_html=True)

# Stats Section
st.markdown('''
<div class="stats-container">
    <div class="stat-box">
        <span class="stat-number">3+</span>
        <span class="stat-label">Interview Modes</span>
    </div>
    <div class="stat-box">
        <span class="stat-number">AI</span>
        <span class="stat-label">Multi-Agent System</span>
    </div>
    <div class="stat-box">
        <span class="stat-number">∞</span>
        <span class="stat-label">Practice Sessions</span>
    </div>
    <div class="stat-box">
        <span class="stat-number">24/7</span>
        <span class="stat-label">Always Available</span>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Section Title
st.markdown('''
<h2 style='
    text-align: center; 
    color: white; 
    font-size: 2.8rem; 
    margin: 3rem 0 2.5rem;
    font-weight: 800;
    letter-spacing: -1px;
'>Choose Your Interview Mode</h2>
''', unsafe_allow_html=True)

# Interview Modes - 3 columns
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('''
    <div class="mode-card">
        <span class="mode-icon">🎓</span>
        <h3 class="mode-title">Teach Mode</h3>
        <p class="mode-description">
            Learn while you practice with detailed feedback and personalized guidance
        </p>
        <ul class="mode-features">
            <li>Instant detailed feedback</li>
            <li>Hints and explanations</li>
            <li>Step-by-step guidance</li>
            <li>Perfect for beginners</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Teach Mode", key="teach_btn"):
        logger.info("User clicked Teach Mode")
        st.switch_page("pages/1_Teach_Mode.py")

with col2:
    st.markdown('''
    <div class="mode-card">
        <span class="mode-icon">💼</span>
        <h3 class="mode-title">Experience Mode</h3>
        <p class="mode-description">
            Realistic mock interviews with professional evaluation and detailed reports
        </p>
        <ul class="mode-features">
            <li>Real interview simulation</li>
            <li>Professional assessment</li>
            <li>Comprehensive final report</li>
            <li>Industry-standard questions</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Experience Mode", key="exp_btn"):
        logger.info("User clicked Experience Mode")
        st.switch_page("pages/2_Experience_Mode.py")

with col3:
    st.markdown('''
    <div class="mode-card">
        <span class="mode-icon">📊</span>
        <h3 class="mode-title">Match Score</h3>
        <p class="mode-description">
            Analyze how well your resume matches job requirements
        </p>
        <ul class="mode-features">
            <li>Resume-JD compatibility</li>
            <li>Skills gap analysis</li>
            <li>Improvement suggestions</li>
            <li>Instant AI scoring</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Check Match Score", key="match_btn"):
        logger.info("User clicked Match Score")
        st.switch_page("pages/3_Match_Score.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# How It Works Section
st.markdown('''
<h2 style='
    text-align: center; 
    color: white; 
    font-size: 2.8rem; 
    margin: 4rem 0 3rem;
    font-weight: 800;
    letter-spacing: -1px;
'>How It Works</h2>
''', unsafe_allow_html=True)

st.markdown('''
<div class="steps-container">
    <div class="step">
        <div class="step-number">01</div>
        <div class="step-content">
            <h4 class="step-title">📄 Upload Your Documents</h4>
            <p class="step-description">
                Upload your resume and the job description you're preparing for. Our AI analyzes both 
                to create personalized interview questions tailored to your experience and the role.
            </p>
        </div>
    </div>
    <div class="step">
        <div class="step-number">02</div>
        <div class="step-content">
            <h4 class="step-title">🎯 Choose Your Mode</h4>
            <p class="step-description">
                Select from Teach Mode for learning with feedback, Experience Mode for realistic practice, 
                or Match Score for quick resume-JD compatibility analysis.
            </p>
        </div>
    </div>
    <div class="step">
        <div class="step-number">03</div>
        <div class="step-content">
            <h4 class="step-title">💬 Answer Questions</h4>
            <p class="step-description">
                Respond to AI-generated questions covering coding challenges, technical knowledge, 
                and behavioral scenarios - all relevant to your target role and experience level.
            </p>
        </div>
    </div>
    <div class="step">
        <div class="step-number">04</div>
        <div class="step-content">
            <h4 class="step-title">📊 Get Detailed Feedback</h4>
            <p class="step-description">
                Receive comprehensive evaluations with scores, personalized recommendations, 
                and actionable insights to significantly improve your interview performance.
            </p>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Powered by AI Section
st.markdown('''
<h2 style='
    text-align: center; 
    color: white; 
    font-size: 2.8rem; 
    margin: 4rem 0 2.5rem;
    font-weight: 800;
    letter-spacing: -1px;
'>Powered by Advanced AI Technology</h2>
''', unsafe_allow_html=True)

feat_col1, feat_col2, feat_col3 = st.columns(3, gap="large")

with feat_col1:
    st.markdown('''
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3 class="feature-title">Multi-Agent AI</h3>
        <p class="feature-description">
            Specialized AI agents for coding, resume analysis, behavioral interviews, and intelligent 
            evaluation work together to create a realistic interview experience.
        </p>
    </div>
    ''', unsafe_allow_html=True)

with feat_col2:
    st.markdown('''
    <div class="feature-card">
        <div class="feature-icon">🔄</div>
        <h3 class="feature-title">Automatic Failover</h3>
        <p class="feature-description">
            Seamless switching between multiple AI providers ensures zero downtime and 
            uninterrupted practice sessions, no matter what.
        </p>
    </div>
    ''', unsafe_allow_html=True)

with feat_col3:
    st.markdown('''
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <h3 class="feature-title">Detailed Analytics</h3>
        <p class="feature-description">
            Comprehensive performance reports with strengths, areas for improvement, and 
            personalized recommendations to accelerate your growth.
        </p>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Backend Status Section
st.markdown('''
<h2 style='
    text-align: center; 
    color: white; 
    font-size: 2rem; 
    margin: 4rem 0 2rem;
    font-weight: 700;
'>System Status</h2>
''', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="status-container">', unsafe_allow_html=True)
    
    try:
        with st.spinner("Checking backend status..."):
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.success("✅ **Backend Online**")
                
                with col_b:
                    if data.get("mock_mode", False):
                        st.warning("🎭 **Mock Mode**")
                    else:
                        st.info("🚀 **Live AI Mode**")
                
                with col_c:
                    st.info(f"🔗 **Provider:** {data.get('current_provider', 'N/A').title()}")
                
                # Show mock mode warning if enabled
                if data.get("mock_mode", False):
                    st.warning('''
                    **🎭 Mock Mode Enabled**
                    
                    The backend is running with dummy data - perfect for testing without using API tokens!
                    No real API calls are being made. To use real AI, set `MOCK_MODE=false` in `.env`.
                    ''')
                    logger.info("Backend is in mock mode")
                else:
                    st.success("✅ System is connected to live AI models and ready for interviews!")
                    logger.info("Backend is using real AI")
                    
            else:
                st.error(f"❌ Backend returned status code: {response.status_code}")
                logger.error(f"Backend health check failed: {response.status_code}")
                
    except requests.exceptions.Timeout:
        st.error("⏱️ Backend connection timed out. Please try again.")
        logger.error("Backend connection timeout")
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend at: {BACKEND_URL}")
        st.info("💡 Make sure the backend server is running.")
        logger.error(f"Cannot connect to backend: {BACKEND_URL}")
    except Exception as e:
        st.error(f"❌ Error checking backend: {str(e)}")
        logger.error(f"Backend check error: {str(e)}", exc_info=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Call to Action
st.markdown('''
<div style="text-align: center; padding: 3rem 0 2rem;">
    <h2 style="color: white; font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem;">
        Ready to Ace Your Interview?
    </h2>
    <p style="color: #e0e7ff; font-size: 1.3rem; margin-bottom: 2rem; font-weight: 300;">
        Start practicing now and boost your confidence for the real thing!
    </p>
</div>
''', unsafe_allow_html=True)

# Footer
st.markdown('''
<div style="
    text-align: center; 
    padding: 2rem 0; 
    margin-top: 3rem; 
    border-top: 1px solid rgba(255,255,255,0.15);
">
    <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.8;">
        Built with ❤️ using FastAPI, Microsoft Autogen, and Streamlit<br>
        <a href="https://github.com/sanyaprem/QuestAI" target="_blank" 
           style="color: #e0e7ff; text-decoration: none; font-weight: 600; transition: color 0.3s;">
            ⭐ Star us on GitHub
        </a>
    </p>
</div>
''', unsafe_allow_html=True)

logger.info("Home page rendered successfully")