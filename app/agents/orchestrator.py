# app/agents/orchestrator.py
"""
Orchestrator: manages sessions and uses specialized agents to generate questions and evaluate answers.
This version ensures resume & behavioral questions are asked sequentially, one by one.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from app.agents.coding_agent import CodingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.behavior_agent import BehaviorAgent
from app.agents.evaluator_agent import EvaluatorAgent

logger = logging.getLogger(__name__)

# In-memory store for interview sessions
SESSIONS: Dict[str, Dict[str, Any]] = {}

# Initialize agent singletons
logger.info("Initializing agent singletons...")
coding_agent = CodingAgent()
resume_agent = ResumeAgent()
behavior_agent = BehaviorAgent()
logger.info("✅ Agent singletons created")


async def create_session(resume_text: str, jd_text: str, mode: str = "experience", user_name: Optional[str] = "Candidate"):
    """
    Create a new interview session.
    Returns session_id and first question (always coding Q1).
    """
    logger.info("=" * 70)
    logger.info("🚀 CREATE SESSION")
    logger.info("=" * 70)
    logger.info(f"Mode: {mode}")
    logger.info(f"User: {user_name}")
    logger.debug(f"Resume: {len(resume_text)} chars")
    logger.debug(f"JD: {len(jd_text)} chars")
    
    session_id = str(uuid.uuid4())
    logger.info(f"Generated session ID: {session_id}")

    # Evaluator depends on mode (teach/experience)
    evaluator = EvaluatorAgent(mode=mode)
    logger.info(f"Created evaluator with mode: {mode}")

    # Generate coding problem (medium)
    logger.info("Generating coding problem...")
    coding_q = await coding_agent.generate_problem(resume_text=resume_text, jd_text=jd_text, difficulty="medium")
    logger.info("✅ Coding problem generated")
    
    logger.info("Generating coding follow-ups...")
    followups = await coding_agent.generate_followups(coding_q)
    logger.info("✅ Coding follow-ups generated")

    # Generate resume and behavioral questions
    logger.info("Generating resume questions...")
    resume_qs = await resume_agent.generate_questions(resume_text=resume_text, jd_text=jd_text)
    logger.info(f"✅ Generated {len(resume_qs)} resume questions")
    
    logger.info("Generating behavioral questions...")
    behavior_qs = await behavior_agent.generate_questions(count=5)
    logger.info(f"✅ Generated {len(behavior_qs)} behavioral questions")

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
    
    logger.info(f"✅ Session {session_id} created and stored")
    logger.info(f"Total sessions: {len(SESSIONS)}")
    logger.info("=" * 70)

    return {"session_id": session_id, "first_question": coding_q}


async def submit_answer(session_id: str, question: str, answer: str, question_meta: dict = None):
    """
    Evaluate an answer, store progress, and return the next question.
    """
    logger.info("=" * 70)
    logger.info("📝 SUBMIT ANSWER")
    logger.info("=" * 70)
    logger.info(f"Session: {session_id}")
    logger.debug(f"Question: {question[:100]}...")
    logger.debug(f"Answer: {answer[:100]}...")
    
    if session_id not in SESSIONS:
        logger.error(f"❌ Invalid session ID: {session_id}")
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    prog = sess["progress"]
    evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
    
    logger.info(f"Current round: {prog['round']}")
    logger.info(f"Total answers so far: {len(prog['answers'])}")

    # Evaluate
    logger.info("Evaluating answer...")
    eval_result = await evaluator.evaluate(question, answer)
    logger.info(f"✅ Evaluation complete - Score: {eval_result.get('score', 0)}/10")

    # Store answer + evaluation
    prog["answers"].append({
        "question": question,
        "answer": answer,
        "evaluation": eval_result
    })
    logger.info(f"Answer stored. Total answers: {len(prog['answers'])}")

    # -------------------------
    # Interview Flow
    # -------------------------
    
    # Round 1: Coding Q1 -> Coding Q2 (easy/hard)
    if prog["round"] == 1 and len(prog["answers"]) == 1:
        logger.info("Round 1 - After first coding question")
        score = eval_result.get("score", 5)
        logger.info(f"Score: {score}/10")
        
        next_q = sess["questions"]["coding"]["q2_hard"] if score >= 7 else sess["questions"]["coding"]["q2_easy"]
        difficulty = "hard" if score >= 7 else "easy"
        
        logger.info(f"Moving to {difficulty} coding question")
        logger.info("=" * 70)
        
        return {"evaluation": eval_result, "next_question": next_q, "done": False}

    # After Coding Q2 -> Resume round
    if prog["round"] == 1 and len(prog["answers"]) >= 2:
        logger.info("Round 1 complete - Moving to Round 2 (Resume)")
        prog["round"] = 2
        prog["resume_index"] = 0
        
        next_q = sess["questions"]["resume"][prog["resume_index"]]
        logger.info(f"First resume question: {next_q[:50]}...")
        logger.info("=" * 70)
        
        return {
            "evaluation": eval_result,
            "next_question": next_q,
            "done": False
        }

    # Round 2: Resume questions one by one
    if prog["round"] == 2:
        logger.info(f"Round 2 - Resume question {prog['resume_index'] + 1}")
        prog["resume_index"] += 1
        
        if prog["resume_index"] < len(sess["questions"]["resume"]):
            next_q = sess["questions"]["resume"][prog["resume_index"]]
            logger.info(f"Next resume question: {next_q[:50]}...")
            logger.info("=" * 70)
            
            return {
                "evaluation": eval_result,
                "next_question": next_q,
                "done": False
            }
        else:
            logger.info("Round 2 complete - Moving to Round 3 (Behavioral)")
            prog["round"] = 3
            prog["behavior_index"] = 0
            
            next_q = sess["questions"]["behavior"][prog["behavior_index"]]
            logger.info(f"First behavioral question: {next_q[:50]}...")
            logger.info("=" * 70)
            
            return {
                "evaluation": eval_result,
                "next_question": next_q,
                "done": False
            }

    # Round 3: Behavioral questions one by one
    if prog["round"] == 3:
        logger.info(f"Round 3 - Behavioral question {prog['behavior_index'] + 1}")
        prog["behavior_index"] += 1
        
        if prog["behavior_index"] < len(sess["questions"]["behavior"]):
            next_q = sess["questions"]["behavior"][prog["behavior_index"]]
            logger.info(f"Next behavioral question: {next_q[:50]}...")
            logger.info("=" * 70)
            
            return {
                "evaluation": eval_result,
                "next_question": next_q,
                "done": False
            }
        else:
            logger.info("Round 3 complete - Interview finished!")
            prog["round"] = 4
            logger.info("=" * 70)
            
            return {
                "evaluation": eval_result,
                "next_question": None,
                "done": True
            }

    # Default fallback
    logger.warning("Unexpected flow state")
    logger.info("=" * 70)
    return {"evaluation": eval_result, "next_question": None, "done": False}


async def generate_report(session_id: str):
    """
    Compile a final evaluation report with strengths, weaknesses, and recommendations.
    """
    logger.info("=" * 70)
    logger.info("📊 GENERATE REPORT")
    logger.info("=" * 70)
    logger.info(f"Session: {session_id}")
    
    if session_id not in SESSIONS:
        logger.error(f"❌ Invalid session ID: {session_id}")
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    answers = sess["progress"]["answers"]
    
    logger.info(f"Total answers to summarize: {len(answers)}")

    # Build summary prompt
    summary_prompt = (
        "Given the following Q&A pairs with evaluations, summarize strengths, weaknesses, and study recommendations. "
        "Return JSON with keys 'strengths', 'weaknesses', 'recommendations'.\n\n"
    )
    
    for idx, a in enumerate(answers, 1):
        summary_prompt += f"Q{idx}: {a['question'][:100]}...\n"
        summary_prompt += f"A{idx}: {a['answer'][:200]}...\n"
        summary_prompt += f"Eval: {a['evaluation']}\n\n"
    
    logger.debug(f"Summary prompt length: {len(summary_prompt)} chars")

    evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
    
    logger.info("Generating report...")
    raw = await evaluator.ask(summary_prompt)
    logger.info(f"✅ Report generated: {len(raw)} chars")

    # Try parsing JSON from model output
    try:
        import re, json
        m = re.search(r"\{.*\}", raw, re.S)
        parsed = json.loads(m.group(0)) if m else {"raw": raw}
        logger.info("✅ Report parsed successfully")
    except Exception as e:
        logger.error(f"❌ Failed to parse report: {str(e)}")
        parsed = {"raw": raw}
    
    logger.info("=" * 70)

    return {"report": parsed, "answers": answers}


logger.info("✅ Orchestrator module loaded")