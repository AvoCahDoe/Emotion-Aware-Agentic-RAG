"""Text emotion classification — DeepSeek API (default) or local HuggingFace model."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

VALID_LABELS = {"anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"}
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"


@dataclass
class EmotionResult:
    label: str
    confidence: float
    scores: dict[str, float]


def _parse_emotion_json(raw: str) -> EmotionResult:
    text = raw.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    data = json.loads(text)
    label = str(data.get("label", "neutral")).lower()
    if label not in VALID_LABELS:
        label = "neutral"
    confidence = float(data.get("confidence", 0.5))
    confidence = max(0.0, min(1.0, confidence))
    scores = {label: confidence}
    return EmotionResult(label=label, confidence=confidence, scores=scores)


class DeepSeekEmotionDetector:
    """Classify emotion via DeepSeek — low memory, suitable for Render free tier."""

    def __init__(self, generator) -> None:
        self._generator = generator
        self._ready = False

    def load(self) -> None:
        self._generator.load()
        self._ready = True

    @property
    def ready(self) -> bool:
        return self._ready and self._generator.ready

    def detect(self, text: str) -> EmotionResult:
        self.load()
        raw = self._generator.generate(
            system_prompt=(
                "You classify the emotional tone of user messages. "
                "Respond with ONLY valid JSON, no markdown: "
                '{"label":"<anger|disgust|fear|joy|neutral|sadness|surprise>",'
                '"confidence":<number 0-1>}'
            ),
            user_prompt=f"Classify this message:\n{text}",
            max_tokens=60,
            temperature=0.0,
        )
        try:
            return _parse_emotion_json(raw)
        except (json.JSONDecodeError, ValueError, TypeError):
            return EmotionResult(label="neutral", confidence=0.5, scores={"neutral": 0.5})


class LocalEmotionDetector:
    """Optional local HuggingFace classifier for offline development."""

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


def create_emotion_detector(generator):
    mode = os.getenv("EMOTION_BACKEND", "deepseek").lower()
    if mode == "local":
        return LocalEmotionDetector()
    return DeepSeekEmotionDetector(generator)
