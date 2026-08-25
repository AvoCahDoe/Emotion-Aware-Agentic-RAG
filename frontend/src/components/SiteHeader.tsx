import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="site-header">
      <Link href="/" className="brand-mark">
        Emotion-Aware RAG
      </Link>
      <nav>
        <Link href="/">Ask</Link>
        <Link href="/compare">Compare</Link>
        <Link href="/documentation">Documentation</Link>
      </nav>
    </header>
  );
}
