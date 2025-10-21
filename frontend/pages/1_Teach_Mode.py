# frontend/pages/1_Teach_Mode.py
import streamlit as st
import requests
import sys
from pathlib import Path
from PyPDF2 import PdfReader

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import setup_frontend_logging
from config import BACKEND_URL
import logging

# Setup logging
setup_frontend_logging()
logger = logging.getLogger(__name__)

st.title("🎓 Teach Mode Interview")

logger.info("=" * 70)
logger.info(f"Using backend: {BACKEND_URL}")
logger.info("=" * 70)

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
                logger.info(f"Sending request to: {BACKEND_URL}/start_interview")
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
                    logger.error(f"Response: {res.text}")
                    st.error(f"❌ Failed to start interview: {res.status_code}")
            
            except requests.exceptions.Timeout:
                logger.error("Request timeout")
                st.error("❌ Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                logger.error(f"Cannot connect to backend: {BACKEND_URL}")
                st.error(f"❌ Cannot connect to backend. Please check if it's running.")
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
    
    # Detect if it's a coding question
    question_lower = st.session_state.current_question.lower()
    is_coding_question = any(keyword in question_lower for keyword in [
        "code", "function", "implement", "algorithm", "write a",
        "def ", "class ", "return", "programming", "solve"
    ])
    
    st.markdown("---")
    
    if is_coding_question:
        # === CODING QUESTION - CODE EDITOR ===
        st.info("💻 **Coding Question Detected** - Use the code editor below")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            language = st.selectbox(
                "Language",
                ["python", "javascript", "java", "cpp", "go", "rust"],
                index=0,
                key="language_selector"
            )
        
        with col1:
            st.markdown("**Your Code:**")
        
        # Multi-line code input with proper height
        code_answer = st.text_area(
            "Write your code here",
            value="",
            height=400,
            placeholder=f"# Write your {language} code here\n\ndef solution():\n    # Your solution\n    pass",
            key="code_editor",
            label_visibility="collapsed"
        )
        
        # Show formatted preview
        if code_answer:
            with st.expander("📋 Preview (how it will be submitted)", expanded=False):
                st.code(code_answer, language=language)
        
        col_a, col_b, col_c = st.columns([2, 1, 1])
        
        with col_a:
            if st.button("✅ Submit Code", type="primary", use_container_width=True, key="submit_code_btn"):
                if not code_answer.strip():
                    st.error("⚠️ Please write your code before submitting")
                    logger.warning("Empty code submission attempted")
                else:
                    # Format answer with language
                    formatted_answer = f"```{language}\n{code_answer}\n```"
                    
                    logger.info(f"Code answer submitted: {len(code_answer)} chars, Language: {language}")
                    
                    st.session_state.chat_history.append(("user", formatted_answer))
                    
                    with st.spinner("🔄 Evaluating your code..."):
                        try:
                            logger.info(f"Submitting answer to: {BACKEND_URL}/submit_answer")
                            res = requests.post(f"{BACKEND_URL}/submit_answer", json={
                                "session_id": st.session_state.session_id,
                                "question": st.session_state.current_question,
                                "answer": formatted_answer
                            }, timeout=60).json()
                            
                            evaluation = res["evaluation"]
                            next_q = res.get("next_question")
                            is_done = res.get("done", False)
                            
                            logger.info(f"Evaluation received - Score: {evaluation.get('score', 'N/A')}")
                            
                            # Show evaluation
                            eval_text = f"**📊 Evaluation:**\n\n"
                            eval_text += f"**Score:** {evaluation.get('score', 'N/A')}/10\n\n"
                            eval_text += f"**Feedback:** {evaluation.get('feedback', 'No feedback')}\n\n"
                            
                            if evaluation.get('recommendations'):
                                eval_text += "**💡 Recommendations:**\n"
                                for rec in evaluation['recommendations']:
                                    eval_text += f"- {rec}\n"
                            
                            st.session_state.chat_history.append(("assistant", eval_text))
                            
                            if is_done:
                                logger.info("Interview completed")
                                st.session_state.chat_history.append(("assistant", "🎉 **Interview Completed!**"))
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
                st.rerun()
        
        with col_c:
            if st.button("⏭️ Skip", use_container_width=True, key="skip_code_btn"):
                logger.info("User skipped question")
                st.session_state.chat_history.append(("user", "[Skipped]"))
                # Submit empty answer
                try:
                    res = requests.post(f"{BACKEND_URL}/submit_answer", json={
                        "session_id": st.session_state.session_id,
                        "question": st.session_state.current_question,
                        "answer": "[Skipped - No answer provided]"
                    }, timeout=60).json()
                    
                    next_q = res.get("next_question")
                    if next_q:
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
        
        # Use chat input for non-coding questions
        if answer := st.chat_input("Your answer here...", key="teach_mode_input"):
            logger.info(f"Answer submitted: {len(answer)} chars")
            
            st.session_state.chat_history.append(("user", answer))
            
            with st.spinner("🔄 Evaluating your answer..."):
                try:
                    logger.info(f"Submitting answer to: {BACKEND_URL}/submit_answer")
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
                    eval_text = f"**📊 Evaluation:**\n\n"
                    eval_text += f"**Score:** {evaluation.get('score', 'N/A')}/10\n\n"
                    eval_text += f"**Feedback:** {evaluation.get('feedback', 'No feedback')}\n\n"
                    
                    if evaluation.get('recommendations'):
                        eval_text += "**💡 Recommendations:**\n"
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



# === REPORT SECTION 
if st.session_state.session_id and st.session_state.current_question is None:
    # Interview is complete, show report option
    st.markdown("---")
    st.subheader("📊 Your Interview Report")
    
    if st.button("📄 Generate Final Report", type="primary", use_container_width=True):
        logger.info(f"Generating report for session: {st.session_state.session_id}")
        
        with st.spinner("Generating your comprehensive report..."):
            try:
                logger.info(f"Fetching report from: {BACKEND_URL}/report")
                res = requests.get(
                    f"{BACKEND_URL}/report",
                    params={"session_id": st.session_state.session_id},
                    timeout=60
                )
                
                if res.status_code == 200:
                    report = res.json()
                    logger.info("Report fetched successfully")
                    
                    st.success("✅ Report Generated Successfully!")
                    
                    # Display report
                    report_data = report.get("report", {})
                    
                    # Overall summary
                    st.markdown("### 📈 Interview Summary")
                    
                    if isinstance(report_data, dict):
                        # Strengths
                        if "strengths" in report_data:
                            with st.expander("💪 Strengths", expanded=True):
                                strengths = report_data.get("strengths", "N/A")
                                if isinstance(strengths, list):
                                    for strength in strengths:
                                        st.success(f"✓ {strength}")
                                else:
                                    st.write(strengths)
                        
                        # Weaknesses
                        if "weaknesses" in report_data:
                            with st.expander("⚠️ Areas for Improvement"):
                                weaknesses = report_data.get("weaknesses", "N/A")
                                if isinstance(weaknesses, list):
                                    for weakness in weaknesses:
                                        st.warning(f"• {weakness}")
                                else:
                                    st.write(weaknesses)
                        
                        # Recommendations
                        if "recommendations" in report_data:
                            with st.expander("📋 Recommendations"):
                                recommendations = report_data.get("recommendations", "N/A")
                                if isinstance(recommendations, list):
                                    for rec in recommendations:
                                        st.info(f"→ {rec}")
                                else:
                                    st.write(recommendations)
                    else:
                        # If report is just text
                        st.markdown(str(report_data))
                    
                    # Detailed answers
                    st.markdown("---")
                    st.markdown("### 📝 Detailed Q&A Review")
                    
                    for idx, ans in enumerate(report.get("answers", []), 1):
                        with st.expander(f"Question {idx}: {ans['question'][:80]}..."):
                            st.markdown(f"**Question:**")
                            st.info(ans['question'])
                            
                            st.markdown(f"**Your Answer:**")
                            st.text_area("", ans['answer'], height=150, disabled=True, key=f"answer_{idx}")
                            
                            st.markdown(f"**Evaluation:**")
                            eval_data = ans['evaluation']
                            if isinstance(eval_data, dict):
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    st.metric("Score", f"{eval_data.get('score', 'N/A')}/10")
                                with col2:
                                    st.write(eval_data.get('feedback', 'No feedback'))
                            else:
                                st.write(eval_data)
                    
                    # Download option
                    st.markdown("---")
                    
                    # Create downloadable text report
                    download_report = f"""
QuestAI Interview Report
========================
Session ID: {st.session_state.session_id}
Mode: Teach Mode

{report_data if isinstance(report_data, str) else str(report_data)}

---
Detailed Answers:
"""
                    for idx, ans in enumerate(report.get("answers", []), 1):
                        download_report += f"\n\nQ{idx}: {ans['question']}\n"
                        download_report += f"A{idx}: {ans['answer']}\n"
                        download_report += f"Evaluation: {ans['evaluation']}\n"
                    
                    st.download_button(
                        label="📥 Download Report as Text",
                        data=download_report,
                        file_name=f"interview_report_{st.session_state.session_id[:8]}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    logger.info(f"Report displayed successfully")
                    
                else:
                    logger.error(f"Failed to fetch report: {res.status_code}")
                    st.error(f"❌ Failed to fetch report: {res.status_code}")
                    st.error(f"Response: {res.text}")
            
            except Exception as e:
                logger.error(f"Error fetching report: {str(e)}", exc_info=True)
                st.error(f"❌ Error: {str(e)}")
    
    # Option to start new interview
    st.markdown("---")
    if st.button("🔄 Start New Interview", use_container_width=True):
        logger.info("User clicked Start New Interview")
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        logger.info("Session state cleared")
        st.rerun()

logger.info("Teach Mode page rendered")