import streamlit as st
from PyPDF2 import PdfReader

def extract_text(file):
    if file is None:
        return ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    return ""

def display_chat(chat_history):
    for role, msg in chat_history:
        with st.chat_message(role):
            st.write(msg)
