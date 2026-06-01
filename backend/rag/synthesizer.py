# ============================================================
# backend/rag/synthesizer.py
# Goal: Take retrieved chunks + user query → Groq → final answer
# ============================================================

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def synthesize(
    query: str,
    retrieved_results: list,
    language: str = "hindi",  # "hindi" or "english"
) -> dict:
    """
    Build context from retrieved chunks → send to Groq → return answer.

    Returns:
        {
            "answer": str,
            "sources": list,
            "model_used": str
        }
    """

    # Step 1: Build context from retrieved chunks
    context_parts = []
    sources = []

    for i, result in enumerate(retrieved_results):
        meta = result["metadata"]
        context_parts.append(
            f"[Reference {i+1}]\n"
            f"Crop: {meta.get('crop', 'N/A')}\n"
            f"Region: {meta.get('district', 'N/A')} ({meta.get('agro_zone', 'N/A')} zone)\n"
            f"Farmer Query: {meta.get('original_query', '')}\n"
            f"Expert Answer: {meta.get('original_answer', '')}\n"
        )
        sources.append({
            "crop"    : meta.get("crop"),
            "district": meta.get("district"),
            "zone"    : meta.get("agro_zone"),
            "query"   : meta.get("original_query"),
            "answer"  : meta.get("original_answer"),
            "score"   : result.get("score"),
        })

    context = "\n\n".join(context_parts)

    # Step 2: Build prompt
    if language == "hindi":
        system_prompt = """आप एक कृषि विशेषज्ञ हैं जो भारतीय किसानों की मदद करते हैं।
नीचे दिए गए संदर्भ (KCC विशेषज्ञों के वास्तविक उत्तर) के आधार पर किसान के प्रश्न का उत्तर दें।
- उत्तर हिंदी में दें
- सरल और स्पष्ट भाषा का उपयोग करें
- केवल संदर्भ में दी गई जानकारी का उपयोग करें
- यदि संदर्भ में उत्तर नहीं है तो स्पष्ट रूप से बताएं"""
    else:
        system_prompt = """You are an agricultural expert helping Indian farmers.
Answer the farmer's question based on the context below (real answers from KCC experts).
- Keep the answer simple and clear
- Only use information from the provided context
- If the answer is not in context, say so clearly"""

    user_prompt = f"""Farmer's Question: {query}

Context from KCC Expert Database:
{context}

Please provide a helpful answer based on the above context."""

    # Step 3: Call Groq
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # fast + free
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.3,   # low temp = more factual
        max_tokens=500,
    )

    answer = response.choices[0].message.content

    return {
        "answer"    : answer,
        "sources"   : sources,
        "model_used": "llama3-8b-8192",
    }
