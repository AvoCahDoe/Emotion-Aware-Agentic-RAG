"use client";

import { useEffect, useMemo, useState } from "react";
import { ResultCard } from "@/components/ResultViews";
import {
  fetchEvalSample,
  postQuery,
  type EvalQuery,
  type QueryResponse,
} from "@/lib/api";

type Column = {
  framing: string;
  query: string;
  loading: boolean;
  error: string | null;
  result: QueryResponse | null;
};

export function ComparePanel() {
  const [samples, setSamples] = useState<EvalQuery[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [baseId, setBaseId] = useState<string>("upload");
  const [columns, setColumns] = useState<Column[]>([]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchEvalSample()
      .then((data) => {
        setSamples(data);
        const first = data[0]?.base_id ?? "upload";
        setBaseId(first);
      })
      .catch((err) =>
        setLoadError(err instanceof Error ? err.message : "Failed to load eval set"),
      );
  }, []);

  const baseIds = useMemo(
    () => Array.from(new Set(samples.map((s) => s.base_id))),
    [samples],
  );

  const variants = useMemo(
    () => samples.filter((s) => s.base_id === baseId),
    [samples, baseId],
  );

  async function runComparison() {
    setRunning(true);
    const initial: Column[] = variants.map((v) => ({
      framing: v.emotion_framing,
      query: v.query,
      loading: true,
      error: null,
      result: null,
    }));
    setColumns(initial);

    const settled = await Promise.all(
      variants.map(async (v) => {
        try {
          const result = await postQuery(v.query);
          return {
            framing: v.emotion_framing,
            query: v.query,
            loading: false,
            error: null,
            result,
          } satisfies Column;
        } catch (err) {
          return {
            framing: v.emotion_framing,
            query: v.query,
            loading: false,
            error: err instanceof Error ? err.message : "Failed",
            result: null,
          } satisfies Column;
        }
      }),
    );
    setColumns(settled);
    setRunning(false);
  }

  return (
    <div className="compare-panel">
      {loadError && <p className="error-banner">{loadError}</p>}

      <div className="compare-controls">
        <label htmlFor="base">Same factual intent</label>
        <select
          id="base"
          value={baseId}
          onChange={(e) => {
            setBaseId(e.target.value);
            setColumns([]);
          }}
          disabled={!baseIds.length}
        >
          {baseIds.map((id) => (
            <option key={id} value={id}>
              {id}
            </option>
          ))}
        </select>
        <button
          type="button"
          className="primary-btn"
          onClick={runComparison}
          disabled={running || variants.length === 0}
        >
          {running ? "Comparing…" : "Run side-by-side"}
        </button>
      </div>

      <div className="variant-preview">
        {variants.map((v) => (
          <p key={v.id}>
            <strong>{v.emotion_framing}:</strong> {v.query}
          </p>
        ))}
      </div>

      <div className="compare-grid">
        {columns.map((col) => (
          <div key={col.framing} className="compare-col">
            <h3 className="framing-title">{col.framing}</h3>
            {col.loading && <p className="muted">Running…</p>}
            {col.error && <p className="error-banner">{col.error}</p>}
            {col.result && <ResultCard result={col.result} />}
          </div>
        ))}
      </div>
    </div>
  );
}
