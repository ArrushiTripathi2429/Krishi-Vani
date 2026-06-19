

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def transcribe_audio(audio_file_path: str, language: str = "hi") -> dict:
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=language,
                response_format="text",
            )

        text = response.strip()

        if not text or len(text) < 3:
            return {
                "text"    : "",
                "language": language,
                "success" : False,
                "error"   : "Empty transcription",
            }

        return {
            "text"    : text,
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