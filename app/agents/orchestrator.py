# app/agents/orchestrator.py
"""
Orchestrator: manages sessions and uses specialized agents to generate questions and evaluate answers.
This version uses direct agent calls (deterministic orchestration).
We include an optional commented example showing how to run agents inside a RoundRobinGroupChat team (docs linked).
"""

import uuid
from typing import Dict, Any, Optional
from app.agents.coding_agent import CodingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.behavior_agent import BehaviorAgent
from app.agents.evaluator_agent import EvaluatorAgent

# Simple in-memory sessions for prototype:
SESSIONS: Dict[str, Dict[str, Any]] = {}

# Initialize agent instances (singletons)
coding_agent = CodingAgent()
resume_agent = ResumeAgent()
behavior_agent = BehaviorAgent()
# evaluator will be re-created per session with mode set
# (so teach/experience mode differences are easy)
# Note: each evaluator uses the BaseAgent wrapper and talks to the LLM


async def create_session(resume_text: str, jd_text: str, mode: str = "experience", user_name: Optional[str] = "Candidate"):
    """
    Create session, ask CodingAgent for an initial medium problem, prepare resume+behavior questions.
    Returns session_id and first_question (string).
    """
    session_id = str(uuid.uuid4())

    # create evaluator configured for this mode
    evaluator = EvaluatorAgent(mode=mode)

    # Generate coding problem (medium)
    coding_q = await coding_agent.generate_problem(resume_text=resume_text, jd_text=jd_text, difficulty="medium")
    # Generate follow-ups for problem (approaches)
    followups = await coding_agent.generate_followups(coding_q)

    # Generate resume and behavior questions
    resume_qs = await resume_agent.generate_questions(resume_text=resume_text, jd_text=jd_text, count=3)
    behavior_qs = await behavior_agent.generate_questions(count=5)

    SESSIONS[session_id] = {
        "mode": mode,
        "user_name": user_name,
        "resume": resume_text,
        "jd": jd_text,
        "agents": {
            "evaluator": evaluator
        },
        "questions": {
            "coding": {"q1": coding_q, "followups": followups, "q2_easy": "Explain a simple hashing problem (easy).", "q2_hard": "Design a concurrency control problem (hard)."},
            "resume": resume_qs,
            "behavior": behavior_qs
        },
        "progress": {"round": 1, "answers": []},
    }
    return {"session_id": session_id, "question": coding_q}


async def submit_answer(session_id: str, question: str, answer: str, question_meta: dict = None):
    """
    Evaluate the answer (using EvaluatorAgent configured for session), store it, and compute next question.
    Returns evaluation dict and next_question (or done=True).
    """
    if session_id not in SESSIONS:
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
    # evaluate
    eval_result = await evaluator.evaluate(question, answer)
    # store
    sess["progress"]["answers"].append({"question": question, "answer": answer, "evaluation": eval_result})

    prog = sess["progress"]

    # Basic flow:
    # Round 1: coding Q1 -> coding Q2 (easy/hard based on score) -> move to resume
    # Round 2: resume questions -> move to behavior
    # Round 3: behavior questions -> finish

    if prog["round"] == 1 and len(prog["answers"]) == 1:
        score = eval_result.get("score") or 5
        next_q = sess["questions"]["coding"]["q2_hard"] if score >= 7 else sess["questions"]["coding"]["q2_easy"]
        return {"evaluation": eval_result, "next_question": next_q, "done": False}

    if prog["round"] == 1 and len(prog["answers"]) >= 2:
        prog["round"] = 2
        return {"evaluation": eval_result, "next_question": sess["questions"]["resume"], "done": False}

    if prog["round"] == 2:
        prog["round"] = 3
        return {"evaluation": eval_result, "next_question": sess["questions"]["behavior"], "done": False}

    if prog["round"] == 3:
        prog["round"] = 4
        return {"evaluation": eval_result, "next_question": None, "done": True}

    return {"evaluation": eval_result, "next_question": None, "done": False}


async def generate_report(session_id: str):
    """
    Ask the evaluator to synthesize a final report (strengths, weaknesses, recommendations).
    """
    if session_id not in SESSIONS:
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    answers = sess["progress"]["answers"]
    summary_prompt = "Given the following Q&A pairs with evaluations, summarize strengths, weaknesses, and concrete study recommendations. Return JSON with keys 'strengths', 'weaknesses', 'recommendations'.\n\n"
    for a in answers:
        summary_prompt += f"Q: {a['question']}\nA: {a['answer']}\nEval: {a['evaluation']}\n\n"

    evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
    raw = await evaluator.ask(summary_prompt)
    # try to parse JSON
    try:
        import re, json
        m = re.search(r"\{.*\}", raw, re.S)
        parsed = json.loads(m.group(0)) if m else {"raw": raw}
    except Exception:
        parsed = {"raw": raw}
    return {"report": parsed, "answers": answers}


# --- OPTIONAL: how you would use AutoGen's RoundRobinGroupChat/team instead ---
# (This is commented guidance only — the orchestrator above uses direct calls which are easier to debug)
#
# Example (docs show RoundRobinGroupChat exists): you would import:
# from autogen_agentchat.teams import RoundRobinGroupChat
# from autogen_agentchat.conditions import MaxMessageTermination
# and create a team config with the Agent instances as participants. Then `await team.run(task=...)`
#
# See AutoGen teams docs for RoundRobinGroupChat and other team types. :contentReference[oaicite:3]{index=3}
