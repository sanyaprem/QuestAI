import streamlit as st

st.set_page_config(page_title="QuestAI - Interview Assistant", page_icon="🤖", layout="wide")

st.title("🤖 QuestAI")
st.subheader("Your AI-powered Interview Partner")

st.markdown("""
Welcome to **QuestAI**!  
This platform simulates interviews with **multi-agent AI**.

You can try two modes:

- 🎓 **Teach Mode** – Guided practice with retries and coaching after feedback.  
- 🧑‍💼 **Experience Mode** – Realistic mock interview simulation.  
- 📊 **Reports** – View a structured report of your performance.  

👉 Use the left sidebar to navigate between modes.
""")
