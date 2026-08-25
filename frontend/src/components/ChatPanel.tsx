"use client";

import { FormEvent, useState } from "react";
import { ResultCard } from "@/components/ResultViews";
import { postQuery, type QueryResponse } from "@/lib/api";

const EXAMPLES = [
  "This is ridiculous — I uploaded my docs an hour ago and still get nothing useful. How do I actually get my documentation into NovaAssist?!",
  "I'm a bit lost... I think I need to upload documentation but I don't understand the steps or what Indexed means. Can you walk me through it slowly?",
  "Curious how document upload and indexing works in NovaAssist — what's the recommended flow?",
];

export function ChatPanel() {
  const [query, setQuery] = useState(EXAMPLES[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResponse | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await postQuery(query.trim());
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-panel">
      <form onSubmit={onSubmit} className="ask-form">
        <label htmlFor="query">Your question</label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          required
          placeholder="Ask with emotional tone — frustration, confusion, curiosity…"
        />
        <div className="example-row">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              className="ghost-btn"
              onClick={() => setQuery(ex)}
            >
              {i === 0 ? "Frustrated" : i === 1 ? "Confused" : "Curious"}
            </button>
          ))}
        </div>
        <button type="submit" className="primary-btn" disabled={loading || !query.trim()}>
          {loading ? "Running agent…" : "Ask with emotion awareness"}
        </button>
      </form>

      {error && <p className="error-banner">{error}</p>}
      {result && <ResultCard result={result} />}
    </div>
  );
}
