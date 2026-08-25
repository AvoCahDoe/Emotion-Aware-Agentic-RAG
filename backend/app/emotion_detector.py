"""Text emotion classification via a pretrained HuggingFace model."""

from __future__ import annotations

from dataclasses import dataclass


EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"


@dataclass
class EmotionResult:
    label: str
    confidence: float
    scores: dict[str, float]


class EmotionDetector:
    def __init__(self, model_name: str = EMOTION_MODEL) -> None:
        self.model_name = model_name
        self._pipe = None

    def load(self) -> None:
        if self._pipe is None:
            from transformers import pipeline

            self._pipe = pipeline(
                "text-classification",
                model=self.model_name,
                top_k=None,
                truncation=True,
            )

    @property
    def ready(self) -> bool:
        return self._pipe is not None

    def detect(self, text: str) -> EmotionResult:
        self.load()
        assert self._pipe is not None
        raw = self._pipe(text)[0]
        scores = {item["label"]: float(item["score"]) for item in raw}
        best = max(raw, key=lambda item: item["score"])
        return EmotionResult(
            label=best["label"],
            confidence=float(best["score"]),
            scores=scores,
        )
