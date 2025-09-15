# QuestAI

QuestAI is a **multi-agent AI interviewer** built with **FastAPI**, **Autogen**, and **Streamlit**.  
It simulates real-world technical interviews in two modes:  
- **Teach Mode** – guided interview with hints and improvements.  
- **Experience Mode** – realistic mock interview with scoring.  

---

## Features

- **Multi-agent architecture**:
  - **CodingAgent** – generates coding problems and follow-up prompts.  
  - **ResumeAgent** – asks questions based on candidate’s resume.  
  - **BehaviorAgent** – asks behavioral interview questions.  
  - **EvaluatorAgent** – scores responses and generates final report.  

- **Round-based interview flow**:
  1. **Round 1 – Coding Questions** (adaptive difficulty: medium → easy/hard).  
  2. **Round 2 – Resume-based Questions** (skills + job description relevance).  
  3. **Round 3 – Behavioral Questions**.  
  4. **Final Report** with strengths, weaknesses, and recommended improvements.  

- **Frontend in Streamlit**:
  - Home page with intro + mode selection.  
  - Teach Mode & Experience Mode pages.  
  - Live interview flow with questions, input box, and evaluation feedback.  

- **Backend in FastAPI**:
  - `/start_interview` → starts a session and returns the first question.  
  - `/submit_answer` → submits an answer, gets evaluation + next question.  
  - `/report` → generates and returns the final interview report.  

---

## Setup

1. Clone repo:
   ```bash
   git clone https://github.com/sanyaprem/QuestAI.git
   cd QuestAI
2. Create and activate environment:
   ```bash
   conda create -n ai-agent python=3.10
   conda activate ai-agent
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
4. Run backend:
   ```bash
   uvicorn app.main:app --reload
5. Run frontend:
   ```bash
   cd frontend
   streamlit run Home.py

