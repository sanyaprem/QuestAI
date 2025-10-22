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

# Page config
st.set_page_config(
    page_title="Match Score - QuestAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Fixed text colors
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
    
    .upload-section {
        background: #1e293b;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .result-card {
        background: #1e293b;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .score-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2rem auto;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .score-text {
        color: white;
        font-size: 3rem;
        font-weight: 800;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 1.5rem 0 1rem;
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
    
    .strength-item {
        background: rgba(34, 197, 94, 0.1);
        border-left: 4px solid #22c55e;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        color: #86efac !important;
    }
    
    .strength-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
        background: rgba(34, 197, 94, 0.15);
    }
    
    .gap-item {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        color: #fca5a5 !important;
    }
    
    .gap-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        background: rgba(239, 68, 68, 0.15);
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
    
    .info-box {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #cbd5e1;
    }
    
    /* Global dark mode fixes */
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
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        color: #fca5a5 !important;
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
</style>
''', unsafe_allow_html=True)

logger.info("=" * 70)
logger.info("Match Score page loaded")
logger.info(f"Using backend: {BACKEND_URL}")
logger.info("=" * 70)

# Page Header
st.markdown('''
<div class="header-card">
    <h1 class="header-title">📊 Resume-Job Match Analyzer</h1>
    <p class="header-subtitle">Discover how well your resume aligns with your dream job</p>
</div>
''', unsafe_allow_html=True)

# Helper to extract text
def extract_text(file):
    """Extract text from PDF or TXT file"""
    if file is None:
        return ""
    
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages])
            logger.info(f"Extracted {len(text)} chars from PDF")
            return text
        elif file.type == "text/plain":
            text = file.read().decode("utf-8")
            logger.info(f"Extracted {len(text)} chars from TXT")
            return text
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        st.error(f"Error reading file: {str(e)}")
    
    return ""

# Upload Section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)

st.markdown("### 📁 Upload Your Documents")
st.markdown("Upload both documents to analyze the compatibility between your profile and the job requirements.")

col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader(
        "📄 Your Resume", 
        type=["pdf", "txt"],
        help="Upload your resume in PDF or TXT format"
    )
    if resume_file:
        st.success(f"✓ {resume_file.name}")

with col2:
    jd_file = st.file_uploader(
        "📑 Job Description", 
        type=["pdf", "txt"],
        help="Upload the target job description"
    )
    if jd_file:
        st.success(f"✓ {jd_file.name}")

st.markdown('</div>', unsafe_allow_html=True)

# Information box
if not (resume_file and jd_file):
    st.markdown('''
    <div class="info-box">
        <h4 style="margin-top: 0; color: #667eea;">💡 How It Works</h4>
        <p style="margin-bottom: 0;">
            Our AI analyzes your resume against the job description to provide:
            <br>• Match percentage score
            <br>• Your key strengths for this role
            <br>• Skills gaps and areas for improvement
            <br>• Actionable recommendations
        </p>
    </div>
    ''', unsafe_allow_html=True)

# Analyze Button
if resume_file and jd_file:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    
    with col_b:
        if st.button("🔍 Analyze Match Score", type="primary", use_container_width=True):
            logger.info("Analyze Match Score button clicked")
            
            resume_text = extract_text(resume_file)
            jd_text = extract_text(jd_file)

            if not resume_text or not jd_text:
                st.error("⚠️ Could not extract text from files. Please check the format.")
                logger.warning("Failed to extract text")
            else:
                logger.info("Calculating match score...")
                
                with st.spinner("🔄 Analyzing your match score... This may take a moment."):
                    try:
                        res = requests.post(f"{BACKEND_URL}/match_score", json={
                            "resume_text": resume_text,
                            "jd_text": jd_text
                        }, timeout=60)

                        if res.status_code == 200:
                            result = res.json()
                            match_score = result.get('match_percent', 0)
                            logger.info(f"Match score received: {match_score}%")

                            # Display Results
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Score Display
                            st.markdown('<div class="result-card">', unsafe_allow_html=True)
                            
                            st.markdown("### 🎯 Your Match Score")
                            
                            # Create visual score circle
                            st.markdown(f'''
                            <div class="score-circle">
                                <div class="score-text">{match_score}%</div>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Interpretation
                            if match_score >= 80:
                                st.success("🌟 **Excellent Match!** You're a strong candidate for this role.")
                            elif match_score >= 60:
                                st.info("👍 **Good Match!** You meet most of the requirements.")
                            elif match_score >= 40:
                                st.warning("⚡ **Fair Match** - Some skill gaps to address.")
                            else:
                                st.error("💪 **Skills Gap** - Consider upskilling for this role.")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Detailed Results
                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                st.markdown('<h3 class="section-title">💪 Your Strengths</h3>', unsafe_allow_html=True)
                                
                                strengths = result.get("strengths", [])
                                if strengths:
                                    for strength in strengths:
                                        st.markdown(f'<div class="strength-item">✓ {strength}</div>', unsafe_allow_html=True)
                                else:
                                    st.info("No specific strengths identified.")
                                
                                st.markdown('</div>', unsafe_allow_html=True)

                            with col2:
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                st.markdown('<h3 class="section-title">⚠️ Areas for Improvement</h3>', unsafe_allow_html=True)
                                
                                gaps = result.get("gaps", [])
                                if gaps:
                                    for gap in gaps:
                                        st.markdown(f'<div class="gap-item">• {gap}</div>', unsafe_allow_html=True)
                                else:
                                    st.success("No significant gaps identified!")
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Recommendations
                            if result.get("recommendations"):
                                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                                st.markdown('<h3 class="section-title">💡 Recommendations</h3>', unsafe_allow_html=True)
                                
                                for rec in result["recommendations"]:
                                    st.markdown(f"**→** {rec}")
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Next Steps
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown('''
                            <div class="info-box">
                                <h4 style="margin-top: 0; color: #667eea;">🚀 Next Steps</h4>
                                <p style="margin-bottom: 0;">
                                    Ready to practice? Try our interview modes:
                                    <br>• <strong>Teach Mode</strong> - Learn with detailed feedback
                                    <br>• <strong>Experience Mode</strong> - Realistic mock interviews
                                </p>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Action buttons
                            col_x, col_y = st.columns(2)
                            
                            with col_x:
                                if st.button("🎓 Start Teach Mode", use_container_width=True):
                                    st.switch_page("pages/1_Teach_Mode.py")
                            
                            with col_y:
                                if st.button("💼 Start Experience Mode", use_container_width=True):
                                    st.switch_page("pages/2_Experience_Mode.py")
                            
                        else:
                            logger.error(f"Backend error: {res.status_code}")
                            st.error(f"❌ Error from backend: {res.text}")
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timed out. Please try again.")
                        logger.error("Request timeout")
                    except requests.exceptions.ConnectionError:
                        st.error(f"❌ Cannot connect to backend at: {BACKEND_URL}")
                        logger.error("Connection error")
                    except Exception as e:
                        logger.error(f"Error: {str(e)}", exc_info=True)
                        st.error(f"❌ Error: {str(e)}")

logger.info("Match Score page rendered")