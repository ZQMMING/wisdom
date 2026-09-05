/**
 * 机会/风险/调整 三栏卡
 * SPEC §38 - Opportunity / Risk / Remediation
 */

import type { InsightItem } from '../../types';

const KIND_LABEL: Record<InsightItem['kind'], string> = {
  opportunity: 'OPPORTUNITY',
  risk:        'RISK',
  remedy:      'REMEDY',
};

const KIND_DOT_BG: Record<InsightItem['kind'], string> = {
  opportunity: 'bg-liorin-accent',
  risk:        'bg-[#d4735a]',
  remedy:      'bg-liorin-muted',
};

interface Props {
  items: InsightItem[];
}

export function InsightCard({ items }: Props) {
  return (
    <article className="border border-liorin-border rounded-md p-4 bg-liorin-surface/40">
      <header className="mb-3">
        <span className="font-mono text-[0.65rem] tracking-wide-2 text-liorin-muted">
          INSIGHT
        </span>
      </header>
      <div className="space-y-3">
        {items.map((it, i) => (
          <div key={i} className="flex gap-3">
            <span
              aria-hidden="true"
              className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${KIND_DOT_BG[it.kind]}`}
            />
            <div>
              <div className="font-mono text-[0.6rem] tracking-wide-1 text-liorin-muted">
                {KIND_LABEL[it.kind]}
              </div>
              <div className="text-sm text-liorin-text font-medium mt-0.5">
                {it.title}
              </div>
              <p className="text-sm text-liorin-muted leading-relaxed mt-1">
                {it.detail}
              </p>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}
