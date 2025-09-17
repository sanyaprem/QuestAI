import streamlit as st
import requests

BACKEND_URL = "https://questai-backend-ga8s.onrender.com"

st.title("📊 Interview Reports")

session_id = st.text_input("Enter Session ID to view report")

if st.button("Fetch Report"):
    if not session_id:
        st.error("Enter a valid session ID")
    else:
        res = requests.get(f"{BACKEND_URL}/report", params={"session_id": session_id})
        if res.status_code == 200:
            report = res.json()
            st.subheader("Strengths")
            st.write(report["report"].get("strengths", "N/A"))
            st.subheader("Weaknesses")
            st.write(report["report"].get("weaknesses", "N/A"))
            st.subheader("Recommendations")
            st.write(report["report"].get("recommendations", "N/A"))
            
            st.subheader("Detailed Answers")
            for ans in report["answers"]:
                st.markdown(f"**Q:** {ans['question']}")
                st.markdown(f"**A:** {ans['answer']}")
                st.markdown(f"**Eval:** {ans['evaluation']}")
                st.markdown("---")
        else:
            st.error("Failed to fetch report")
