"""Lightweight TF-IDF retriever — no torch/FAISS, fits Render free tier."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    doc_type: str  # faq | howto | overview


@dataclass
class RetrievedChunk:
    doc: Document
    score: float


class Retriever:
    def __init__(self, docs_dir: Path) -> None:
        self.docs_dir = docs_dir
        self.documents: list[Document] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None

    def load(self) -> None:
        if self._matrix is not None:
            return
        self.documents = self._load_documents()
        if not self.documents:
            raise RuntimeError(f"No documents found in {self.docs_dir}")
        corpus = [f"{d.title}\n{d.text}" for d in self.documents]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(corpus)

    @property
    def ready(self) -> bool:
        return self._matrix is not None and self._vectorizer is not None

    def _load_documents(self) -> list[Document]:
        docs: list[Document] = []
        for path in sorted(self.docs_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8").strip()
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else path.stem
            type_match = re.search(r"^type:\s*(\w+)", content, re.MULTILINE | re.IGNORECASE)
            doc_type = type_match.group(1).lower() if type_match else "faq"
            body = re.sub(r"^type:\s*\w+\s*\n?", "", content, count=1, flags=re.IGNORECASE)
            body = re.sub(r"^#\s+.+\n?", "", body, count=1).strip()
            docs.append(
                Document(doc_id=path.stem, title=title, text=body, doc_type=doc_type)
            )
        return docs

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 3,
        min_score: float = 0.0,
        preferred_types: set[str] | None = None,
    ) -> list[RetrievedChunk]:
        self.load()
        assert self._vectorizer is not None and self._matrix is not None

        q_vec = self._vectorizer.transform([query])
        scores = (self._matrix @ q_vec.T).toarray().ravel()

        chunks: list[RetrievedChunk] = []
        for idx, score in enumerate(scores):
            s = float(score)
            if s < min_score:
                continue
            doc = self.documents[idx]
            if preferred_types and doc.doc_type in preferred_types:
                s = min(1.0, s + 0.05)
            chunks.append(RetrievedChunk(doc=doc, score=s))

        chunks.sort(key=lambda c: c.score, reverse=True)
        return chunks[:top_k]
