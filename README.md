# QuestAI - AI-Powered Technical Interview Platform

QuestAI is an advanced multi-agent AI interviewer built with FastAPI, Microsoft Autogen, and Streamlit. It simulates realistic technical interviews using **automatic API failover** and **comprehensive logging** for debugging.

## 🌟 Features

### Multi-Agent Architecture
- **CodingAgent**: Generates coding problems with adaptive difficulty
- **ResumeAgent**: Asks questions based on candidate's resume and job description
- **BehaviorAgent**: Conducts behavioral interviews using STAR format
- **EvaluatorAgent**: Scores responses and generates comprehensive reports

### Automatic API Failover
- Seamlessly switches between Gemini and OpenRouter when quota is exceeded
- Zero downtime - users never see API errors
- Full logging of all failover events

### Comprehensive Logging
- Every operation logged with timestamps
- Easy debugging with detailed logs
- Separate logs for backend (`logs/quest_ai.log`) and frontend (`logs/frontend.log`)

### Two Interview Modes
- **Teach Mode**: Learning-focused with detailed feedback and hints
- **Experience Mode**: Realistic mock interview with professional evaluation

### Three Interview Rounds
1. **Coding Round**: Algorithm and data structure problems
2. **Resume Round**: Technical questions about experience
3. **Behavioral Round**: Soft skills and situational questions

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Gemini API key (required)
- OpenRouter API key (optional, for failover)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sanyaprem/QuestAI.git
cd QuestAI
```

2. **Create and activate virtual environment**
```bash
conda create -n ai-agent python=3.10
conda activate ai-agent
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file:
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for failover)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Running the Application

#### Start Backend Server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

#### Start Frontend
In a new terminal:
```bash
cd frontend
streamlit run Home.py
```

The UI will be available at `http://localhost:8501`

## 📁 Project Structure
```
QuestAI/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration with failover
│   ├── models.py            # Pydantic models
│   └── agents/
│       ├── __init__.py
│       ├── base_agent.py    # Base agent with logging
│       ├── coding_agent.py
│       ├── resume_agent.py
│       ├── behavior_agent.py
│       ├── evaluator_agent.py
│       └── orchestrator.py  # Interview orchestration
├── frontend/
│   ├── Home.py              # Landing page
│   ├── utils.py             # Utility functions
│   └── pages/
│       ├── 1_Teach_Mode.py
│       ├── 2_Experience_Mode.py
│       ├── 3_Match_Score.py
│       └── Reports.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_base_agent.py
│   ├── test_coding_agent.py
│   └── test_api.py
├── logs/                    # Log files (auto-created)
├── requirements.txt
├── .env                     # Environment variables
├── .gitignore
└── README.md
```

## 🧪 Testing

Run tests to verify everything works:
```bash
# Test configuration
python tests/test_config.py

# Test agents
python tests/test_base_agent.py
python tests/test_coding_agent.py

# Test API (start server first)
python tests/test_api.py
```

## 📊 Logging

All operations are logged for debugging:

### View Logs
```bash
# Backend logs
cat logs/quest_ai.log

# Frontend logs
cat logs
cat logs/frontend.log

# Follow logs in real-time
tail -f logs/quest_ai.log
```

### Log Format
```
2024-10-17 15:30:45 - app.agents.base_agent - INFO - 🤖 CodingAgent - Call #1
2024-10-17 15:30:45 - app.agents.base_agent - INFO - 📝 Prompt: Generate a coding problem...
2024-10-17 15:30:47 - app.agents.base_agent - INFO - ✅ CodingAgent responded successfully
```

### When Failover Occurs
```
2024-10-17 15:30:00 - app.agents.base_agent - ERROR - ❌ ERROR in CodingAgent
2024-10-17 15:30:00 - app.agents.base_agent - ERROR - ❌ Error message: Quota exceeded
2024-10-17 15:30:01 - app.config - WARNING - ⚠️ FAILOVER TRIGGERED!
2024-10-17 15:30:02 - app.config - INFO - 🔄 Switching from gemini to openrouter...
2024-10-17 15:30:03 - app.config - INFO - ✅ FAILOVER SUCCESSFUL!

###API Endpoints
```
Start Interview
```bash
POST /start_interview
Content-Type: application/json

{
  "resume_text": "Python developer with 3 years experience...",
  "jd_text": "Looking for senior backend engineer...",
  "mode": "teach",
  "user_name": "John Doe"
}
```

Submit Answer
```bash
POST /submit_answer
Content-Type: application/json

{
  "session_id": "abc-123",
  "question": "What is a hash map?",
  "answer": "A hash map is a data structure...",
  "question_meta": {}
}
```

Generate Report
```bash
GET /report?session_id=abc-123
```

Check Status
```bash
GET /status
```
Response
```bash
{
  "current_provider": "gemini",
  "failover_count": 0,
  "has_gemini_key": true,
  "has_openrouter_key": true,
  "switch_history": []
}
```

## 🎯 How Automatic Failover Works

1. **Normal Operation**: All requests go to Gemini (primary provider)
2. **Quota Exceeded**: Gemini returns quota error
3. **Auto Switch**: System automatically switches to OpenRouter
4. **Retry**: Original request is retried with OpenRouter
5. **Success**: User receives response without knowing there was an issue
```
Request → Gemini API → Quota Error
                ↓
         Detect Error
                ↓
      Switch to OpenRouter
                ↓
         Retry Request
                ↓
         Success! ✅
```

## Configuration

Adjust Settings in app/config.py
```bash
class Config:
    # Which provider to use first
    PRIMARY_PROVIDER = "gemini"
    BACKUP_PROVIDER = "openrouter"
    
    # Model settings
    TEMPERATURE = 0.7  # 0=deterministic, 1=creative
    
    # Timeouts
    TIMEOUT = 300  # seconds
```

Change log level
```bash
# In app/config.py
console_handler.setLevel(logging.DEBUG)  # More verbose
console_handler.setLevel(logging.WARNING)  # Less verbose
```

## Troubleshooting

Issue: Logs not appearing in file
Solution:
```bash
# Check if logs directory exists
ls -la logs/

# Create it if missing
mkdir -p logs

# Check permissions
chmod 755 logs
```

Issue: "Module not found" error
Solution:
```bash
# Make sure you're in project root
cd /path/to/QuestAI

# Run as module
python -m tests.test_config

# Or add to path
export PYTHONPATH=$PWD  # Linux/Mac
$env:PYTHONPATH = $PWD  # Windows PowerShell
```
Issue: Backend not connecting
Solution:
```bash
# Check if server is running
curl http://localhost:8000/health

# Check logs
cat logs/quest_ai.log

# Restart server
uvicorn app.main:app --reload
```

Issue: API quota exceeded
Solution:
```bash
The system should automatically failover to the backup provider. Check logs:

grep "FAILOVER" logs/quest_ai.log
```

If both APIs are exhausted, you'll see:
```
❌ RETRY FAILED! Both providers exhausted

```

📚 Usage Examples

Example 1: Start Interview with Logging

```bash
import requests

response = requests.post("http://localhost:8000/start_interview", json={
    "resume_text": "Python developer with 3 years experience",
    "jd_text": "Looking for backend engineer",
    "mode": "teach",
    "user_name": "Alice"
})

print(response.json())
# Check logs: tail -f logs/quest_ai.log
```

Example 2: Monitor Failover
```bash
import requests

# Get current status
status = requests.get("http://localhost:8000/status").json()
print(f"Current provider: {status['current_provider']}")
print(f"Failover count: {status['failover_count']}")
print(f"Switch history: {status['switch_history']}")

```

Example 3: View Agent Statistics
```bash
from app.agents.coding_agent import CodingAgent
import asyncio

async def main():
    agent = CodingAgent()
    
    # Make some calls
    await agent.generate_problem(resume_text="...", jd_text="...")
    await agent.generate_problem(resume_text="...", jd_text="...")
    
    # Get stats
    stats = agent.get_stats()
    print(stats)
    # {'name': 'CodingAgent', 'call_count': 2, 'error_count': 0, 'success_rate': '100.0%'}

asyncio.run(main())
```

## 🎓 Learning Resources

### Understanding the Code

1. **Start with `app/config.py`**: See how logging and failover are set up
2. **Read `app/agents/base_agent.py`**: Understand how agents work
3. **Check `app/agents/orchestrator.py`**: See how interview flow works
4. **Look at `app/main.py`**: See how API endpoints are defined

### Key Concepts

**Logging:**
- Every important action is logged
- Logs help you debug issues
- Check logs when something goes wrong

**Failover:**
- Primary provider fails → Automatically switch to backup
- Transparent to users
- All switches are logged

**Agents:**
- Each agent has a specific role (coding, resume, behavior)
- All inherit from `BaseAgent`
- Automatic retry on failure

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add comprehensive logging to new code
4. Write tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Microsoft Autogen**: Multi-agent framework
- **OpenAI/Gemini**: AI models
- **FastAPI**: Backend framework
- **Streamlit**: Frontend framework

## 📧 Support

For issues or questions:
- Check logs first: `cat logs/quest_ai.log`
- Open an issue on GitHub
- Read the troubleshooting section above

## 🔄 Version History

### v2.0.0 (Current)
- ✅ Added automatic API failover
- ✅ Comprehensive logging at every step
- ✅ Improved error handling
- ✅ Better session management
- ✅ Enhanced debugging capabilities

### v1.0.0
- Initial release
- Basic multi-agent system
- Two interview modes
- Three interview rounds

---

Built with ❤️ for interview preparation

**Happy Interviewing! 🚀**
