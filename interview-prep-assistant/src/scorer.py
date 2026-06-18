"""
Answer Scoring Module
Uses Claude to evaluate an interview answer on multiple dimensions,
then blends in NLP-based signals (filler-word usage) as a penalty.
"""

import json
import re
from anthropic import Anthropic

from .nlp_metrics import compute_metrics


class AnswerScorer:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def score_answer(self, question: str, answer: str, role: str) -> dict:
        metrics = compute_metrics(answer)

        prompt = f"""You are an expert technical interviewer evaluating a candidate's spoken answer
for a "{role}" position.

Question: {question}
Candidate's answer (transcribed from speech): {answer if answer.strip() else "[No answer given]"}

Score the answer from 0-10 on each dimension below. Be strict and realistic;
a vague or empty answer should score low.

Return ONLY valid JSON (no markdown) with this exact structure:
{{
  "relevance": <0-10>,
  "clarity": <0-10>,
  "technical_depth": <0-10>,
  "communication": <0-10>,
  "overall": <0-10>,
  "justification": "<2-3 sentence explanation>"
}}
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = "".join(b.text for b in response.content if b.type == "text")
        scores = self._parse_scores(raw_text)

        # Light penalty for excessive filler words, never below 0
        if metrics["filler_ratio"] > 0.08:
            penalty = min(1.5, metrics["filler_ratio"] * 10)
            scores["overall"] = max(0, round(scores["overall"] - penalty, 1))

        scores["metrics"] = metrics
        return scores

    @staticmethod
    def _parse_scores(raw_text: str) -> dict:
        cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
        try:
            data = json.loads(cleaned)
            for key in ("relevance", "clarity", "technical_depth", "communication", "overall"):
                data.setdefault(key, 0)
            data.setdefault("justification", "")
            return data
        except json.JSONDecodeError:
            return {
                "relevance": 0, "clarity": 0, "technical_depth": 0,
                "communication": 0, "overall": 0,
                "justification": "Could not parse model response.",
            }
