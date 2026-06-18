"""
Question Generator Module
Generates role-specific interview questions using Claude (Anthropic LLM).
"""

import json
import re
from anthropic import Anthropic


class QuestionGenerator:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def generate_questions(self, role: str, experience_level: str,
                            num_questions: int = 5,
                            question_mix: str = "balanced") -> list:
        """
        Generate a list of interview questions.
        Returns a list of dicts: {"question": str, "type": str, "difficulty": str}
        """
        mix_instructions = {
            "technical": "Focus mostly on technical/domain questions.",
            "behavioral": "Focus mostly on behavioral/HR questions.",
            "balanced": "Mix technical, behavioral, and situational questions evenly.",
        }.get(question_mix, "Mix technical, behavioral, and situational questions evenly.")

        prompt = f"""You are an experienced technical recruiter preparing an interview.

Role: {role}
Candidate experience level: {experience_level}
Number of questions: {num_questions}
Instruction: {mix_instructions}

Return ONLY a valid JSON array (no markdown, no commentary) where each item has:
- "question": the interview question text
- "type": one of "technical", "behavioral", "situational"
- "difficulty": one of "easy", "medium", "hard"

Example format:
[{{"question": "...", "type": "technical", "difficulty": "medium"}}]
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = "".join(
            block.text for block in response.content if block.type == "text"
        )

        return self._parse_questions(raw_text, num_questions)

    @staticmethod
    def _parse_questions(raw_text: str, num_questions: int) -> list:
        cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
        try:
            questions = json.loads(cleaned)
            if isinstance(questions, list) and questions:
                return questions[:num_questions]
        except json.JSONDecodeError:
            pass

        # Fallback: treat each non-empty line as a question
        lines = [l.strip("-• ").strip() for l in raw_text.splitlines() if l.strip()]
        return [{"question": q, "type": "general", "difficulty": "medium"} for q in lines[:num_questions]]
