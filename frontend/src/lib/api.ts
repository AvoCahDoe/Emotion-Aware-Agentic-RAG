export type SourceChunk = {
  doc_id: string;
  title: string;
  text: string;
  score: number;
  doc_type: string;
};

export type Explainability = {
  emotion: string;
  confidence: number;
  strategy: string;
  rationale: string;
};

export type QueryResponse = {
  answer: string;
  sources: SourceChunk[];
  explainability: Explainability;
};

export type EvalQuery = {
  id: string;
  base_id: string;
  emotion_framing: string;
  query: string;
};

export function apiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
    /\/$/,
    "",
  );
}

export async function postQuery(query: string): Promise<QueryResponse> {
  const res = await fetch(`${apiBase()}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function fetchEvalSample(): Promise<EvalQuery[]> {
  const res = await fetch(`${apiBase()}/eval/sample`);
  if (!res.ok) {
    throw new Error(`Failed to load eval sample (${res.status})`);
  }
  return res.json();
}
