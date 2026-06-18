"""
Feedback Generation Module
Produces structured, actionable feedback for a candidate's answer.
"""

from anthropic import Anthropic


class FeedbackGenerator:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def generate_feedback(self, question: str, answer: str, scores: dict, role: str) -> str:
        prompt = f"""You are a supportive but honest interview coach for a "{role}" candidate.

Question: {question}
Candidate's answer: {answer if answer.strip() else "[No answer given]"}
Scores: {scores}

Write concise feedback (under 150 words) with three short sections:
1. Strengths
2. Areas to improve
3. A brief model-answer outline (2-3 bullet points, not a full essay)

Use a direct, encouraging tone. No markdown headers, just clear short paragraphs."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )

        return "".join(b.text for b in response.content if b.type == "text").strip()
