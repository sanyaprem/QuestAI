# tests/test_api.py
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import time

BASE_URL = "http://localhost:8000"

def test_root():
    print("\n🧪 TEST: Root Endpoint")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    print("=" * 60)

def test_start_interview():
    print("\n🧪 TEST: Start Interview")
    print("=" * 60)
    payload = {
        "resume_text": "Python developer with 3 years experience",
        "jd_text": "Looking for senior backend engineer",
        "mode": "teach",
        "user_name": "Test User"
    }
    try:
        response = requests.post(f"{BASE_URL}/start_interview", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Interview started")
            print(f"✅ Session ID: {data['session_id']}")
            print(f"✅ First question: {data['first_question'][:100]}...")
            print("=" * 60)
            return data['session_id']
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print("=" * 60)
    return None

def test_submit_answer(session_id):
    print("\n🧪 TEST: Submit Answer")
    print("=" * 60)
    payload = {
        "session_id": session_id,
        "question": "Test question",
        "answer": "I would use a hash map for O(n) complexity.",
        "question_meta": {}
    }
    try:
        response = requests.post(f"{BASE_URL}/submit_answer", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Answer submitted")
            print(f"✅ Evaluation: {str(data['evaluation'])[:100]}...")
        else:
            print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print("=" * 60)

def main():
    print("\n" + "=" * 60)
    print("🚀 STARTING API TESTS")
    print("⚠️ Make sure server is running: uvicorn app.main:app --reload")
    print("=" * 60)
    
    try:
        test_root()
        session_id = test_start_interview()
        if session_id:
            time.sleep(2)
            test_submit_answer(session_id)
        print("\n✅ ALL API TESTS COMPLETE")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("Start server: uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()