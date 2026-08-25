import Link from "next/link";

export default function DocumentationPage() {
  return (
    <main className="docs-page">
      <h1 className="page-title">Documentation</h1>
      <p className="page-sub">
        How emotion-aware agentic RAG works in this demo — from query to
        strategy to answer.
      </p>

      <section className="panel docs-section">
        <h2>What is this?</h2>
        <p>
          <strong>Emotion-Aware Agentic RAG</strong> is a research demo that
          treats the user&apos;s emotional tone as a control signal for
          retrieval and generation. Instead of running the same RAG pipeline for
          every message, an agent detects affect, picks a strategy, retrieves
          documents accordingly, and generates an answer shaped to that state.
        </p>
        <p>
          The goal is to show how{" "}
          <strong>affective computing</strong>, <strong>agentic control</strong>,
          and <strong>explainable AI</strong> can fit together in a small,
          inspectable system — not just as separate ideas, but as one loop you
          can try in the browser.
        </p>
      </section>

      <section className="panel docs-section">
        <h2>Pipeline</h2>
        <ol className="docs-steps">
          <li>
            <strong>Query in</strong> — You send a natural-language question.
            Wording carries emotional tone (frustrated, confused, curious).
          </li>
          <li>
            <strong>Emotion detection</strong> — DeepSeek classifies the
            message into labels such as anger, sadness, joy, or neutral, with a
            confidence score.
          </li>
          <li>
            <strong>Strategy selection</strong> — The agent maps emotion → one
            of three modes: <code>concise</code>, <code>scaffolded</code>, or{" "}
            <code>standard</code>.
          </li>
          <li>
            <strong>Retrieval</strong> — TF-IDF search over a small FAQ corpus
            runs with strategy-specific settings (top-k, score threshold,
            preferred doc types).
          </li>
          <li>
            <strong>Generation</strong> — DeepSeek answers using retrieved
            context and a strategy-specific system prompt. Answers use Markdown
            when helpful (lists, bold, steps).
          </li>
          <li>
            <strong>Explainability</strong> — Every response includes a
            rationale: detected emotion, confidence, chosen strategy, and why.
          </li>
        </ol>
      </section>

      <section className="panel docs-section">
        <h2>Strategies</h2>
        <div className="docs-table-wrap">
          <table className="docs-table">
            <thead>
              <tr>
                <th>Strategy</th>
                <th>Typical emotions</th>
                <th>Retrieval</th>
                <th>Answer shape</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <code>concise</code>
                </td>
                <td>anger, disgust, fear</td>
                <td>Fewer chunks, higher score bar, prefer FAQ</td>
                <td>Short, direct, reassuring</td>
              </tr>
              <tr>
                <td>
                  <code>scaffolded</code>
                </td>
                <td>sadness, low-confidence neutral</td>
                <td>More chunks, prefer how-to docs</td>
                <td>Numbered steps, defines jargon</td>
              </tr>
              <tr>
                <td>
                  <code>standard</code>
                </td>
                <td>joy, surprise, confident neutral</td>
                <td>Balanced top-k across doc types</td>
                <td>Informative mid-length answer</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel docs-section">
        <h2>Why emotion changes the answer</h2>
        <p>
          The same factual question can be asked in different emotional frames.
          A frustrated user often needs a fast, calming path forward; a confused
          user needs structure; a curious user may want a balanced overview.
        </p>
        <p>
          Static RAG ignores that difference. This demo makes the choice
          explicit: open the{" "}
          <Link href="/compare">Compare</Link> page, pick an intent (e.g. upload
          docs), and run frustrated vs confused vs curious variants side by
          side.
        </p>
      </section>

      <section className="panel docs-section">
        <h2>Explainability trace</h2>
        <p>Each response includes metadata like:</p>
        <pre className="docs-code">
{`Detected emotion: anger (0.95 confidence)
-> switched to concise mode: fewer high-confidence chunks,
   shorter reassuring answer.`}
        </pre>
        <p>
          That trace is the explainability layer: you can see what the agent
          inferred and which retrieval/generation policy it applied, without
          digging into logs.
        </p>
      </section>

      <section className="panel docs-section">
        <h2>Stack</h2>
        <ul className="docs-list">
          <li>
            <strong>Frontend</strong> — Next.js on Vercel; Markdown-rendered
            answers
          </li>
          <li>
            <strong>API</strong> — FastAPI on Render
          </li>
          <li>
            <strong>LLM</strong> — DeepSeek (<code>deepseek-chat</code>) for
            emotion classification and answer generation
          </li>
          <li>
            <strong>Retrieval</strong> — TF-IDF over a bundled NovaAssist FAQ
            corpus
          </li>
        </ul>
      </section>

      <section className="panel docs-section">
        <h2>Try it</h2>
        <p>
          Go to <Link href="/">Ask</Link> and try the example buttons
          (Frustrated / Confused / Curious) on the same underlying topic. Watch
          the strategy chip and rationale change, then read the Markdown-formatted
          answer.
        </p>
      </section>
    </main>
  );
}
