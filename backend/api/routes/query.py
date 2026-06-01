# ============================================================
# backend/api/routes/query.py
# Goal: Main FastAPI endpoint — ties everything together
# ============================================================

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../../rag"))

from retriever import retrieve
from synthesizer import synthesize
from intent_extractor import extract_intent

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
