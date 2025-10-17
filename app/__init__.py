# app/__init__.py
"""
QuestAI Backend Application
Multi-agent AI interviewer with RoundRobin orchestration
"""

import logging

logger = logging.getLogger(__name__)
logger.info("QuestAI backend package initialized")

__version__ = "2.0.0"
__author__ = "QuestAI Team"
__description__ = "AI-Powered Technical Interview Platform"