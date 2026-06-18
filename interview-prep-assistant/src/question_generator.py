import json
import re
from groq import Groq


class QuestionGenerator:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model


    def generate_questions(self, role: str, experience_level: str,
                            num_questions: int = 5,
                            question_mix: str = "balanced") -> list:
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

CRITICAL: Generate {num_questions} completely UNIQUE questions with NO repetition.
- Each question must cover a DIFFERENT topic/skill
- NO duplicate or similar questions
- Vary the difficulty levels
- Cover different aspects of the role

Return ONLY a valid JSON array (no markdown, no commentary) where each item has:
- "question": the interview question text
- "type": one of "technical", "behavioral", "situational"  
- "difficulty": one of "easy", "medium", "hard"

Example format:
[{{"question": "...", "type": "technical", "difficulty": "medium"}}]"""


        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )


        raw_text = response.choices[0].message.content


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


        lines = [l.strip("-• ").strip() for l in raw_text.splitlines() if l.strip()]
        return [{"question": q, "type": "general", "difficulty": "medium"} for q in lines[:num_questions]]