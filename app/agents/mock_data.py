# app/agents/mock_data.py
"""
Mock data for testing without API calls
"""

import random
import time

MOCK_CODING_PROBLEMS = [
    """**Coding Problem: Two Sum**

Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

**Constraints:**
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- Only one valid answer exists

**Example:**
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: nums[0] + nums[1] = 2 + 7 = 9

**Expected Time Complexity:** O(n)
**Expected Space Complexity:** O(n)""",

#     """**Coding Problem: Reverse Linked List**

# Given the head of a singly linked list, reverse the list and return the reversed list.

# **Constraints:**
# - The number of nodes in the list is in the range [0, 5000]
# - -5000 <= Node.val <= 5000

# **Example:**
# Input: 1 -> 2 -> 3 -> 4 -> 5
# Output: 5 -> 4 -> 3 -> 2 -> 1

# **Expected Time Complexity:** O(n)
# **Expected Space Complexity:** O(1)"""
]

MOCK_RESUME_QUESTIONS = [
    "Tell me about your experience with Python. What projects have you built using Python?",
    # "I see you have experience with FastAPI. Can you explain how you've used it in production?",
    # "What's the most challenging technical problem you've solved in your recent projects?",
    # "How do you handle API rate limiting in your applications?"
]

MOCK_BEHAVIORAL_QUESTIONS = [
    "Tell me about a time when you had to deal with a difficult team member. How did you handle it?",
    # "Describe a situation where you had to learn a new technology quickly. What was your approach?",
    # "Tell me about a time when you made a mistake in your code that went to production. How did you handle it?",
    # "Describe a situation where you had to explain a complex technical concept to a non-technical stakeholder."
]

def mock_evaluate(question: str, answer: str) -> dict:
    """Generate mock evaluation"""
    time.sleep(0.5)  # Simulate API delay
    
    score = random.randint(6, 10)
    
    feedbacks = [
        f"Good approach! You demonstrated understanding of the core concepts. Score: {score}/10",
        f"Solid answer with some room for improvement. You covered the main points effectively. Score: {score}/10",
        f"Excellent response! You showed deep understanding and practical knowledge. Score: {score}/10",
        f"Nice work! Your explanation was clear and well-structured. Score: {score}/10"
    ]
    
    recommendations = [
        ["Consider edge cases in your solution", "Think about time complexity optimization", "Add error handling"],
        ["Explain your thought process more clearly", "Provide concrete examples", "Discuss trade-offs"],
        ["Consider scalability aspects", "Think about memory usage", "Add unit tests"]
    ]
    
    return {
        "score": score,
        "feedback": random.choice(feedbacks),
        "recommendations": random.choice(recommendations)
    }

def mock_generate_report(answers: list) -> dict:
    """Generate mock final report"""
    time.sleep(1)  # Simulate processing
    
    avg_score = sum(a['evaluation']['score'] for a in answers) / len(answers) if answers else 0
    
    strengths = [
        "Strong problem-solving skills demonstrated throughout the interview",
        "Clear communication and ability to explain complex concepts",
        "Good understanding of data structures and algorithms",
        "Practical experience with modern development tools"
    ]
    
    weaknesses = [
        "Could improve time complexity analysis",
        "More practice needed with system design concepts",
        "Consider edge cases more carefully",
        "Work on explaining trade-offs in solutions"
    ]
    
    recommendations = [
        "Practice more LeetCode medium/hard problems",
        "Study system design patterns",
        "Read about scalability best practices",
        "Work on communication skills for technical interviews"
    ]
    
    return {
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "recommendations": recommendations[:3],
        "overall_score": int(avg_score * 10),
        "summary": f"Overall performance was {'excellent' if avg_score >= 8 else 'good' if avg_score >= 6 else 'satisfactory'}. The candidate demonstrated {avg_score:.1f}/10 average competency across all rounds."
    }