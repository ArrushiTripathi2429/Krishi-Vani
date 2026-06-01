# ============================================================
# backend/rag/retriever.py
# ============================================================

import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from typing import Optional

# ── Absolute path to vector store ───────────────────────────
# Go up from backend/rag/ → backend/ → krishivani/ → data/vector_store/
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_store")
)

FAISS_PATH    = os.path.join(BASE_DIR, "kcc_index.faiss")
METADATA_PATH = os.path.join(BASE_DIR, "kcc_metadata.pkl")
TEXTS_PATH    = os.path.join(BASE_DIR, "kcc_texts.pkl")

print(f"Looking for FAISS index at: {FAISS_PATH}")

# ── Load once at startup ─────────────────────────────────────
print("Loading embedding model...")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

print("Loading FAISS index...")
index = faiss.read_index(FAISS_PATH)

with open(METADATA_PATH, "rb") as f:
    metadatas = pickle.load(f)

with open(TEXTS_PATH, "rb") as f:
    texts = pickle.load(f)

print(f"FAISS index loaded: {index.ntotal:,} vectors")


# ── Core retrieval function ──────────────────────────────────
def retrieve(
    query: str,
    agro_zone: Optional[str] = None,
    crop: Optional[str] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.60,
) -> dict:

    # Step 1: Embed query
    query_vector = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_vector)

    # Step 2: Search top candidates
    fetch_k = top_k * 10
    scores, indices = index.search(query_vector, k=fetch_k)

    # Step 3: Collect results
    raw_results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        raw_results.append({
            "score"   : float(score),
            "text"    : texts[idx],
            "metadata": metadatas[idx],
        })

    # Step 4: Apply metadata filters
    filtered = raw_results

    if agro_zone:
        zone_filtered = [
            r for r in filtered
            if r["metadata"].get("agro_zone") == agro_zone
        ]
        if len(zone_filtered) >= 2:
            filtered = zone_filtered

    if crop and crop.lower() != "others":
        crop_filtered = [
            r for r in filtered
            if crop.lower() in r["metadata"].get("crop", "").lower()
        ]
        if len(crop_filtered) >= 2:
            filtered = crop_filtered

    filtered   = filtered[:top_k]
    best_score = filtered[0]["score"] if filtered else 0.0
    fallback_triggered = best_score < similarity_threshold

    return {
        "results"           : filtered,
        "fallback_triggered": fallback_triggered,
        "best_score"        : best_score,
    }


# ── Zone mapper ──────────────────────────────────────────────
DISTRICT_TO_ZONE = {
    "LAKHIMPUR KHERI": "tarai", "BAHRAICH": "tarai", "SHRAVASTI": "tarai",
    "BALRAMPUR": "tarai", "SIDDHARTHNAGAR": "tarai", "MAHARAJGANJ": "tarai",
    "GORAKHPUR": "tarai", "KUSHINAGAR": "tarai", "DEORIA": "tarai",
    "LUCKNOW": "central_plain", "UNNAO": "central_plain", "RAE BARELI": "central_plain",
    "FATEHPUR": "central_plain", "KANPUR NAGAR": "central_plain",
    "KANPUR DEHAT": "central_plain", "HARDOI": "central_plain",
    "SITAPUR": "central_plain", "BARABANKI": "central_plain",
    "VARANASI": "eastern_plain", "JAUNPUR": "eastern_plain", "AZAMGARH": "eastern_plain",
    "GHAZIPUR": "eastern_plain", "BALLIA": "eastern_plain", "BASTI": "eastern_plain",
    "AMBEDKAR NAGAR": "eastern_plain", "SULTANPUR": "eastern_plain",
    "AGRA": "western_plain", "MATHURA": "western_plain", "ETAH": "western_plain",
    "MAINPURI": "western_plain", "FIROZABAD": "western_plain",
    "ALIGARH": "western_plain", "BULANDSHAHR": "western_plain",
    "JHANSI": "bundelkhand", "LALITPUR": "bundelkhand", "JALAUN": "bundelkhand",
    "HAMIRPUR": "bundelkhand", "MAHOBA": "bundelkhand", "BANDA": "bundelkhand",
    "MIRZAPUR": "vindhyan", "SONBHADRA": "vindhyan", "ALLAHABAD": "vindhyan",
}

def get_zone_from_district(district: str) -> str:
    if not district:
        return "central_plain"
    return DISTRICT_TO_ZONE.get(district.upper().strip(), "central_plain")
