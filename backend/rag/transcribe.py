# ============================================================
# backend/rag/transcribe.py
# Goal: Convert voice input (audio file) → text using Groq Whisper
# ============================================================

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def transcribe_audio(audio_file_path: str, language: str = "hi") -> dict:
    """
    Convert audio file to text using Groq Whisper.
    
    Args:
        audio_file_path: Path to audio file (mp3, wav, m4a, webm)
        language: "hi" for Hindi, "en" for English
    
    Returns:
        {
            "text": str,
            "language": str,
            "success": bool
        }
    """

    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=language,
                response_format="text",
            )

        return {
            "text"    : response.strip(),
            "language": language,
            "success" : True,
        }

    except Exception as e:
        return {
            "text"    : "",
            "language": language,
            "success" : False,
            "error"   : str(e),
        }