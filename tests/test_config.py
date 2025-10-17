# tests/test_config.py
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import logger, Config, ModelClientFactory

def test_logging():
    print("\n🧪 TEST 1: Logging")
    print("=" * 60)
    logger.info("✅ Test log message INFO")
    logger.debug("✅ Test log message DEBUG")
    logger.warning("⚠️ Test log message WARNING")
    logger.error("❌ Test log message ERROR")
    print("✅ Check logs/quest_ai.log for these messages")
    print("=" * 60)

def test_config_validation():
    print("\n🧪 TEST 2: Config Validation")
    print("=" * 60)
    print(f"Gemini Key: {'✅ Present' if Config.GEMINI_API_KEY else '❌ Missing'}")
    print(f"OpenRouter Key: {'✅ Present' if Config.OPENROUTER_API_KEY else '❌ Missing'}")
    print(f"Current Provider: {Config.CURRENT_PROVIDER}")
    print("=" * 60)

def test_model_client_creation():
    print("\n🧪 TEST 3: Model Client Creation")
    print("=" * 60)
    try:
        client = ModelClientFactory.get_client()
        print(f"✅ Client created successfully")
        print(f"✅ Type: {type(client)}")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
    print("=" * 60)

if __name__ == "__main__":
    test_logging()
    test_config_validation()
    test_model_client_creation()
    print("\n✅ ALL CONFIG TESTS COMPLETE")
    print("📁 Check logs/quest_ai.log for detailed logs")