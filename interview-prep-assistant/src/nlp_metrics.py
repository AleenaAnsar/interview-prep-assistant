"""
NLP Metrics Module
Computes lightweight linguistic metrics on a transcribed answer:
word count, filler-word usage, and readability.
"""

import re
import textstat

FILLER_WORDS = [
    "um", "uh", "uhh", "umm", "like", "you know", "basically",
    "actually", "literally", "kind of", "sort of", "i mean",
]


def compute_metrics(text: str) -> dict:
    if not text or not text.strip():
        return {
            "word_count": 0,
            "filler_count": 0,
            "filler_ratio": 0.0,
            "readability": 0.0,
        }

    words = re.findall(r"\b\w+\b", text.lower())
    word_count = len(words)

    filler_count = 0
    lowered = text.lower()
    for filler in FILLER_WORDS:
        filler_count += len(re.findall(r"\b" + re.escape(filler) + r"\b", lowered))

    filler_ratio = round(filler_count / word_count, 3) if word_count else 0.0

    try:
        readability = textstat.flesch_reading_ease(text)
    except Exception:
        readability = 0.0

    return {
        "word_count": word_count,
        "filler_count": filler_count,
        "filler_ratio": filler_ratio,
        "readability": round(readability, 1),
    }
