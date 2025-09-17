from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
# from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from app.agents.orchestrator import create_session, submit_answer, generate_report
from app.agents.evaluator_agent import EvaluatorAgent

load_dotenv()

# model_client = OpenAIChatCompletionClient(
#     model="gemini-1.5-flash-8b",
#     api_key=os.getenv("gemini_api_key")

# )
# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # or restrict to your frontend Render URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app = FastAPI(
    title="QuestAI Interview Agent",
    description="Multi-agent interview simulation with Teach & Experience modes",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# agent = AssistantAgent(
#     name="QuestAI",
#     system_message="You are QuestAI, an interview assistant helping users practice technical interviews.",
#     model_client=model_client

# -----------------------------
# Request Models
# -----------------------------
class StartRequest(BaseModel):
    resume_text: str
    jd_text: str
    mode: str  # 'teach' or 'experience'
    user_name: Optional[str] = "Candidate"

class SubmitAnswerReq(BaseModel):
    session_id: str
    question: str
    answer: str
    question_meta: dict = {}

class MatchRequest(BaseModel):
    resume_text: str
    jd_text: str

# -----------------------------
# Endpoints
# -----------------------------
@app.get("/")
def root():
    return {"message": "QuestAI backend is running."}

@app.post("/start_interview")
async def api_start_interview(req: StartRequest):
    """Start a new interview session."""
    result = await create_session(
        req.resume_text,
        req.jd_text,
        mode=req.mode,
        user_name=req.user_name
    )
    return result

@app.post("/submit_answer")
async def api_submit_answer(payload: SubmitAnswerReq):
    """Submit an answer and get evaluation + next question."""
    res = await submit_answer(
        payload.session_id,
        payload.question,
        payload.answer,
        payload.question_meta
    )
    return res

@app.get("/report")
async def api_report(session_id: str):
    """Generate final interview report for a given session."""
    rep = await generate_report(session_id)
    return rep

@app.post("/match_score")
async def match_score(req: MatchRequest):
    """Check resume–job match percentage + strengths + gaps."""
    evaluator = EvaluatorAgent(mode="analysis")

    prompt = f"""
    Compare the following resume and job description.

    Resume:
    {req.resume_text}

    Job Description:
    {req.jd_text}

    Task:
    1. Give a match percentage (0-100%) that represents how well the resume fits the job.
    2. List 3 key strengths that make the candidate a good fit.
    3. List 3 gaps/weaknesses the candidate should improve.

    Return ONLY valid JSON in this format:
    {{
        "match_percent": <number>,
        "strengths": ["point1", "point2", "point3"],
        "gaps": ["point1", "point2", "point3"]
    }}
    """

    raw = await evaluator.ask(prompt)

    import re, json
    try:
        m = re.search(r"\{.*\}", raw, re.S)
        parsed = json.loads(m.group(0)) if m else {"raw": raw}
    except Exception:
        parsed = {"match_percent": 0, "strengths": [], "gaps": [], "raw": raw}


    return parsed
