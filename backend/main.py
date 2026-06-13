from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.query import router as query_router
from db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Krishi-Vani API",
    description="Cross-lingual Agentic RAG for Indian Farmers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "Krishi-Vani backend running 🌾"}