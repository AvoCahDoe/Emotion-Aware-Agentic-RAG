from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


class SourceChunk(BaseModel):
    doc_id: str
    title: str
    text: str
    score: float
    doc_type: str


class Explainability(BaseModel):
    emotion: str
    confidence: float
    strategy: str
    rationale: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    explainability: Explainability


class HealthResponse(BaseModel):
    status: str
    models_ready: bool
    detail: str | None = None
