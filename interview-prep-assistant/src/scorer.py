import json
from groq import Groq


class AnswerScorer:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def score_answer(self, question: str, answer: str, role: str) -> dict:
        """Score the answer based on relevance, clarity, technical depth, communication"""
        
        prompt = f"""Score this interview answer on a scale of 1-10 for each criterion:

Question: {question}
Answer: {answer}
Role: {role}

Score each criterion (1-10):
1. Relevance: How relevant is the answer to the question?
2. Clarity: How clear and well-structured is the answer?
3. Technical Depth: How technically accurate and deep is the answer?
4. Communication: How well does the person communicate their ideas?

Return ONLY JSON in this format:
{{
    "relevance": 8,
    "clarity": 7,
    "technical_depth": 9,
    "communication": 8,
    "overall": 8
}}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        scores_text = response.choices[0].message.content
        
        try:
            scores = json.loads(scores_text)
            return scores
        except json.JSONDecodeError:
            return {
                "relevance": 5,
                "clarity": 5,
                "technical_depth": 5,
                "communication": 5,
                "overall": 5
            }