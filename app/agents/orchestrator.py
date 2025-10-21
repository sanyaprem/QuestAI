# app/agents/orchestrator.py
"""
Orchestrator: manages sessions and uses specialized agents to generate questions and evaluate answers.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from app.agents.coding_agent import CodingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.behavior_agent import BehaviorAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.config import Config

# Import mock data
from app.agents.mock_data import (
    MOCK_CODING_PROBLEMS,
    MOCK_RESUME_QUESTIONS,
    MOCK_BEHAVIORAL_QUESTIONS,
    mock_evaluate,
    mock_generate_report
)

logger = logging.getLogger(__name__)

# In-memory store for interview sessions
SESSIONS: Dict[str, Dict[str, Any]] = {}

# Initialize agent singletons (only if not in mock mode)
if not Config.MOCK_MODE:
    logger.info("Initializing real agent singletons...")
    coding_agent = CodingAgent()
    resume_agent = ResumeAgent()
    behavior_agent = BehaviorAgent()
    logger.info("✅ Agent singletons created")
else:
    logger.warning("🎭 Mock mode - Skipping real agent creation")
    coding_agent = None
    resume_agent = None
    behavior_agent = None


async def create_session(resume_text: str, jd_text: str, mode: str = "experience", user_name: Optional[str] = "Candidate"):
    """
    Create a new interview session.
    Returns session_id and first question (always coding Q1).
    """
    logger.info("=" * 70)
    logger.info("🚀 CREATE SESSION")
    logger.info("=" * 70)
    logger.info(f"Mode: {mode} | Mock: {Config.MOCK_MODE}")
    logger.info(f"User: {user_name}")
    
    session_id = str(uuid.uuid4())
    logger.info(f"Generated session ID: {session_id}")

    # Evaluator depends on mode (teach/experience)
    evaluator = EvaluatorAgent(mode=mode) if not Config.MOCK_MODE else None

    if Config.MOCK_MODE:
        logger.warning("🎭 Using MOCK DATA")
        import random
        
        # Use mock data
        coding_q = random.choice(MOCK_CODING_PROBLEMS)
        followups = "1. What's the brute force approach?\n2. Can you optimize it?"
        resume_qs = MOCK_RESUME_QUESTIONS
        behavior_qs = MOCK_BEHAVIORAL_QUESTIONS
        
    else:
        logger.info("Generating real questions from AI...")
        # Generate coding problem
        coding_q = await coding_agent.generate_problem(resume_text=resume_text, jd_text=jd_text, difficulty="medium")
        followups = await coding_agent.generate_followups(coding_q)
        
        # Generate resume and behavioral questions
        resume_qs = await resume_agent.generate_questions(resume_text=resume_text, jd_text=jd_text)
        behavior_qs = await behavior_agent.generate_questions(count=5)

    # Store session
    SESSIONS[session_id] = {
        "mode": mode,
        "user_name": user_name,
        "resume": resume_text,
        "jd": jd_text,
        "agents": {"evaluator": evaluator},
        "questions": {
            "coding": {
                "q1": coding_q,
                "followups": followups,
                "q2_easy": "Explain a simple hashing problem (easy).",
                "q2_hard": "Design a concurrency control problem (hard)."
            },
            "resume": resume_qs,
            "behavior": behavior_qs
        },
        "progress": {
            "round": 1,
            "answers": [],
            "resume_index": 0,
            "behavior_index": 0
        },
    }
    
    logger.info(f"✅ Session {session_id} created")
    logger.info("=" * 70)

    return {"session_id": session_id, "first_question": coding_q}


async def submit_answer(session_id: str, question: str, answer: str, question_meta: dict = None):
    """
    Evaluate an answer, store progress, and return the next question.
    """
    logger.info("=" * 70)
    logger.info("📝 SUBMIT ANSWER")
    logger.info(f"Session: {session_id} | Mock: {Config.MOCK_MODE}")
    
    if session_id not in SESSIONS:
        logger.error(f"❌ Invalid session ID: {session_id}")
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    prog = sess["progress"]
    
    # Evaluate
    if Config.MOCK_MODE:
        logger.warning("🎭 Using MOCK evaluation")
        eval_result = mock_evaluate(question, answer)
    else:
        evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
        eval_result = await evaluator.evaluate(question, answer)
    
    logger.info(f"✅ Evaluation complete - Score: {eval_result.get('score', 0)}/10")

    # Store answer + evaluation
    prog["answers"].append({
        "question": question,
        "answer": answer,
        "evaluation": eval_result
    })

    # Interview Flow (same as before)
    if prog["round"] == 1 and len(prog["answers"]) == 1:
        score = eval_result.get("score", 5)
        next_q = sess["questions"]["coding"]["q2_hard"] if score >= 7 else sess["questions"]["coding"]["q2_easy"]
        return {"evaluation": eval_result, "next_question": next_q, "done": False}

    if prog["round"] == 1 and len(prog["answers"]) >= 2:
        prog["round"] = 2
        prog["resume_index"] = 0
        return {
            "evaluation": eval_result,
            "next_question": sess["questions"]["resume"][prog["resume_index"]],
            "done": False
        }

    if prog["round"] == 2:
        prog["resume_index"] += 1
        if prog["resume_index"] < len(sess["questions"]["resume"]):
            return {
                "evaluation": eval_result,
                "next_question": sess["questions"]["resume"][prog["resume_index"]],
                "done": False
            }
        else:
            prog["round"] = 3
            prog["behavior_index"] = 0
            return {
                "evaluation": eval_result,
                "next_question": sess["questions"]["behavior"][prog["behavior_index"]],
                "done": False
            }

    if prog["round"] == 3:
        prog["behavior_index"] += 1
        if prog["behavior_index"] < len(sess["questions"]["behavior"]):
            return {
                "evaluation": eval_result,
                "next_question": sess["questions"]["behavior"][prog["behavior_index"]],
                "done": False
            }
        else:
            prog["round"] = 4
            return {"evaluation": eval_result, "next_question": None, "done": True}

    return {"evaluation": eval_result, "next_question": None, "done": False}


async def generate_report(session_id: str):
    """
    Compile a final evaluation report.
    """
    logger.info("=" * 70)
    logger.info("📊 GENERATE REPORT")
    logger.info(f"Session: {session_id} | Mock: {Config.MOCK_MODE}")
    
    if session_id not in SESSIONS:
        logger.error(f"❌ Invalid session ID")
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    answers = sess["progress"]["answers"]
    
    if Config.MOCK_MODE:
        logger.warning("🎭 Using MOCK report")
        parsed = mock_generate_report(answers)
    else:
        # Build summary prompt
        summary_prompt = (
            "Given the following Q&A pairs with evaluations, summarize strengths, weaknesses, and recommendations. "
            "Return JSON with keys 'strengths', 'weaknesses', 'recommendations'.\n\n"
        )
        for a in answers:
            summary_prompt += f"Q: {a['question']}\nA: {a['answer']}\nEval: {a['evaluation']}\n\n"

        evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
        raw = await evaluator.ask(summary_prompt)

        # Try parsing JSON
        try:
            import re, json
            m = re.search(r"\{.*\}", raw, re.S)
            parsed = json.loads(m.group(0)) if m else {"raw": raw}
        except Exception:
            parsed = {"raw": raw}
    
    logger.info("✅ Report generated")
    logger.info("=" * 70)

    return {"report": parsed, "answers": answers}


logger.info("✅ Orchestrator module loaded")