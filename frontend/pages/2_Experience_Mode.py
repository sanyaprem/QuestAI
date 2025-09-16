import streamlit as st
import requests
from PyPDF2 import PdfReader

st.title("Teach Mode Interview")

# Upload files
resume_file = st.file_uploader("Upload your Resume (PDF/TXT)", type=["pdf", "txt"])
jd_file = st.file_uploader("Upload the Job Description (PDF/TXT)", type=["pdf", "txt"])

BACKEND_URL = "https://questai-backend-ga8s.onrender.com"

def extract_text(file):
    if file is None:
        return ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    return ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Start Teach Mode Interview"):
    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)

    if not resume_text or not jd_text:
        st.error("Please upload both resume and JD.")
    else:

        res = requests.post(f"{BACKEND_URL}/start_interview", json={
            "resume_text": resume_text,
            "jd_text": jd_text,
            "mode": "experience",
            "user_name": "Candidate"
        })
        data = res.json()
        st.session_state.session_id = data["session_id"]
        st.session_state.current_question = data["question"]
        st.session_state.chat_history = [("assistant", data["question"])]

# Display chat messages
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(msg)

if "session_id" in st.session_state and st.session_state.current_question:
    if answer := st.chat_input("Your answer here..."):
        st.session_state.chat_history.append(("user", answer))

        res = requests.post(f"{BACKEND_URL}/submit_answer", json={
            "session_id": st.session_state.session_id,
            "question": st.session_state.current_question,
            "answer": answer
        }).json()

        evaluation = res["evaluation"]
        next_q = res["next_question"]

        st.session_state.chat_history.append(("assistant", f"Evaluation: {evaluation}"))
        if next_q:
            st.session_state.chat_history.append(("assistant", next_q))
            st.session_state.current_question = next_q
        else:
            st.session_state.chat_history.append(("assistant", "Interview Completed ✅"))
            st.session_state.current_question = None
