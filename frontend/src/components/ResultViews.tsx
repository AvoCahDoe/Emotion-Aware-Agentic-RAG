"use client";

import type { Explainability, QueryResponse } from "@/lib/api";
import { MarkdownContent } from "@/components/MarkdownContent";

const STRATEGY_LABEL: Record<string, string> = {
  concise: "Concise",
  scaffolded: "Scaffolded",
  standard: "Standard",
};

export function EmotionBadge({
  emotion,
  confidence,
}: {
  emotion: string;
  confidence: number;
}) {
  return (
    <span className="meta-pill emotion">
      {emotion}
      <em>{(confidence * 100).toFixed(0)}%</em>
    </span>
  );
}

export function StrategyChip({ strategy }: { strategy: string }) {
  return (
    <span className={`meta-pill strategy strategy-${strategy}`}>
      {STRATEGY_LABEL[strategy] ?? strategy}
    </span>
  );
}

export function ExplainPanel({ explainability }: { explainability: Explainability }) {
  return (
    <aside className="explain-panel" aria-label="Strategy rationale">
      <p className="explain-label">Why this strategy</p>
      <p className="explain-text">{explainability.rationale}</p>
      <div className="meta-row">
        <EmotionBadge
          emotion={explainability.emotion}
          confidence={explainability.confidence}
        />
        <StrategyChip strategy={explainability.strategy} />
      </div>
    </aside>
  );
}

export function ResultCard({ result }: { result: QueryResponse }) {
  return (
    <div className="result-stack">
      <ExplainPanel explainability={result.explainability} />
      <article className="answer-block">
        <h3>Answer</h3>
        <MarkdownContent content={result.answer} />
      </article>
      {result.sources.length > 0 && (
        <section className="sources-block">
          <h3>Retrieved sources</h3>
          <ul>
            {result.sources.map((s) => (
              <li key={`${s.doc_id}-${s.score}`}>
                <div className="source-head">
                  <strong>{s.title}</strong>
                  <span>
                    {s.doc_type} · score {s.score.toFixed(2)}
                  </span>
                </div>
                <MarkdownContent content={s.text} className="source-markdown" />
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
