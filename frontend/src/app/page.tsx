import { ChatPanel } from "@/components/ChatPanel";

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <h1>Emotion-Aware RAG</h1>
        <p className="lede">
          An agent that detects how you feel from text, then chooses how to
          retrieve and answer — concise when frustrated, scaffolded when
          confused, standard when curious.
        </p>
        <p className="motivation">
          A research demo at the intersection of affective computing, agentic
          RAG, and explainable AI.
        </p>
      </section>

      <section className="panel">
        <ChatPanel />
      </section>
    </main>
  );
}
