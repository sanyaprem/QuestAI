# app/agents/orchestrator.py
"""
Orchestrator: manages sessions and uses specialized agents to generate questions and evaluate answers.
This version ensures resume & behavioral questions are asked sequentially, one by one.
"""

import uuid
from typing import Dict, Any, Optional
from app.agents.coding_agent import CodingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.behavior_agent import BehaviorAgent
from app.agents.evaluator_agent import EvaluatorAgent

# In-memory store for interview sessions
SESSIONS: Dict[str, Dict[str, Any]] = {}

# Initialize agent singletons
coding_agent = CodingAgent()
resume_agent = ResumeAgent()
behavior_agent = BehaviorAgent()


async def create_session(resume_text: str, jd_text: str, mode: str = "experience", user_name: Optional[str] = "Candidate"):
    """
    Create a new interview session.
    Returns session_id and first question (always coding Q1).
    """
    session_id = str(uuid.uuid4())

    # Evaluator depends on mode (teach/experience)
    evaluator = EvaluatorAgent(mode=mode)

    # Generate coding problem (medium)
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

    return {"session_id": session_id, "first_question": coding_q}


async def submit_answer(session_id: str, question: str, answer: str, question_meta: dict = None):
    """
    Evaluate an answer, store progress, and return the next question.
    """
    if session_id not in SESSIONS:
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    prog = sess["progress"]
    evaluator: EvaluatorAgent = sess["agents"]["evaluator"]

    # Evaluate
    eval_result = await evaluator.evaluate(question, answer)

    # Store answer + evaluation
    prog["answers"].append({"question": question, "answer": answer, "evaluation": eval_result})

    # -------------------------
    # Interview Flow
    # -------------------------
    # Round 1: Coding Q1 -> Coding Q2 (easy/hard)
    if prog["round"] == 1 and len(prog["answers"]) == 1:
        score = eval_result.get("score", 5)
        next_q = sess["questions"]["coding"]["q2_hard"] if score >= 7 else sess["questions"]["coding"]["q2_easy"]
        return {"evaluation": eval_result, "next_question": next_q, "done": False}

    # After Coding Q2 -> Resume round
    if prog["round"] == 1 and len(prog["answers"]) >= 2:
        prog["round"] = 2
        prog["resume_index"] = 0
        return {
            "evaluation": eval_result,
            "next_question": sess["questions"]["resume"][prog["resume_index"]],
            "done": False
        }

    # Round 2: Resume questions one by one
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

    # Round 3: Behavioral questions one by one
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

    # Default fallback
    return {"evaluation": eval_result, "next_question": None, "done": False}


async def generate_report(session_id: str):
    """
    Compile a final evaluation report with strengths, weaknesses, and recommendations.
    """
    if session_id not in SESSIONS:
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    answers = sess["progress"]["answers"]

    # Build summary prompt
    summary_prompt = (
        "Given the following Q&A pairs with evaluations, summarize strengths, weaknesses, and study recommendations. "
        "Return JSON with keys 'strengths', 'weaknesses', 'recommendations'.\n\n"
    )
    for a in answers:
        summary_prompt += f"Q: {a['question']}\nA: {a['answer']}\nEval: {a['evaluation']}\n\n"

    evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
    raw = await evaluator.ask(summary_prompt)

    # Try parsing JSON from model output
    try:
        import re, json
        m = re.search(r"\{.*\}", raw, re.S)
        parsed = json.loads(m.group(0)) if m else {"raw": raw}
    except Exception:
        parsed = {"raw": raw}

    return {"report": parsed, "answers": answers}
