import streamlit as st

st.set_page_config(page_title="QuestAI", layout="centered")

st.title("🤖 QuestAI: AI Interview Assistant")
st.markdown("""
Welcome to **QuestAI**!  
Choose a mode to practice your interview:
- **Teach Mode** 🧑‍🏫 → Guided practice with hints & explanations  
- **Experience Mode** 🎯 → Real interview simulation with scores only
""")

col1, col2 = st.columns(2)

with col1:
    if st.button("Teach Mode 🧑‍🏫"):
        st.switch_page("pages/1_Teach_Mode.py")

with col2:
    if st.button("Experience Mode 🎯"):
        st.switch_page("pages/2_Experience_Mode.py")
