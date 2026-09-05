/**
 * 原典证据
 * SPEC §38 - Evidence
 */

import type { EvidenceItem } from '../../types';

export function EvidenceCard({ items }: { items: EvidenceItem[] }) {
  return (
    <article className="border border-liorin-border rounded-md p-4 bg-liorin-surface/40">
      <header className="mb-3">
        <span className="font-mono text-[0.65rem] tracking-wide-2 text-liorin-muted">
          EVIDENCE
        </span>
      </header>
      <ul className="space-y-3">
        {items.map((it, i) => (
          <li key={i} className="border-l-2 border-liorin-border pl-3">
            <div className="font-mono text-[0.6rem] tracking-wide-1 text-liorin-muted mb-1">
              {it.source}
            </div>
            <blockquote className="font-display text-sm text-liorin-text leading-relaxed">
              {it.excerpt}
            </blockquote>
          </li>
        ))}
      </ul>
    </article>
  );
}
