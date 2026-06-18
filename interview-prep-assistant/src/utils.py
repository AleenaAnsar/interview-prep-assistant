import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    """Get Groq API key from environment"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Set it in your .env file")
    return api_key

def build_report(role: str, results: list) -> str:
    """Build a text report from interview results"""
    report = f"Interview Preparation Report\n"
    report += f"Role: {role}\n"
    report += f"Total Questions: {len(results)}\n"
    report += f"================================\n\n"
    
    for i, r in enumerate(results, start=1):
        report += f"Q{i}: {r['question']}\n"
        report += f"A: {r['answer']}\n"
        report += f"Scores: {r['scores']}\n"
        report += f"Feedback: {r['feedback']}\n\n"
    
    return report