import { ComparePanel } from "@/components/ComparePanel";

export default function ComparePage() {
  return (
    <main>
      <h1 className="page-title">Compare strategies</h1>
      <p className="page-sub">
        Same factual intent, different emotional framing. Watch the agent switch
        retrieval and generation strategies — and read the rationale for each
        choice.
      </p>
      <section className="panel">
        <ComparePanel />
      </section>
    </main>
  );
}
