FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data
COPY eval ./eval

ENV HF_HOME=/app/.cache/huggingface
RUN python - <<'PY'
from transformers import pipeline
from sentence_transformers import SentenceTransformer
pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None,
)
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("Models cached.")
PY

ENV PORT=10000
EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
