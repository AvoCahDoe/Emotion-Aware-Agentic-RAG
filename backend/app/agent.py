"""Emotion-aware strategy selection and RAG orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from .emotion_detector import EmotionDetector, EmotionResult
from .generator import Generator
from .retriever import RetrievedChunk, Retriever
from .schemas import Explainability, QueryResponse, SourceChunk


# Frustration-like labels from the Hartmann emotion model
CONCISE_EMOTIONS = {"anger", "disgust", "fear"}
# Confusion / distress → scaffolded explanations
SCAFFOLDED_EMOTIONS = {"sadness"}
# Everything else → standard RAG
STANDARD_EMOTIONS = {"joy", "neutral", "surprise"}


@dataclass
class StrategyConfig:
    name: str
    top_k: int
    min_score: float
    preferred_types: set[str]
    max_tokens: int
    temperature: float
    system_prompt: str
    description: str


STRATEGIES: dict[str, StrategyConfig] = {
    "concise": StrategyConfig(
        name="concise",
        top_k=2,
        min_score=0.25,
        preferred_types={"faq"},
        max_tokens=220,
        temperature=0.3,
        system_prompt=(
            "You are a calm, reassuring support assistant. The user seems frustrated. "
            "Answer in 2–4 short sentences. Be direct, empathetic, and concrete. "
            "Do not overwhelm with steps. Use only the provided context. "
            "If the context is insufficient, say what you know and suggest one next action."
        ),
        description="fewer high-confidence chunks, shorter reassuring answer",
    ),
    "scaffolded": StrategyConfig(
        name="scaffolded",
        top_k=4,
        min_score=0.15,
        preferred_types={"howto"},
        max_tokens=700,
        temperature=0.4,
        system_prompt=(
            "You are a patient tutor. The user seems confused or overwhelmed. "
            "Answer with a clear numbered step-by-step explanation. "
            "Define jargon briefly. Use only the provided context. "
            "End with a one-sentence check-in asking if a step needs clarifying."
        ),
        description="more explanatory chunks, longer step-by-step answer",
    ),
    "standard": StrategyConfig(
        name="standard",
        top_k=3,
        min_score=0.2,
        preferred_types={"faq", "howto", "overview"},
        max_tokens=450,
        temperature=0.4,
        system_prompt=(
            "You are a helpful documentation assistant. "
            "Answer clearly and accurately using only the provided context. "
            "Keep a balanced length: informative but not verbose."
        ),
        description="standard retrieval and answer length",
    ),
}


def select_strategy(emotion: EmotionResult) -> StrategyConfig:
    """Map detected emotion (+ confidence) to a retrieval/generation strategy."""
    label = emotion.label.lower()
    if label in CONCISE_EMOTIONS:
        return STRATEGIES["concise"]
    if label in SCAFFOLDED_EMOTIONS:
        return STRATEGIES["scaffolded"]
    # Low-confidence predictions often indicate mixed/confused affect → scaffold
    if emotion.confidence < 0.45 and label in STANDARD_EMOTIONS:
        return STRATEGIES["scaffolded"]
    return STRATEGIES["standard"]


def build_rationale(emotion: EmotionResult, strategy: StrategyConfig) -> str:
    return (
        f"Detected emotion: {emotion.label} ({emotion.confidence:.2f} confidence) "
        f"-> switched to {strategy.name} mode: {strategy.description}."
    )


class EmotionAwareAgent:
    def __init__(
        self,
        emotion_detector: EmotionDetector,
        retriever: Retriever,
        generator: Generator,
    ) -> None:
        self.emotion_detector = emotion_detector
        self.retriever = retriever
        self.generator = generator

    def load(self) -> None:
        self.emotion_detector.load()
        self.retriever.load()
        # Generator only needs the API key present; no heavy model download
        if not self.generator.ready:
            raise RuntimeError("DEEPSEEK_API_KEY is required")

    @property
    def ready(self) -> bool:
        return (
            self.emotion_detector.ready
            and self.retriever.ready
            and self.generator.ready
        )

    def run(self, query: str) -> QueryResponse:
        emotion = self.emotion_detector.detect(query)
        strategy = select_strategy(emotion)
        chunks = self.retriever.retrieve(
            query,
            top_k=strategy.top_k,
            min_score=strategy.min_score,
            preferred_types=strategy.preferred_types,
        )
        context = self._format_context(chunks)
        user_prompt = (
            f"User question:\n{query}\n\n"
            f"Retrieved context:\n{context}\n\n"
            "Answer the user question using the context above."
        )
        answer = self.generator.generate(
            system_prompt=strategy.system_prompt,
            user_prompt=user_prompt,
            max_tokens=strategy.max_tokens,
            temperature=strategy.temperature,
        )
        return QueryResponse(
            answer=answer,
            sources=[
                SourceChunk(
                    doc_id=c.doc.doc_id,
                    title=c.doc.title,
                    text=c.doc.text,
                    score=round(c.score, 4),
                    doc_type=c.doc.doc_type,
                )
                for c in chunks
            ],
            explainability=Explainability(
                emotion=emotion.label,
                confidence=round(emotion.confidence, 4),
                strategy=strategy.name,
                rationale=build_rationale(emotion, strategy),
            ),
        )

    @staticmethod
    def _format_context(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "(No relevant documents retrieved.)"
        parts = []
        for i, chunk in enumerate(chunks, start=1):
            parts.append(
                f"[{i}] ({chunk.doc.doc_type}) {chunk.doc.title}\n{chunk.doc.text}"
            )
        return "\n\n".join(parts)
