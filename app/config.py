# # from autogen_agentchat.agents import AssistantAgent
# from autogen_ext.models.openai import OpenAIChatCompletionClient
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # --- Gemini Config ---
# GEMINI_API_KEY = os.getenv("gemini_api_key")
# GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-8b")
# GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

# # --- OpenRouter Config ---
# OPENROUTER_API_KEY = os.getenv("openrouter_api_key")
# OPENROUTER_MODEL = os.getenv("openrouter_model", "deepseek/deepseek-chat-v3.1:free")
# OPENROUTER_BASE_URL = os.getenv("openrouter_base_url", "https://openrouter.ai/api/v1")

# # --- General Defaults ---
# DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini")  # "gemini" | "openrouter"
# model_client = OpenAIChatCompletionClient(
#      base_url="https://openrouter.ai/api/v1",
#      model="deepseek/deepseek-chat-v3.1:free",
#      api_key = os.getenv("OPENROUTER_API_KEY"),
#      model_info={
#          "family":'deepseek',
#          "vision" :True,
#          "function_calling":True,
#          "json_output": False
#      }
# )

# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.5-flash",
#     api_key=os.getenv("GEMINI_API_KEY")
# )


# app/config.py
# app/config.py
import os
import sys
import logging
import pathlib
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Load environment variables
load_dotenv()

# ============================================
# LOGGING SETUP (ROBUST VERSION)
# ============================================

def setup_logging():
    """Setup logging with both file and console handlers"""
    
    # Create logs directory
    log_dir = pathlib.Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "quest_ai.log"
    
    # Define format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # File Handler (detailed logs)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console Handler (less verbose)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Test it works
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("✅ Logging initialized successfully")
    logger.info(f"📁 Log file: {log_file.absolute()}")
    logger.info("=" * 70)
    
    return log_file

# Initialize logging
LOG_FILE_PATH = setup_logging()
logger = logging.getLogger(__name__)

# ============================================
# REST OF YOUR CONFIG
# ============================================

class Config:
    """Application configuration with automatic API failover"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Model Configuration
    PRIMARY_PROVIDER = "gemini"
    GEMINI_MODEL = "gemini-2.5-flash"
    OPENROUTER_MODEL = "deepseek/deepseek-chat-v3.1:free"
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    TEMPERATURE = 0.7
    MAX_ROUND_ROBIN_TURNS = 3
    TIMEOUT = 300
    
    CURRENT_PROVIDER = PRIMARY_PROVIDER
    FAILOVER_COUNT = 0
    
    ROUNDS = {
        1: "Coding",
        2: "Resume",
        3: "Behavioral"
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        logger.info("🔍 Validating configuration...")
        
        has_gemini = bool(cls.GEMINI_API_KEY)
        has_openrouter = bool(cls.OPENROUTER_API_KEY)
        
        if not has_gemini and not has_openrouter:
            logger.critical("❌ CRITICAL: No API keys found!")
            raise ValueError("At least one API key must be set")
        
        if has_gemini:
            logger.info("✅ Gemini API key found")
        if has_openrouter:
            logger.info("✅ OpenRouter API key found")
        
        if has_gemini and has_openrouter:
            logger.info("🎉 Both API keys available - Failover enabled!")
        
        logger.info("✅ Configuration validated")

class ModelClientFactory:
    """Factory to create and manage model clients with failover"""
    
    _current_client = None
    _client_history = []
    
    @classmethod
    def create_client(cls, provider: Optional[str] = None):
        """Create a model client"""
        if provider is None:
            provider = Config.CURRENT_PROVIDER
        
        logger.info(f"🔧 Creating model client for: {provider}")
        
        if provider == "gemini":
            return cls._create_gemini_client()
        elif provider == "openrouter":
            return cls._create_openrouter_client()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @classmethod
    def _create_gemini_client(cls):
        """Create Gemini client"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        logger.info(f"✅ Creating Gemini client: {Config.GEMINI_MODEL}")
        
        client = OpenAIChatCompletionClient(
            model=Config.GEMINI_MODEL,
            api_key=Config.GEMINI_API_KEY
        )
        
        logger.info("✅ Gemini client created")
        return client
    
    @classmethod
    def _create_openrouter_client(cls):
        """Create OpenRouter client"""
        if not Config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        logger.info(f"✅ Creating OpenRouter client: {Config.OPENROUTER_MODEL}")
        
        client = OpenAIChatCompletionClient(
            base_url=Config.OPENROUTER_BASE_URL,
            model=Config.OPENROUTER_MODEL,
            api_key=Config.OPENROUTER_API_KEY,
            model_info={
                "family": "deepseek",
                "vision": True,
                "function_calling": True,
                "json_output": False
            }
        )
        
        logger.info("✅ OpenRouter client created")
        return client
    
    @classmethod
    def get_client(cls):
        """Get current active client"""
        if cls._current_client is None:
            logger.info("📡 Creating initial client...")
            cls._current_client = cls.create_client()
        return cls._current_client
    
    @classmethod
    def switch_to_backup(cls, error_msg: str = ""):
        """Switch to backup provider"""
        current = Config.CURRENT_PROVIDER
        
        logger.warning("⚠️" + "=" * 60)
        logger.warning("⚠️ FAILOVER TRIGGERED!")
        logger.warning(f"⚠️ Current: {current}, Error: {error_msg}")
        logger.warning("⚠️" + "=" * 60)
        
        backup = "openrouter" if current == "gemini" else "gemini"
        
        if backup == "gemini" and not Config.GEMINI_API_KEY:
            raise ValueError("Cannot failover to Gemini - no API key")
        if backup == "openrouter" and not Config.OPENROUTER_API_KEY:
            raise ValueError("Cannot failover to OpenRouter - no API key")
        
        logger.info(f"🔄 Switching from {current} to {backup}...")
        
        Config.CURRENT_PROVIDER = backup
        Config.FAILOVER_COUNT += 1
        cls._current_client = cls.create_client(backup)
        
        cls._client_history.append({
            "from": current,
            "to": backup,
            "reason": error_msg,
            "count": Config.FAILOVER_COUNT
        })
        
        logger.info("✅" + "=" * 60)
        logger.info(f"✅ Failover successful! Now using: {backup}")
        logger.info("✅" + "=" * 60)
        
        return cls._current_client
    
    @classmethod
    def get_status(cls):
        """Get client status"""
        return {
            "current_provider": Config.CURRENT_PROVIDER,
            "failover_count": Config.FAILOVER_COUNT,
            "has_gemini": bool(Config.GEMINI_API_KEY),
            "has_openrouter": bool(Config.OPENROUTER_API_KEY),
            "history": cls._client_history
        }

# Initialize
logger.info("🚀 QuestAI Configuration Loading...")
Config.validate()
logger.info(f"📡 Initializing primary provider: {Config.CURRENT_PROVIDER}")
model_client = ModelClientFactory.get_client()
logger.info("✅ Configuration loaded successfully!")