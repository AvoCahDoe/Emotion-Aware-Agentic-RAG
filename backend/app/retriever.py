"""FAISS-backed document retriever with strategy-aware parameters."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


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
    def __init__(self, docs_dir: Path, model_name: str = EMBED_MODEL) -> None:
        self.docs_dir = docs_dir
        self.model_name = model_name
        self.documents: list[Document] = []
        self._model: Any = None
        self._index: Any = None
        self._embeddings: Any = None

    def load(self) -> None:
        if self._index is not None:
            return
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer

        self.documents = self._load_documents()
        if not self.documents:
            raise RuntimeError(f"No documents found in {self.docs_dir}")
        self._model = SentenceTransformer(self.model_name)
        texts = [f"{d.title}\n{d.text}" for d in self.documents]
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        self._embeddings = np.asarray(embeddings, dtype=np.float32)
        self._index = faiss.IndexFlatIP(self._embeddings.shape[1])
        self._index.add(self._embeddings)

    @property
    def ready(self) -> bool:
        return self._index is not None and self._model is not None

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
                Document(
                    doc_id=path.stem,
                    title=title,
                    text=body,
                    doc_type=doc_type,
                )
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
        assert self._model is not None and self._index is not None

        fetch_k = min(len(self.documents), max(top_k * 3, top_k))
        q = self._model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype("float32")
        scores, indices = self._index.search(q, fetch_k)

        chunks: list[RetrievedChunk] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            doc = self.documents[int(idx)]
            s = float(score)
            if s < min_score:
                continue
            if preferred_types and doc.doc_type in preferred_types:
                s = min(1.0, s + 0.05)
            chunks.append(RetrievedChunk(doc=doc, score=s))

        chunks.sort(key=lambda c: c.score, reverse=True)
        return chunks[:top_k]
