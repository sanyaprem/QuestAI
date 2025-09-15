import streamlit as st
import requests

st.title("🎯 Experience Mode")

backend_url = "http://127.0.0.1:8000"

if "session_id" not in st.session_state:
    st.session_state.session_id = None
    st.session_state.current_question = None
    st.session_state.report = None

resume_text = st.text_area("Paste your Resume text here")
jd_text = st.text_area("Paste Job Description here")

if st.button("Start Interview"):
    res = requests.post(f"{backend_url}/start_interview", json={
        "resume_text": resume_text,
        "jd_text": jd_text,
        "mode": "experience",
        "user_name": "Candidate"
    })
    data = res.json()
    st.session_state.session_id = data["session_id"]
    st.session_state.current_question = data["question"]

if st.session_state.current_question:
    st.subheader("Question:")
    st.write(st.session_state.current_question)

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer"):
        res = requests.post(f"{backend_url}/submit_answer", json={
            "session_id": st.session_state.session_id,
            "question": st.session_state.current_question,
            "answer": answer,
            "question_meta": {}
        })
        data = res.json()
        st.write("### Feedback:")
        st.write(data.get("evaluation", "No feedback"))
        st.session_state.current_question = data.get("next_question")

        if data.get("finished"):
            rep = requests.get(f"{backend_url}/report", params={"session_id": st.session_state.session_id})
            st.session_state.report = rep.json()
            st.write("## Final Report")
            st.json(st.session_state.report)
