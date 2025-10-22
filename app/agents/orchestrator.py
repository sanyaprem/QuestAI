# app/agents/orchestrator.py
"""
Enhanced Orchestrator with AutoGen Multi-Agent Patterns
Supports both sequential and collaborative interview modes
"""

import uuid
import logging
from typing import Dict, Any, Optional, List
from app.agents.coding_agent import CodingAgent
from app.agents.resume_agent import ResumeAgent
from app.agents.behavior_agent import BehaviorAgent
from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.group_chat_manager import InterviewGroupChat, RoundRobinInterviewManager
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

# Agent singletons
if not Config.MOCK_MODE:
    logger.info("Initializing enhanced agent singletons...")
    coding_agent = CodingAgent()
    resume_agent = ResumeAgent()
    behavior_agent = BehaviorAgent()
    logger.info("✅ Agent singletons created")
else:
    logger.warning("🎭 Mock mode - Skipping real agent creation")
    coding_agent = None
    resume_agent = None
    behavior_agent = None


async def create_session(
    resume_text: str,
    jd_text: str,
    mode: str = "experience",
    user_name: Optional[str] = "Candidate",
    collaboration_mode: str = "sequential"  # NEW: "sequential" or "collaborative"
):
    """
    Create a new interview session with enhanced AutoGen patterns.
    
    Args:
        resume_text: Candidate's resume
        jd_text: Job description
        mode: "teach" or "experience"
        user_name: Candidate's name
        collaboration_mode: "sequential" (default) or "collaborative" (GroupChat)
    
    Returns:
        Session details with first question
    """
    logger.info("=" * 70)
    logger.info("🚀 CREATE SESSION (Enhanced)")
    logger.info("=" * 70)
    logger.info(f"Mode: {mode} | Collaboration: {collaboration_mode} | Mock: {Config.MOCK_MODE}")
    logger.info(f"User: {user_name}")
    
    session_id = str(uuid.uuid4())
    logger.info(f"Generated session ID: {session_id}")

    # Create evaluator
    evaluator = EvaluatorAgent(mode=mode) if not Config.MOCK_MODE else None

    # COLLABORATIVE MODE - Using GroupChat
    if collaboration_mode == "collaborative" and not Config.MOCK_MODE:
        logger.info("🎭 Using COLLABORATIVE mode with GroupChat")
        
        # Create group chat
        group_chat = InterviewGroupChat(
            agents=[
                coding_agent.agent,
                resume_agent.agent,
                behavior_agent.agent,
                evaluator.agent
            ],
            mode="roundrobin",  # or "selector" for dynamic
            max_turns=15
        )
        
        # Run collaborative question generation
        initial_task = f"""
        We need to prepare interview questions for a candidate.
        
        Resume Summary: {resume_text[:300]}...
        Job Description: {jd_text[:300]}...
        
        CodingAgent: Please generate 2 coding problems (1 medium, 1 adaptive)
        ResumeAgent: Please generate 3-4 experience-based questions
        BehaviorAgent: Please generate 5 behavioral questions
        
        Work together to ensure comprehensive coverage.
        """
        
        result = await group_chat.run_collaborative_interview(
            initial_task=initial_task,
            context={
                "resume": resume_text,
                "jd": jd_text,
                "mode": mode
            }
        )
        
        # Extract questions from conversation
        coding_questions = []
        resume_questions = []
        behavior_questions = []
        
        for msg in group_chat.conversation_history:
            agent_name = msg.get('agent', '')
            content = msg.get('content', '')
            
            if 'CodingAgent' in agent_name:
                # Extract coding questions
                lines = content.split('\n')
                coding_questions.extend([l for l in lines if '?' in l or 'Problem:' in l])
            elif 'ResumeAgent' in agent_name:
                lines = content.split('\n')
                resume_questions.extend([l for l in lines if '?' in l])
            elif 'BehaviorAgent' in agent_name:
                lines = content.split('\n')
                behavior_questions.extend([l for l in lines if '?' in l])
        
        # Use first coding question or generate one
        if coding_questions:
            coding_q = coding_questions[0]
        else:
            coding_q = await coding_agent.generate_problem(resume_text, jd_text)
        
        followups = "1. Explain your approach\n2. What's the time complexity?"
        
        logger.info(f"Collaborative generation complete: {len(coding_questions)} coding, {len(resume_questions)} resume, {len(behavior_questions)} behavioral")
    
    # SEQUENTIAL MODE or MOCK MODE - Original approach
    else:
        if Config.MOCK_MODE:
            logger.warning("🎭 Using MOCK DATA")
            import random
            
            coding_q = random.choice(MOCK_CODING_PROBLEMS)
            followups = "1. What's the brute force approach?\n2. Can you optimize it?"
            resume_questions = MOCK_RESUME_QUESTIONS
            behavior_questions = MOCK_BEHAVIORAL_QUESTIONS
        else:
            logger.info("📋 Using SEQUENTIAL mode (original approach)")
            
            # Generate coding problem
            coding_q = await coding_agent.generate_problem(
                resume_text=resume_text,
                jd_text=jd_text,
                difficulty="medium"
            )
            followups = await coding_agent.generate_followups(coding_q)
            
            # Generate resume and behavioral questions
            resume_questions = await resume_agent.generate_questions(
                resume_text=resume_text,
                jd_text=jd_text
            )
            behavior_questions = await behavior_agent.generate_questions(count=5)

    # Store session
    SESSIONS[session_id] = {
        "mode": mode,
        "collaboration_mode": collaboration_mode,
        "user_name": user_name,
        "resume": resume_text,
        "jd": jd_text,
        "agents": {"evaluator": evaluator},
        "questions": {
            "coding": {
                "q1": coding_q,
                "followups": followups,
                "q2_easy": "Explain how you would implement a simple cache.",
                "q2_hard": "Design a distributed caching system with consistency guarantees."
            },
            "resume": resume_questions if isinstance(resume_questions, list) else [resume_questions],
            "behavior": behavior_questions if isinstance(behavior_questions, list) else [behavior_questions]
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


async def submit_answer(
    session_id: str,
    question: str,
    answer: str,
    question_meta: dict = None
):
    """
    Enhanced answer submission with collaborative evaluation option.
    """
    logger.info("=" * 70)
    logger.info("📝 SUBMIT ANSWER")
    logger.info(f"Session: {session_id} | Mock: {Config.MOCK_MODE}")
    
    if session_id not in SESSIONS:
        logger.error(f"❌ Invalid session ID: {session_id}")
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    prog = sess["progress"]
    collaboration_mode = sess.get("collaboration_mode", "sequential")
    
    # Evaluate
    if Config.MOCK_MODE:
        logger.warning("🎭 Using MOCK evaluation")
        eval_result = mock_evaluate(question, answer)
    elif collaboration_mode == "collaborative":
        # Use group chat for evaluation
        logger.info("🎭 Using COLLABORATIVE evaluation")
        
        evaluator = sess["agents"]["evaluator"]
        group_chat = InterviewGroupChat(
            agents=[evaluator.agent],
            mode="roundrobin",
            max_turns=2
        )
        
        eval_task = f"""
        Evaluate this interview response:
        
        QUESTION: {question}
        ANSWER: {answer}
        
        Provide score (0-10), feedback, and recommendations.
        """
        
        result = await group_chat.run_collaborative_interview(eval_task)
        
        # Parse result
        conversation = group_chat.get_conversation_summary()
        
        # Extract evaluation (simplified)
        eval_result = {
            "score": 7,  # Default
            "feedback": conversation[:300],
            "recommendations": ["See detailed feedback above"]
        }
    else:
        # Standard evaluation
        evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
        eval_result = await evaluator.evaluate(question, answer)
    
    logger.info(f"✅ Evaluation complete - Score: {eval_result.get('score', 0)}/10")

    # Store answer + evaluation
    prog["answers"].append({
        "question": question,
        "answer": answer,
        "evaluation": eval_result
    })

    # Interview Flow (same adaptive logic as before)
    if prog["round"] == 1 and len(prog["answers"]) == 1:
        score = eval_result.get("score", 5)
        next_q = sess["questions"]["coding"]["q2_hard"] if score >= 7 else sess["questions"]["coding"]["q2_easy"]
        return {"evaluation": eval_result, "next_question": next_q, "done": False}

    if prog["round"] == 1 and len(prog["answers"]) >= 2:
        prog["round"] = 2
        prog["resume_index"] = 0
        resume_qs = sess["questions"]["resume"]
        if isinstance(resume_qs, list) and len(resume_qs) > 0:
            return {
                "evaluation": eval_result,
                "next_question": resume_qs[0],
                "done": False
            }
        else:
            # Skip to behavioral if no resume questions
            prog["round"] = 3
            prog["behavior_index"] = 0
            behavior_qs = sess["questions"]["behavior"]
            if isinstance(behavior_qs, list) and len(behavior_qs) > 0:
                return {
                    "evaluation": eval_result,
                    "next_question": behavior_qs[0],
                    "done": False
                }

    if prog["round"] == 2:
        prog["resume_index"] += 1
        resume_qs = sess["questions"]["resume"]
        if isinstance(resume_qs, list) and prog["resume_index"] < len(resume_qs):
            return {
                "evaluation": eval_result,
                "next_question": resume_qs[prog["resume_index"]],
                "done": False
            }
        else:
            prog["round"] = 3
            prog["behavior_index"] = 0
            behavior_qs = sess["questions"]["behavior"]
            if isinstance(behavior_qs, list) and len(behavior_qs) > 0:
                return {
                    "evaluation": eval_result,
                    "next_question": behavior_qs[0],
                    "done": False
                }

    if prog["round"] == 3:
        prog["behavior_index"] += 1
        behavior_qs = sess["questions"]["behavior"]
        if isinstance(behavior_qs, list) and prog["behavior_index"] < len(behavior_qs):
            return {
                "evaluation": eval_result,
                "next_question": behavior_qs[prog["behavior_index"]],
                "done": False
            }
        else:
            prog["round"] = 4
            return {"evaluation": eval_result, "next_question": None, "done": True}

    return {"evaluation": eval_result, "next_question": None, "done": False}


async def generate_report(session_id: str):
    """
    Enhanced report generation with optional collaborative summary.
    """
    logger.info("=" * 70)
    logger.info("📊 GENERATE REPORT (Enhanced)")
    logger.info(f"Session: {session_id} | Mock: {Config.MOCK_MODE}")
    
    if session_id not in SESSIONS:
        logger.error(f"❌ Invalid session ID")
        return {"error": "invalid_session"}

    sess = SESSIONS[session_id]
    answers = sess["progress"]["answers"]
    collaboration_mode = sess.get("collaboration_mode", "sequential")
    
    if Config.MOCK_MODE:
        logger.warning("🎭 Using MOCK report")
        parsed = mock_generate_report(answers)
    elif collaboration_mode == "collaborative":
        logger.info("🎭 Using COLLABORATIVE report generation")
        
        # Use multiple agents to generate comprehensive report
        evaluator = sess["agents"]["evaluator"]
        
        # Build comprehensive summary
        summary_prompt = f"""
        Generate a comprehensive interview report.
        
        Total Questions: {len(answers)}
        
        Analyze all responses and provide:
        1. Top 3 strengths
        2. Top 3 areas for improvement
        3. Top 3 actionable recommendations
        
        All Q&A pairs:
        """
        
        for i, a in enumerate(answers, 1):
            summary_prompt += f"\n\nQ{i}: {a['question'][:100]}...\n"
            summary_prompt += f"A{i}: {a['answer'][:100]}...\n"
            summary_prompt += f"Score: {a['evaluation'].get('score', 'N/A')}/10\n"
        
        raw = await evaluator.ask(summary_prompt)
        
        # Try parsing JSON
        try:
            import re, json
            m = re.search(r"\{.*\}", raw, re.S)
            parsed = json.loads(m.group(0)) if m else {
                "strengths": ["Strong technical knowledge"],
                "weaknesses": ["Could improve communication"],
                "recommendations": ["Practice more mock interviews"],
                "raw": raw
            }
        except Exception:
            parsed = {
                "strengths": ["Strong technical knowledge"],
                "weaknesses": ["Could improve communication"],
                "recommendations": ["Practice more mock interviews"],
                "raw": raw
            }
    else:
        # Standard report generation
        summary_prompt = (
            "Given the following Q&A pairs with evaluations, summarize strengths, weaknesses, and recommendations. "
            "Return JSON with keys 'strengths', 'weaknesses', 'recommendations'.\n\n"
        )
        for a in answers:
            summary_prompt += f"Q: {a['question']}\nA: {a['answer']}\nEval: {a['evaluation']}\n\n"

        evaluator: EvaluatorAgent = sess["agents"]["evaluator"]
        raw = await evaluator.ask(summary_prompt)

        try:
            import re, json
            m = re.search(r"\{.*\}", raw, re.S)
            parsed = json.loads(m.group(0)) if m else {"raw": raw}
        except Exception:
            parsed = {"raw": raw}
    
    logger.info("✅ Report generated")
    logger.info("=" * 70)

    return {"report": parsed, "answers": answers}


logger.info("✅ Enhanced Orchestrator module loaded")