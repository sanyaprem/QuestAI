import streamlit as st
import requests
from PyPDF2 import PdfReader
import os

st.set_page_config(page_title="Resume–Job Match Analyzer", page_icon="📊", layout="wide")

st.title("📊 Resume–Job Match Analyzer")
st.markdown("Upload your resume and the job description to check how well you match the role.")

BACKEND_URL ="https://questai-backend-ga8s.onrender.com"

# -------------------------
# Helper to extract text
# -------------------------
def extract_text(file):
    if file is None:
        return ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    return ""

# -------------------------
# File Upload Section
# -------------------------
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader("📄 Upload Resume", type=["pdf", "txt"])

with col2:
    jd_file = st.file_uploader("📑 Upload Job Description", type=["pdf", "txt"])

st.markdown("---")

# -------------------------
# Match Score Button
# -------------------------
if st.button("🔍 Check Match Score", use_container_width=True):
    resume_text = extract_text(resume_file)
    jd_text = extract_text(jd_file)

    if not resume_text or not jd_text:
        st.error("⚠️ Please upload both a resume and job description.")
    else:
        with st.spinner("Analyzing match score... ⏳"):
            res = requests.post(f"{BACKEND_URL}/match_score", json={
                "resume_text": resume_text,
                "jd_text": jd_text
            })

        if res.status_code == 200:
            result = res.json()

            # Display Match Score
            st.subheader("✅ Results")
            st.metric("Match Score", f"{result.get('match_percent', 0)} %")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 💪 Strengths")
                for s in result.get("strengths", []):
                    st.success(f"- {s}")

            with col2:
                st.markdown("### ⚠️ Gaps / Improvements")
                for g in result.get("gaps", []):
                    st.warning(f"- {g}")

        else:
            st.error(f"❌ Error from backend: {res.text}")
