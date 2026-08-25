"""FastAPI entrypoint for the Emotion-Aware Agentic RAG service."""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import EmotionAwareAgent
from .emotion_detector import create_emotion_detector
from .generator import Generator
from .retriever import Retriever
from .schemas import HealthResponse, QueryRequest, QueryResponse

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "data" / "docs"
EVAL_PATH = BASE_DIR / "eval" / "queries.json"

agent: EmotionAwareAgent | None = None
models_ready = False
startup_error: str | None = None


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global agent, models_ready, startup_error
    try:
        generator = Generator()
        if not generator.ready:
            startup_error = "DEEPSEEK_API_KEY is not set"
            models_ready = False
            agent = None
        else:
            detector = create_emotion_detector(generator)
            retriever = Retriever(DOCS_DIR)
            agent = EmotionAwareAgent(detector, retriever, generator)
            retriever.load()
            detector.load()
            models_ready = True
            startup_error = None
    except Exception as exc:  # noqa: BLE001
        startup_error = str(exc)
        models_ready = False
        agent = None
    yield


app = FastAPI(
    title="Emotion-Aware Agentic RAG",
    description="Affective strategy selection over a small RAG corpus with explainability traces.",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    if models_ready and agent is not None:
        return HealthResponse(status="ok", models_ready=True)
    return HealthResponse(
        status="degraded",
        models_ready=False,
        detail=startup_error or "Models not ready",
    )


@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest) -> QueryResponse:
    if agent is None or not models_ready:
        raise HTTPException(
            status_code=503,
            detail=startup_error or "Service not ready. Check DEEPSEEK_API_KEY.",
        )
    try:
        return agent.run(body.query.strip())
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/eval/sample")
def eval_sample():
    if not EVAL_PATH.exists():
        raise HTTPException(status_code=404, detail="Eval queries not found")
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))
