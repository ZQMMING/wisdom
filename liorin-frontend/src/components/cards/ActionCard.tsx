/**
 * 今日行动 01/02/03
 * SPEC §38 - Action
 */

import type { ActionItem } from '../../types';

export function ActionCard({ items }: { items: ActionItem[] }) {
  return (
    <article className="border border-liorin-border rounded-md p-4 bg-liorin-surface/40">
      <header className="mb-3 flex items-baseline justify-between">
        <span className="font-mono text-[0.65rem] tracking-wide-2 text-liorin-muted">
          ACTION
        </span>
        <span className="font-mono text-[0.6rem] text-liorin-muted">
          0{items.length}
        </span>
      </header>
      <ol className="space-y-3">
        {items.map((it) => (
          <li key={it.index} className="flex gap-3">
            <span className="font-mono text-xs text-liorin-accent flex-shrink-0 w-6">
              {String(it.index).padStart(2, '0')}
            </span>
            <div>
              <div className="text-sm text-liorin-text font-medium">{it.title}</div>
              <p className="text-sm text-liorin-muted leading-relaxed mt-1">
                {it.detail}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </article>
  );
}
