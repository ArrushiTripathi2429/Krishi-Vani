# ============================================================
# backend/main.py
# Goal: FastAPI app entry point
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.query import router as query_router

app = FastAPI(
    title="Krishi-Vani API",
    description="Cross-lingual Agentic RAG for Indian Farmers",
    version="1.0.0",
)

# ── CORS — allow Next.js frontend ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────
app.include_router(query_router, prefix="/api")


@app.get("/")
def health_check():
    return {"status": "Krishi-Vani backend running 🌾"}
