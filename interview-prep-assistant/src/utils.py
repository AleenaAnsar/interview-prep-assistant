"""
Utility helpers shared across the app.
"""

import os
from dotenv import load_dotenv


def get_api_key() -> str:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not found. Create a .env file with "
            "ANTHROPIC_API_KEY=your_key_here (see .env.example)."
        )
    return api_key


def build_report(role: str, results: list) -> str:
    """Builds a plain-text summary report from a list of per-question results."""
    lines = [f"Interview Report - Role: {role}", "=" * 50, ""]
    overall_scores = []

    for i, r in enumerate(results, start=1):
        lines.append(f"Q{i}: {r['question']}")
        lines.append(f"Your answer: {r['answer'] or '[No answer given]'}")
        s = r["scores"]
        overall_scores.append(s.get("overall", 0))
        lines.append(
            f"Scores - Relevance: {s.get('relevance')}, Clarity: {s.get('clarity')}, "
            f"Technical depth: {s.get('technical_depth')}, Communication: {s.get('communication')}, "
            f"Overall: {s.get('overall')}/10"
        )
        lines.append(f"Feedback: {r['feedback']}")
        lines.append("-" * 50)

    if overall_scores:
        avg = round(sum(overall_scores) / len(overall_scores), 1)
        lines.insert(2, f"Average score: {avg}/10\n")

    return "\n".join(lines)
