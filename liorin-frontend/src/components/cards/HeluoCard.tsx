import type { HeluoPanel } from '../../types';
import { PanelCard } from './PanelCard';

export function HeluoCard({ panel }: { panel: HeluoPanel }) {
  return (
    <PanelCard
      label="河洛"
      summary={panel.summary}
      detail={
        <div className="space-y-3">
          {/* 数字组合 */}
          <div className="flex items-center gap-2">
            {panel.numbers.map((n) => (
              <span
                key={n}
                className="w-9 h-9 flex items-center justify-center rounded-full border border-liorin-accent/40 text-liorin-accent font-mono text-sm"
                aria-label={`数字 ${n}`}
              >
                {n}
              </span>
            ))}
          </div>
          {/* 字段表 */}
          <dl className="grid grid-cols-2 gap-y-1 gap-x-3 text-xs">
            {panel.fields.map((f) => (
              <div key={f.label} className="flex justify-between border-b border-liorin-border/50 py-1">
                <dt className="font-mono text-liorin-muted tracking-wide-1">{f.label}</dt>
                <dd className="text-liorin-text font-mono">{f.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      }
    />
  );
}
