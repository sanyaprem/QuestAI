# frontend/pages/2_Experience_Mode.py
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
    page_title="Experience Mode - QuestAI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling (same as Teach Mode)
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
    
    .upload-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .stFileUploader {
        border: 2px dashed #cbd5e1;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.05);
    }
    
    .stChatMessage {
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
    
    .stTextArea textarea {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        background: #0f172a !important;
        color: #e2e8f0 !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stTextArea label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }
    
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 10px;
        border-left: 4px solid;
        padding: 1rem;
    }
</style>
''', unsafe_allow_html=True)

logger.info("=" * 70)
logger.info("Experience Mode page loaded")
logger.info(f"Using backend: {BACKEND_URL}")
logger.info("=" * 70)

# Page Header
st.markdown('''
<div class="header-card">
    <h1 class="header-title">💼 Experience Mode Interview</h1>
    <p class="header-subtitle">Realistic mock interview with professional evaluation</p>
</div>
''', unsafe_allow_html=True)

def extract_text(file):
    """Extract text from PDF or TXT file"""
    logger.info(f"Extracting text from file: {file.name if file else 'None'}")
    
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


def is_coding_question(question_text: str) -> bool:
    """
    Determine if a question is a coding question.
    Same logic as Teach Mode.
    """
    if not question_text:
        return False
    
    text_lower = question_text.lower()
    
    strong_indicators = [
        "write a function",
        "implement a",
        "write code",
        "write a program",
        "create a function",
        "def ",
        "class ",
        "algorithm to",
        "data structure",
        "complexity analysis",
        "time complexity",
        "space complexity",
        "pseudocode"
    ]
    
    for indicator in strong_indicators:
        if indicator in text_lower:
            logger.info(f"Coding question detected: '{indicator}' found")
            return True
    
    if any(phrase in text_lower for phrase in ["write", "implement", "code"]) and \
       any(word in text_lower for word in ["function", "method", "algorithm", "program"]):
        logger.info("Coding question detected: composite match")
        return True
    
    logger.info("Not a coding question")
    return False


# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    logger.info("Initialized chat_history")

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "code_input_exp" not in st.session_state:
    st.session_state.code_input_exp = ""

# Only show upload section if interview hasn't started
if not st.session_state.session_id:
    # Upload Section
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    
    st.markdown("### 📁 Upload Your Documents")
    st.markdown("Upload your resume and job description to get started with a realistic interview simulation.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        resume_file = st.file_uploader(
            "📄 Your Resume", 
            type=["pdf", "txt"],
            help="Upload your resume in PDF or TXT format"
        )
    
    with col2:
        jd_file = st.file_uploader(
            "📑 Job Description", 
            type=["pdf", "txt"],
            help="Upload the job description you're targeting"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Start Interview Button
    if resume_file and jd_file:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🚀 Start Experience Mode Interview", type="primary", use_container_width=True):
                logger.info("Start button clicked")
                
                resume_text = extract_text(resume_file)
                jd_text = extract_text(jd_file)

                if not resume_text or not jd_text:
                    st.error("⚠️ Please upload both resume and JD.")
                    logger.warning("Missing resume or JD")
                else:
                    logger.info("Starting interview...")
                    
                    with st.spinner("🔄 Starting your interview... Please wait."):
                        try:
                            res = requests.post(f"{BACKEND_URL}/start_interview", json={
                                "resume_text": resume_text,
                                "jd_text": jd_text,
                                "mode": "experience",
                                "user_name": "Candidate"
                            }, timeout=180)
                            
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state.session_id = data["session_id"]
                                st.session_state.current_question = data["first_question"]
                                st.session_state.chat_history = [("assistant", data["first_question"])]
                                
                                logger.info(f"✅ Interview started - Session: {data['session_id']}")
                                st.success("✅ Interview started!")
                                st.rerun()
                            else:
                                logger.error(f"Failed to start: {res.status_code}")
                                st.error(f"❌ Failed: {res.status_code}")
                        
                        except Exception as e:
                            logger.error(f"Error: {str(e)}", exc_info=True)
                            st.error(f"❌ Error: {str(e)}")
    else:
        st.info("👆 Please upload both your resume and the job description to begin")

# Display chat messages
if st.session_state.chat_history:
    st.markdown("### 💬 Interview Conversation")

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(msg)

# --- Answer input ---
if st.session_state.session_id and st.session_state.current_question:
    logger.info("Rendering answer input")
    
    # FIXED: Use improved coding question detection
    is_coding = is_coding_question(st.session_state.current_question)
    
    st.markdown("---")
    
    if is_coding:
        # === CODING QUESTION - CODE EDITOR ===
        st.info("💻 **Coding Question Detected** - Use the code editor below")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            language = st.selectbox(
                "Programming Language",
                ["python", "javascript", "java", "cpp", "go", "rust"],
                index=0,
                key="language_selector_exp"
            )
            
            if st.button("📋 Insert Template", use_container_width=True):
                templates = {
                    "python": "def solution():\n    # Write your solution here\n    pass\n\n# Test your solution\nif __name__ == '__main__':\n    print(solution())",
                    "javascript": "function solution() {\n    // Write your solution here\n    \n}\n\n// Test your solution\nconsole.log(solution());",
                    "java": "public class Solution {\n    public static void main(String[] args) {\n        // Write your solution here\n    }\n}",
                    "cpp": "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your solution here\n    return 0;\n}",
                    "go": "package main\n\nimport \"fmt\"\n\nfunc solution() {\n    // Write your solution here\n}\n\nfunc main() {\n    solution()\n}",
                    "rust": "fn solution() {\n    // Write your solution here\n}\n\nfn main() {\n    solution();\n}"
                }
                st.session_state.code_input_exp = templates.get(language, "")
                st.rerun()
        
        with col1:
            st.markdown("**✍️ Write Your Code:**")
        
        code_answer = st.text_area(
            "Code Editor",
            value=st.session_state.code_input_exp,
            height=400,
            placeholder=f"# Write your {language} code here\n\ndef solution():\n    # Your solution\n    pass",
            key="code_editor_input_exp",
            label_visibility="collapsed",
            help="Write your code here. The editor supports syntax highlighting."
        )
        
        st.session_state.code_input_exp = code_answer
        
        if code_answer and code_answer.strip():
            with st.expander("📋 Preview (how it will be submitted)", expanded=False):
                st.code(code_answer, language=language)
        
        col_a, col_b, col_c = st.columns([2, 1, 1])
        
        with col_a:
            if st.button("✅ Submit Code", type="primary", use_container_width=True, key="submit_code_btn"):
                if not code_answer or not code_answer.strip():
                    st.error("⚠️ Please write your code before submitting")
                    logger.warning("Empty code submission attempted")
                else:
                    formatted_answer = f"```{language}\n{code_answer}\n```"
                    
                    logger.info(f"Code answer submitted: {len(code_answer)} chars, Language: {language}")
                    
                    st.session_state.chat_history.append(("user", formatted_answer))
                    
                    with st.spinner("🔄 Submitting your code..."):
                        try:
                            res = requests.post(f"{BACKEND_URL}/submit_answer", json={
                                "session_id": st.session_state.session_id,
                                "question": st.session_state.current_question,
                                "answer": formatted_answer
                            }, timeout=180).json()
                            
                            evaluation = res["evaluation"]
                            next_q = res.get("next_question")
                            is_done = res.get("done", False)
                            
                            logger.info(f"Evaluation received - Score: {evaluation.get('score', 'N/A')}")
                            
                            # In Experience Mode: Only show confirmation, NOT the evaluation
                            confirmation_text = "✅ **Answer submitted successfully!**"
                            st.session_state.chat_history.append(("assistant", confirmation_text))
                            
                            st.session_state.code_input_exp = ""
                            
                            if is_done:
                                logger.info("Interview completed")
                                st.session_state.chat_history.append(("assistant", "🎉 **Interview Completed!** Click below to view your detailed report."))
                                st.session_state.current_question = None
                            elif next_q:
                                logger.info("Moving to next question")
                                st.session_state.current_question = next_q
                                st.session_state.chat_history.append(("assistant", next_q))
                            else:
                                st.session_state.current_question = None
                            
                            st.rerun()
                        
                        except Exception as e:
                            logger.error(f"Error submitting answer: {str(e)}", exc_info=True)
                            st.error(f"❌ Error: {str(e)}")
        
        with col_b:
            if st.button("🗑️ Clear", use_container_width=True, key="clear_code_btn"):
                st.session_state.code_input_exp = ""
                st.rerun()
        
        with col_c:
            if st.button("⏭️ Skip", use_container_width=True, key="skip_code_btn"):
                logger.info("User skipped question")
                st.session_state.chat_history.append(("user", "[Skipped]"))
                st.session_state.code_input_exp = ""
                try:
                    res = requests.post(f"{BACKEND_URL}/submit_answer", json={
                        "session_id": st.session_state.session_id,
                        "question": st.session_state.current_question,
                        "answer": "[Skipped - No answer provided]"
                    }, timeout=180).json()
                    
                    next_q = res.get("next_question")
                    is_done = res.get("done", False)
                    
                    if is_done:
                        st.session_state.chat_history.append(("assistant", "🎉 **Interview Completed!** Click below to view your detailed report."))
                        st.session_state.current_question = None
                    elif next_q:
                        st.session_state.current_question = next_q
                        st.session_state.chat_history.append(("assistant", next_q))
                    else:
                        st.session_state.current_question = None
                    
                    st.rerun()
                except Exception as e:
                    logger.error(f"Error skipping: {str(e)}")
    
    else:
        # === NON-CODING QUESTION - REGULAR CHAT INPUT ===
        st.info("💬 **Regular Question** - Type your answer below")
        
        # Use chat input for non-coding questions with validation
        if answer := st.chat_input("Your answer here...", key="experience_mode_input"):
            # FIXED: Validate answer before submission
            answer_clean = answer.strip().lower()
            
            if len(answer.strip()) < 10:
                st.warning("⚠️ Please provide a more detailed answer (at least 10 characters)")
                logger.warning(f"Answer too short: {len(answer)} chars")
                st.stop()
            
            acknowledgments = ['ok', 'okay', 'yes', 'no', 'sure', 'fine', 'good', 'alright', 'k', 'yep', 'nope']
            if answer_clean in acknowledgments:
                st.warning("⚠️ Please provide a detailed answer instead of just acknowledging")
                logger.warning(f"Invalid answer: {answer}")
                st.stop()
            
            logger.info(f"Valid answer submitted: {len(answer)} chars")
            
            st.session_state.chat_history.append(("user", answer))

            with st.spinner("Submitting your answer..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/submit_answer", json={
                        "session_id": st.session_state.session_id,
                        "question": st.session_state.current_question,
                        "answer": answer
                    }, timeout=180).json()

                    evaluation = res["evaluation"]
                    next_q = res.get("next_question")
                    is_done = res.get("done", False)
                    
                    logger.info(f"Evaluation received - Score: {evaluation.get('score', 'N/A')}")

                    # In Experience Mode: Only show confirmation, NOT the evaluation
                    confirmation_text = "✅ **Answer submitted successfully!**"
                    st.session_state.chat_history.append(("assistant", confirmation_text))

                    if is_done:
                        logger.info("Interview completed")
                        st.session_state.chat_history.append(("assistant", "🎉 **Interview Completed!** View your report in the Reports page."))
                        st.session_state.current_question = None
                    elif next_q:
                        logger.info("Next question")
                        st.session_state.current_question = next_q
                        st.session_state.chat_history.append(("assistant", next_q))
                    else:
                        st.session_state.current_question = None
                    
                    st.rerun()
                
                except Exception as e:
                    logger.error(f"Error: {str(e)}", exc_info=True)
                    st.error(f"❌ Error: {str(e)}")

logger.info("Experience Mode page rendered")