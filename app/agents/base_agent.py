# app/agents/base_agent.py
import asyncio
import json
import logging
from typing import Any, Optional
from app.config import ModelClientFactory, Config

# Import AssistantAgent
try:
    from autogen_agentchat.agents import AssistantAgent
except Exception:
    try:
        from autogen import AssistantAgent
    except Exception as e:
        raise ImportError("Could not import AssistantAgent.") from e

# Create logger for this file
logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all interview agents.
    Handles API calls with automatic failover and comprehensive logging.
    """
    
    def __init__(self, name: str, system_message: str):
        """
        Initialize a base agent.
        
        Args:
            name: Agent name (e.g., "CodingAgent")
            system_message: Instructions for the agent
        """
        logger.info("=" * 60)
        logger.info(f"🤖 Creating {name}")
        logger.info("=" * 60)
        logger.debug(f"System message: {system_message[:100]}...")
        
        # Get the current model client
        model_client = ModelClientFactory.get_client()
        
        # Create the Autogen agent
        self.agent = AssistantAgent(
            name=name,
            system_message=system_message,
            model_client=model_client
        )
        
        self.name = name
        self.system_message = system_message
        self.call_count = 0  # Track how many times this agent was called
        self.error_count = 0  # Track errors
        
        logger.info(f"✅ {name} created successfully")
        logger.info(f"📊 Using provider: {Config.CURRENT_PROVIDER}")
        logger.info("=" * 60)
    
    async def ask(self, prompt: str, retry_on_failure: bool = True) -> str:
        """
        Send a prompt to the agent and get a response.
        Automatically handles failover if API quota is exceeded.
        
        Args:
            prompt: The question/task for the agent
            retry_on_failure: Whether to retry with backup API on failure
            
        Returns:
            Agent's response as string
        """
        self.call_count += 1
        
        logger.info("─" * 60)
        logger.info(f"🤖 {self.name} - Call #{self.call_count}")
        logger.info(f"📝 Prompt: {prompt[:150]}...")
        logger.debug(f"📝 Full prompt: {prompt}")
        logger.info(f"🌐 Current provider: {Config.CURRENT_PROVIDER}")
        logger.info("─" * 60)
        
        try:
            # Attempt to call the agent
            logger.debug(f"⏳ Sending request to {Config.CURRENT_PROVIDER}...")
            result = await self.agent.run(task=prompt)
            
            # Extract response
            response = self._extract_response(result)
            
            logger.info(f"✅ {self.name} responded successfully")
            logger.info(f"📤 Response length: {len(response)} characters")
            logger.debug(f"📤 Response preview: {response[:200]}...")
            logger.info("─" * 60)
            
            return response
        
        except Exception as e:
            self.error_count += 1
            error_msg = str(e)
            
            logger.error("❌" + "=" * 60)
            logger.error(f"❌ ERROR in {self.name}")
            logger.error(f"❌ Error #{self.error_count}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Error message: {error_msg}")
            logger.error("❌" + "=" * 60)
            
            # Check if it's a quota/rate limit error
            is_quota_error = self._is_quota_error(error_msg)
            
            if is_quota_error and retry_on_failure:
                logger.warning("🔄 Detected quota/rate limit error")
                logger.warning("🔄 Attempting automatic failover...")
                
                try:
                    # Switch to backup provider
                    new_client = ModelClientFactory.switch_to_backup(error_msg)
                    
                    # Update this agent's client
                    self.agent.model_client = new_client
                    
                    logger.info("🔄 Retrying with new provider...")
                    
                    # Retry the request
                    result = await self.agent.run(task=prompt)
                    response = self._extract_response(result)
                    
                    logger.info("✅" + "=" * 60)
                    logger.info(f"✅ {self.name} retry SUCCESSFUL")
                    logger.info(f"✅ Now using: {Config.CURRENT_PROVIDER}")
                    logger.info("✅" + "=" * 60)
                    
                    return response
                
                except Exception as retry_error:
                    logger.critical("❌" + "=" * 60)
                    logger.critical("❌ RETRY FAILED!")
                    logger.critical(f"❌ Retry error: {str(retry_error)}")
                    logger.critical("❌ Both providers exhausted")
                    logger.critical("❌" + "=" * 60)
                    
                    return f"ERROR: Both API providers failed. Original: {error_msg}, Retry: {str(retry_error)}"
            
            else:
                # Not a quota error, or retry disabled
                logger.error(f"❌ Not attempting failover (quota_error={is_quota_error}, retry={retry_on_failure})")
                return f"ERROR_CALLING_AGENT: {error_msg}"
    
    def _extract_response(self, result: Any) -> str:
        """
        Extract text response from agent result.
        
        Args:
            result: The result object from agent.run()
            
        Returns:
            Extracted response text
        """
        logger.debug("🔍 Extracting response from result...")
        
        # Try different ways to extract the response
        if hasattr(result, "messages") and result.messages:
            response = result.messages[-1].content
            logger.debug(f"✅ Extracted from messages (count: {len(result.messages)})")
            return response
        
        if hasattr(result, "content"):
            response = result.content
            logger.debug("✅ Extracted from content attribute")
            return response
        
        # Fallback: convert to string
        response = str(result)
        logger.debug("⚠️ Used fallback str() conversion")
        return response
    
    def _is_quota_error(self, error_msg: str) -> bool:
        """
        Check if error message indicates quota/rate limit exceeded.
        
        Args:
            error_msg: Error message string
            
        Returns:
            True if it's a quota error
        """
        error_lower = error_msg.lower()
        
        quota_keywords = [
            "quota",
            "rate limit",
            "too many requests",
            "429",
            "resource exhausted",
            "limit exceeded",
            "insufficient_quota",
        ]
        
        for keyword in quota_keywords:
            if keyword in error_lower:
                logger.debug(f"🔍 Quota error detected: keyword '{keyword}' found")
                return True
        
        return False
    
    def get_stats(self) -> dict:
        """
        Get statistics about this agent's usage.
        
        Returns:
            Dictionary with call count, errors, etc.
        """
        return {
            "name": self.name,
            "call_count": self.call_count,
            "error_count": self.error_count,
            "success_rate": f"{((self.call_count - self.error_count) / max(self.call_count, 1)) * 100:.1f}%",
            "current_provider": Config.CURRENT_PROVIDER
        }
    
    def reset_stats(self):
        """Reset usage statistics"""
        logger.info(f"🔄 Resetting stats for {self.name}")
        self.call_count = 0
        self.error_count = 0


# Helper function for backwards compatibility
async def _maybe_await(value: Any) -> Any:
    """Await a value if it's a coroutine, otherwise return as-is"""
    if asyncio.iscoroutine(value):
        return await value
    return value


logger.info("✅ BaseAgent module loaded successfully")