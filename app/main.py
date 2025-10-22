# app/main.py
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.config import Config, ModelClientFactory
from app.models import StartRequest, SubmitAnswerReq, MatchRequest
from app.agents.orchestrator import create_session, submit_answer, generate_report
from app.agents.evaluator_agent import EvaluatorAgent

logger = logging.getLogger(__name__)

# ============================================
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="QuestAI Interview Agent",
    description="Multi-agent interview simulation with AutoGen GroupChat support",
    version="2.1.0"  # Updated version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("=" * 70)
logger.info("🚀 FastAPI application initialized with AutoGen enhancements")
logger.info("=" * 70)


# ============================================
# STARTUP & SHUTDOWN EVENTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("=" * 70)
    logger.info("🚀 QuestAI Backend Starting (Enhanced)")
    logger.info(f"Version: {app.version}")
    logger.info(f"Current Provider: {Config.CURRENT_PROVIDER}")
    logger.info(f"Mock Mode: {Config.MOCK_MODE}")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("=" * 70)
    logger.info("🛑 QuestAI Backend Shutting Down")
    logger.info(f"Failover Count: {Config.FAILOVER_COUNT}")
    logger.info("=" * 70)


# ============================================
# ENDPOINTS
# ============================================

@app.get("/")
def root():
    """Root endpoint"""
    logger.info("GET / - Root endpoint accessed")
    
    return {
        "message": "QuestAI backend with AutoGen multi-agent support",
        "version": app.version,
        "current_provider": Config.CURRENT_PROVIDER,
        "failover_count": Config.FAILOVER_COUNT,
        "features": [
            "Sequential Orchestration",
            "GroupChat Collaboration (RoundRobin)",
            "Automatic API Failover",
            "Comprehensive Logging"
        ]
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.info("GET /health - Health check")
    
    return {
        "status": "healthy",
        "mock_mode": Config.MOCK_MODE,
        "provider": Config.CURRENT_PROVIDER if not Config.MOCK_MODE else "mock",
        "failover_count": Config.FAILOVER_COUNT
    }


@app.get("/status")
def get_status():
    """Get API status and failover information"""
    logger.info("GET /status - Status check")
    
    status = ModelClientFactory.get_status()
    logger.debug(f"Status: {status}")
    
    return status


@app.post("/start_interview")
async def api_start_interview(req: StartRequest):
    """
    Start a new interview session.
    Supports both sequential and collaborative modes.
    """
    logger.info("=" * 70)
    logger.info("POST /start_interview (Enhanced)")
    logger.info("=" * 70)
    
    req.log_request()
    
    # Check for collaboration_mode in request (optional)
    collaboration_mode = getattr(req, 'collaboration_mode', 'sequential')
    
    try:
        result = await create_session(
            req.resume_text,
            req.jd_text,
            mode=req.mode,
            user_name=req.user_name,
            collaboration_mode=collaboration_mode
        )
        
        logger.info(f"✅ Interview started - Session: {result['session_id']}")
        logger.info("=" * 70)
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error starting interview: {str(e)}", exc_info=True)
        logger.info("=" * 70)
        
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")


@app.post("/start_collaborative_interview")
async def api_start_collaborative_interview(req: StartRequest):
    """
    Start a collaborative interview using AutoGen GroupChat.
    NEW ENDPOINT for explicit collaborative mode.
    """
    logger.info("=" * 70)
    logger.info("POST /start_collaborative_interview")
    logger.info("=" * 70)
    
    req.log_request()
    
    try:
        result = await create_session(
            req.resume_text,
            req.jd_text,
            mode=req.mode,
            user_name=req.user_name,
            collaboration_mode="collaborative"  # Force collaborative mode
        )
        
        logger.info(f"✅ Collaborative interview started - Session: {result['session_id']}")
        logger.info("=" * 70)
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error starting collaborative interview: {str(e)}", exc_info=True)
        logger.info("=" * 70)
        
        raise HTTPException(status_code=500, detail=f"Failed to start collaborative interview: {str(e)}")


@app.post("/submit_answer")
async def api_submit_answer(payload: SubmitAnswerReq):
    """Submit an answer and get evaluation + next question."""
    logger.info("=" * 70)
    logger.info("POST /submit_answer")
    logger.info("=" * 70)
    
    payload.log_request()
    
    try:
        res = await submit_answer(
            payload.session_id,
            payload.question,
            payload.answer,
            payload.question_meta
        )
        
        if "error" in res:
            logger.error(f"❌ Error: {res['error']}")
            logger.info("=" * 70)
            raise HTTPException(status_code=404, detail=res["error"])
        
        logger.info("✅ Answer submitted successfully")
        logger.info("=" * 70)
        
        return res
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error submitting answer: {str(e)}", exc_info=True)
        logger.info("=" * 70)
        
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")


@app.get("/report")
async def api_report(session_id: str):
    """Generate final interview report for a given session."""
    logger.info("=" * 70)
    logger.info("GET /report")
    logger.info("=" * 70)
    logger.info(f"Session: {session_id}")
    
    try:
        rep = await generate_report(session_id)
        
        if "error" in rep:
            logger.error(f"❌ Error: {rep['error']}")
            logger.info("=" * 70)
            raise HTTPException(status_code=404, detail=rep["error"])
        
        logger.info("✅ Report generated successfully")
        logger.info("=" * 70)
        
        return rep
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating report: {str(e)}", exc_info=True)
        logger.info("=" * 70)
        
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@app.post("/match_score")
async def match_score(req: MatchRequest):
    """Check resume–job match percentage + strengths + gaps."""
    logger.info("=" * 70)
    logger.info("POST /match_score")
    logger.info("=" * 70)
    
    req.log_request()
    
    evaluator = EvaluatorAgent(mode="analysis")

    prompt = f"""
    Compare the following resume and job description.

    Resume:
    {req.resume_text[:1000]}

    Job Description:
    {req.jd_text[:1000]}

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

    try:
        raw = await evaluator.ask(prompt)
        logger.debug(f"Raw match response: {raw[:200]}...")

        import re, json
        try:
            m = re.search(r"\{.*\}", raw, re.S)
            parsed = json.loads(m.group(0)) if m else {"raw": raw}
            logger.info("✅ Match score calculated")
        except Exception:
            logger.warning("Failed to parse match response")
            parsed = {"match_percent": 0, "strengths": [], "gaps": [], "raw": raw}

        logger.info("=" * 70)
        return parsed
    
    except Exception as e:
        logger.error(f"❌ Error calculating match score: {str(e)}", exc_info=True)
        logger.info("=" * 70)
        
        raise HTTPException(status_code=500, detail=f"Failed to calculate match: {str(e)}")


logger.info("✅ FastAPI routes configured with AutoGen enhancements")