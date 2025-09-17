import streamlit as st
import requests
from PyPDF2 import PdfReader

st.title("Teach Mode Interview")

BACKEND_URL = "https://questai-backend-ga8s.onrender.com"

# --- Helper to extract text from uploaded file ---
def extract_text(file):
    if file is None:
        return ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    return ""

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "retry_mode" not in st.session_state:
    st.session_state.retry_mode = False  # Track if user wants to retry

# --- File upload ---
resume_file = st.file_uploader("Upload your Resume (PDF/TXT)", type=["pdf", "txt"])
jd_file = st.file_uploader("Upload the Job Description (PDF/TXT)", type=["pdf", "txt"])

# --- Start Interview ---
if st.button("Start Teach Mode Interview"):
    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)

    if not resume_text or not jd_text:
        st.error("Please upload both resume and JD.")
    else:
        res = requests.post(f"{BACKEND_URL}/start_interview", json={
            "resume_text": resume_text,
            "jd_text": jd_text,
            "mode": "teach",
            "user_name": "Candidate"
        })

        if res.status_code == 200:
            data = res.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.current_question = data["question"]
            st.session_state.chat_history = [("assistant", data["question"])]
        else:
            st.error("Failed to start interview.")

# --- Display chat ---
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

# --- Answer input ---
if st.session_state.session_id and st.session_state.current_question:
    answer = st.chat_input("Your answer here...")

    if answer := st.chat_input("Your answer here...", key="teach_mode_input"):
        st.session_state.chat_history.append(("user", answer))
    
        res = requests.post(f"{BACKEND_URL}/submit_answer", json={
            "session_id": st.session_state.session_id,
            "question": st.session_state.current_question,
            "answer": answer
        }).json()
        
        evaluation = res["evaluation"]
        next_q = res["next_question"]
        
        # Show evaluation feedback
        st.session_state.chat_history.append(("assistant", f"Evaluation: {evaluation}"))
        
        # If no answer given, just skip to the next question (don’t stop interview)
        if not answer.strip():
            if next_q:
                st.session_state.current_question = next_q
                st.session_state.chat_history.append(("assistant", f"Okay, let's try the next one:\n\n{next_q}"))
            else:
                st.session_state.chat_history.append(("assistant", "Interview Completed ✅"))
                st.session_state.current_question = None
        else:
            # Normal flow
            if next_q:
                st.session_state.current_question = next_q
                st.session_state.chat_history.append(("assistant", next_q))
            else:
                st.session_state.chat_history.append(("assistant", "Interview Completed ✅"))
                st.session_state.current_question = None

