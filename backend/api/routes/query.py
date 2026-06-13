# ============================================================
# backend/api/routes/query.py
# Goal: Main FastAPI endpoint — ties everything together
# ============================================================


from fastapi import APIRouter, UploadFile, File  # sirf yeh ek line
from pydantic import BaseModel
from typing import Optional
import sys
import os
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "../../rag"))
from transcribe import transcribe_audio
from retriever import retrieve
from synthesizer import synthesize
from intent_extractor import extract_intent
from db import create_thread, save_message, get_thread_messages, get_all_threads, delete_thread, update_thread_title
import uuid
router = APIRouter()


# ── Request / Response models ────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    district: Optional[str] = None   # optional — user can provide
    language: Optional[str] = "hindi"


class SourceItem(BaseModel):
    crop: Optional[str]
    district: Optional[str]
    zone: Optional[str]
    query: Optional[str]
    answer: Optional[str]
    score: Optional[float]


class QueryResponse(BaseModel):
    answer: str
    sources: list
    agro_zone: Optional[str]
    crop_detected: Optional[str]
    fallback_triggered: bool
    best_score: float


# ── Main query endpoint ──────────────────────────────────────
@router.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """
    Full RAG pipeline:
    1. Extract intent (crop, district, zone) from query
    2. Retrieve top-k chunks from FAISS with metadata filter
    3. If low similarity → fallback (broader search)
    4. Synthesize answer via Groq
    5. Return answer + sources
    """

    # Step 1: Extract intent
    intent = extract_intent(request.query)

    crop      = intent.get("crop")
    agro_zone = intent.get("agro_zone")
    translated_query = intent.get("translated_query", request.query)

    # Override zone if user provided district directly
    if request.district:
        from retriever import get_zone_from_district
        agro_zone = get_zone_from_district(request.district)

    # Step 2: Retrieve from FAISS
    retrieval = retrieve(
        query     = translated_query,
        agro_zone = agro_zone,
        crop      = crop,
        top_k     = 5,
    )

    results           = retrieval["results"]
    fallback_triggered = retrieval["fallback_triggered"]
    best_score        = retrieval["best_score"]

    # Step 3: If fallback triggered → retry without zone filter
    if fallback_triggered:
        retrieval = retrieve(
            query     = translated_query,
            agro_zone = None,   # remove zone filter
            crop      = crop,
            top_k     = 5,
        )
        results    = retrieval["results"]
        best_score = retrieval["best_score"]

    # Step 4: Synthesize answer
    synthesis = synthesize(
        query             = request.query,
        retrieved_results = results,
        language          = request.language or "hindi",
    )

    # Step 5: Return response
    return QueryResponse(
        answer            = synthesis["answer"],
        sources           = synthesis["sources"],
        agro_zone         = agro_zone,
        crop_detected     = crop,
        fallback_triggered = fallback_triggered,
        best_score        = best_score,
    )

    # ── Voice endpoint — add at bottom of query.py ──────────────
@router.post("/voice-query", response_model=QueryResponse)
async def handle_voice_query(
    audio: UploadFile = File(...),
    district: Optional[str] = None,
    language: str = "hindi",
):
    """
    Voice RAG pipeline:
    1. Save uploaded audio to temp file
    2. Groq Whisper → text
    3. Pass text to existing RAG pipeline
    """

    # Step 1: Save audio to temp file
    suffix = os.path.splitext(audio.filename)[-1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await audio.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Step 2: Transcribe
        whisper_lang = "hi" if language == "hindi" else "en"
        transcription = transcribe_audio(tmp_path, language=whisper_lang)

        if not transcription["success"]:
            return QueryResponse(
                answer="आवाज़ सुनने में दिक्कत हुई। कृपया दोबारा बोलें।",
                sources=[],
                agro_zone=None,
                crop_detected=None,
                fallback_triggered=False,
                best_score=0.0,
            )

        transcribed_text = transcription["text"]

        # Step 3: Reuse existing RAG pipeline
        fake_request = QueryRequest(
            query=transcribed_text,
            district=district,
            language=language,
        )
        return await handle_query(fake_request)

    finally:
        os.unlink(tmp_path)  # cleanup temp file


        # ── Chat models ──────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    language: Optional[str] = "english"

class ChatResponse(BaseModel):
    answer: str
    is_farming: bool
    sources: list = []

@router.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    farming_keywords = [
        "crop", "plant", "soil", "fertilizer", "pest", "disease", "harvest",
        "seed", "irrigation", "wheat", "paddy", "sugarcane", "potato", "mango",
        "fasal", "khet", "beej", "khad", "keede", "paani", "gehu", "dhan",
        "yellow", "leaves", "fungus", "spray", "insects", "blight", "rot"
    ]
    is_farming = any(kw in request.message.lower() for kw in farming_keywords)

    if is_farming:
        intent = extract_intent(request.message)
        crop = intent.get("crop")
        agro_zone = intent.get("agro_zone")
        translated_query = intent.get("translated_query", request.message)

        retrieval = retrieve(query=translated_query, agro_zone=agro_zone, crop=crop, top_k=5)
        results = retrieval["results"]

        if retrieval["fallback_triggered"]:
            retrieval = retrieve(query=translated_query, agro_zone=None, crop=crop, top_k=5)
            results = retrieval["results"]

        synthesis = synthesize(
            query=request.message,
            retrieved_results=results,
            language=request.language or "english",
        )
        return ChatResponse(answer=synthesis["answer"], is_farming=True, sources=synthesis["sources"])

    else:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        messages = [{"role": "system", "content": "You are KrishiVani, a friendly AI assistant for Indian farmers. Answer general questions naturally and concisely."}]
        for msg in request.history[-6:]:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": request.message})

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=400,
        )
        return ChatResponse(answer=response.choices[0].message.content, is_farming=False, sources=[])


# ── Thread models ─────────────────────────────────────────────
class ThreadChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None  # None = new thread
    language: Optional[str] = "english"

class ThreadChatResponse(BaseModel):
    answer: str
    is_farming: bool
    sources: list = []
    thread_id: str

# ── Thread chat endpoint ──────────────────────────────────────
@router.post("/thread-chat", response_model=ThreadChatResponse)
async def handle_thread_chat(request: ThreadChatRequest):
    # Create new thread if not provided
    thread_id = request.thread_id or str(uuid.uuid4())
    await create_thread(thread_id)

    # Get history from DB
    history = await get_thread_messages(thread_id)

    # Save user message
    await save_message(thread_id, "user", request.message)

    # Reuse /chat logic
    chat_req = ChatRequest(
        message=request.message,
        history=[ChatMessage(role=m["role"], content=m["content"]) for m in history],
        language=request.language,
    )
    response = await handle_chat(chat_req)

    # Save assistant message
    await save_message(thread_id, "assistant", response.answer, response.is_farming, response.sources)

    # Auto-title thread from first message
    if len(history) == 0:
        title = request.message[:40] + "..." if len(request.message) > 40 else request.message
        await update_thread_title(thread_id, title)

    return ThreadChatResponse(
        answer=response.answer,
        is_farming=response.is_farming,
        sources=response.sources,
        thread_id=thread_id,
    )

# ── Get all threads ───────────────────────────────────────────
@router.get("/threads")
async def get_threads():
    return await get_all_threads()

# ── Get thread messages ───────────────────────────────────────
@router.get("/threads/{thread_id}/messages")
async def get_messages(thread_id: str):
    return await get_thread_messages(thread_id)

# ── Delete thread ─────────────────────────────────────────────
@router.delete("/threads/{thread_id}")
async def remove_thread(thread_id: str):
    await delete_thread(thread_id)
    return {"status": "deleted"}

