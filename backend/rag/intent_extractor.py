# ============================================================
# backend/rag/intent_extractor.py
# Goal: Extract crop, district, zone from farmer query using Groq
# ============================================================

import os
import json
from groq import Groq
from dotenv import load_dotenv
from retriever import get_zone_from_district


load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_intent(query: str) -> dict:
    """
    Use Groq LLM to extract structured info from farmer query.

    Returns:
        {
            "crop": str or None,
            "district": str or None,
            "agro_zone": str or None,
            "translated_query": str,
            "language_detected": str
        }
    """

    prompt = f"""Extract information from this farmer query. Return ONLY a JSON object, nothing else.

Query: "{query}"

Return this exact JSON format:
{{
  "crop": "crop name in English or null",
  "district": "UP district name in caps or null",
  "language_detected": "hindi/english/hinglish",
  "translated_query": "English translation of the query"
}}

Common crops: Wheat, Paddy (Dhan), Sugarcane, Potato, Mustard, Mango, Mentha, Tomato, Onion
Common UP districts: LUCKNOW, RAE BARELI, VARANASI, AGRA, GORAKHPUR, JHANSI, ALLAHABAD, KANPUR NAGAR"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=200,
    )

    raw = response.choices[0].message.content.strip()

    # Parse JSON safely
    try:
        # Remove markdown code blocks if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        extracted = json.loads(raw)
    except Exception:
        # Fallback if JSON parsing fails
        extracted = {
            "crop"             : None,
            "district"         : None,
            "language_detected": "hinglish",
            "translated_query" : query,
        }

    # Map district → agro zone
    district = extracted.get("district")
    extracted["agro_zone"] = get_zone_from_district(district) if district else None

    return extracted
