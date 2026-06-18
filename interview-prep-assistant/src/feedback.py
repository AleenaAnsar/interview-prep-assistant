from groq import Groq


class FeedbackGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def generate_feedback(self, question: str, answer: str, scores: dict, role: str) -> str:
        """Generate feedback based on the answer and scores"""
        
        prompt = f"""Provide constructive feedback for this interview answer.

Role: {role}
Question: {question}
Answer: {answer}
Scores: Relevance={scores.get('relevance')}, Clarity={scores.get('clarity')}, Technical Depth={scores.get('technical_depth')}, Communication={scores.get('communication')}

Give 2-3 specific suggestions for improvement. Be concise and helpful."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        return response.choices[0].message.content