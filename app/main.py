from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
from app.agents.orchestrator import create_session, submit_answer, generate_report

load_dotenv()

# model_client = OpenAIChatCompletionClient(
#     model="gemini-1.5-flash-8b",
#     api_key= os.getenv("api_key")

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

# -----------------------------
# Endpoints
# -----------------------------

@app.get("/")
def root():
    return {"message": "QuestAI backend is running."}

@app.post("/start_interview")
async def api_start_interview(req: StartRequest):
    """
    Start a new interview session.
    Mode: teach or experience
    Returns: session_id and first question
    """
    result = await create_session(
        req.resume_text,
        req.jd_text,
        mode=req.mode,
        user_name=req.user_name
    )
    return result

@app.post("/submit_answer")
async def api_submit_answer(payload: SubmitAnswerReq):
    """
    Submit an answer for the current round.
    Returns evaluation + next question or end of interview.
    """
    res = await submit_answer(
        payload.session_id,
        payload.question,
        payload.answer,
        payload.question_meta
    )
    return res

@app.get("/report")
async def api_report(session_id: str):
    """
    Generate final interview report for a given session.
    """
    rep = await generate_report(session_id)
    return rep