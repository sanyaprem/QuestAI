# app/models.py
import logging
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Query(BaseModel):
    """Basic query model"""
    question: str


class StartRequest(BaseModel):
    """Request model for starting an interview"""
    resume_text: str = Field(..., description="Candidate's resume text")
    jd_text: str = Field(..., description="Job description text")
    mode: str = Field(..., description="Interview mode: 'teach' or 'experience'")
    user_name: Optional[str] = Field(default="Candidate", description="Candidate's name")
    collaboration_mode: Optional[str] = Field(
        default="sequential",
        description="Collaboration mode: 'sequential' or 'collaborative'"
    )
    
    def log_request(self):
        """Log the request details"""
        logger.info(f"StartRequest - Mode: {self.mode}, User: {self.user_name}, Collaboration: {self.collaboration_mode}")
        logger.debug(f"Resume length: {len(self.resume_text)} chars")
        logger.debug(f"JD length: {len(self.jd_text)} chars")


class SubmitAnswerReq(BaseModel):
    """Request model for submitting an answer"""
    session_id: str = Field(..., description="Session identifier")
    question: str = Field(..., description="The question being answered")
    answer: str = Field(..., description="Candidate's answer")
    question_meta: dict = Field(default_factory=dict, description="Additional metadata")
    
    def log_request(self):
        """Log the request details"""
        logger.info(f"SubmitAnswerReq - Session: {self.session_id}")
        logger.debug(f"Answer length: {len(self.answer)} chars")


class MatchRequest(BaseModel):
    """Request model for resume-job matching"""
    resume_text: str = Field(..., description="Candidate's resume")
    jd_text: str = Field(..., description="Job description")
    
    def log_request(self):
        """Log the request details"""
        logger.info("MatchRequest received")
        logger.debug(f"Resume: {len(self.resume_text)} chars, JD: {len(self.jd_text)} chars")


logger.info("✅ Models module loaded with enhanced features")