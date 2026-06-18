"""
Speech-to-Text Module
Transcribes recorded audio answers using OpenAI's Whisper model (runs locally,
no internet/API call needed for transcription itself).
"""

import os
import tempfile
import whisper

_model_cache = {}


def load_model(model_size: str = "base"):
    """Loads (and caches) a Whisper model. 'base' is a good speed/accuracy tradeoff."""
    if model_size not in _model_cache:
        _model_cache[model_size] = whisper.load_model(model_size)
    return _model_cache[model_size]


def transcribe_audio(audio_bytes: bytes, model_size: str = "base") -> str:
    """
    Takes raw audio bytes (wav format), writes to a temp file, and transcribes with Whisper.
    Returns the transcribed text (empty string if nothing could be transcribed).
    """
    if not audio_bytes:
        return ""

    model = load_model(model_size)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    try:
        result = model.transcribe(tmp_path, fp16=False)
        return result.get("text", "").strip()
    finally:
        os.remove(tmp_path)
