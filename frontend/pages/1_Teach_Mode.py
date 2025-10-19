# frontend/pages/1_Teach_Mode.py
import streamlit as st
import requests
import sys
from pathlib import Path
from PyPDF2 import PdfReader

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_frontend_logging
import logging

# Setup logging
setup_frontend_logging()
logger = logging.getLogger(__name__)

st.title("🎓 Teach Mode Interview")

BACKEND_URL = "http://127.0.0.1:8000"

logger.info("=" * 70)
logger.info("Teach Mode page loaded")
logger.info("=" * 70)


logger.info(f"Using backend: {BACKEND_URL}")

# --- Helper to extract text from uploaded file ---
def extract_text(file):
    """Extract text from PDF or TXT file"""
    logger.info(f"Extracting text from file: {file.name if file else 'None'}")
    
    if file is None:
        logger.warning("No file provided")
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

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    logger.info("Initialized chat_history")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
    logger.info("Initialized session_id")

if "current_question" not in st.session_state:
    st.session_state.current_question = None
    logger.info("Initialized current_question")

if "retry_mode" not in st.session_state:
    st.session_state.retry_mode = False
    logger.info("Initialized retry_mode")

# --- File upload ---
logger.info("Rendering file upload section")
resume_file = st.file_uploader("📄 Upload your Resume (PDF/TXT)", type=["pdf", "txt"])
jd_file = st.file_uploader("📑 Upload the Job Description (PDF/TXT)", type=["pdf", "txt"])

# --- Start Interview ---
if st.button("🚀 Start Teach Mode Interview"):
    logger.info("Start button clicked")
    
    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)

    if not resume_text or not jd_text:
        st.error("⚠️ Please upload both resume and JD.")
        logger.warning("Missing resume or JD")
    else:
        logger.info("Starting interview...")
        logger.debug(f"Resume: {len(resume_text)} chars, JD: {len(jd_text)} chars")
        
        with st.spinner("Starting interview... Please wait."):
            try:
                res = requests.post(f"{BACKEND_URL}/start_interview", json={
                    "resume_text": resume_text,
                    "jd_text": jd_text,
                    "mode": "teach",
                    "user_name": "Candidate"
                }, timeout=60)

                if res.status_code == 200:
                    data = res.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.current_question = data["first_question"]
                    st.session_state.chat_history = [("assistant", data["first_question"])]
                    
                    logger.info(f"✅ Interview started - Session: {data['session_id']}")
                    st.success("✅ Interview started!")
                    st.rerun()
                else:
                    logger.error(f"Failed to start interview: {res.status_code}")
                    st.error(f"❌ Failed to start interview: {res.status_code}")
            
            except Exception as e:
                logger.error(f"Error starting interview: {str(e)}", exc_info=True)
                st.error(f"❌ Error: {str(e)}")

# --- Display chat ---
logger.debug(f"Displaying {len(st.session_state.chat_history)} messages")
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

# --- Answer input ---
if st.session_state.session_id and st.session_state.current_question:
    logger.info("Rendering answer input")
    
    if answer := st.chat_input("Your answer here...", key="teach_mode_input"):
        logger.info(f"Answer submitted: {len(answer)} chars")
        
        st.session_state.chat_history.append(("user", answer))
        
        with st.spinner("Evaluating your answer..."):
            try:
                res = requests.post(f"{BACKEND_URL}/submit_answer", json={
                    "session_id": st.session_state.session_id,
                    "question": st.session_state.current_question,
                    "answer": answer
                }, timeout=60).json()
                
                evaluation = res["evaluation"]
                next_q = res.get("next_question")
                is_done = res.get("done", False)
                
                logger.info(f"Evaluation received - Score: {evaluation.get('score', 'N/A')}")
                
                # Show evaluation feedback
                eval_text = f"**Evaluation:**\n\n"
                eval_text += f"**Score:** {evaluation.get('score', 'N/A')}/10\n\n"
                eval_text += f"**Feedback:** {evaluation.get('feedback', 'No feedback')}\n\n"
                
                if evaluation.get('recommendations'):
                    eval_text += "**Recommendations:**\n"
                    for rec in evaluation['recommendations']:
                        eval_text += f"- {rec}\n"
                
                st.session_state.chat_history.append(("assistant", eval_text))
                
                # Check if interview is complete
                if is_done:
                    logger.info("Interview completed")
                    st.session_state.chat_history.append(("assistant", "🎉 **Interview Completed!** You can now view your report."))
                    st.session_state.current_question = None
                elif next_q:
                    logger.info("Moving to next question")
                    st.session_state.current_question = next_q
                    st.session_state.chat_history.append(("assistant", next_q))
                else:
                    logger.warning("No next question but not done")
                    st.session_state.current_question = None
                
                st.rerun()
            
            except Exception as e:
                logger.error(f"Error submitting answer: {str(e)}", exc_info=True)
                st.error(f"❌ Error: {str(e)}")

logger.info("Teach Mode page rendered")