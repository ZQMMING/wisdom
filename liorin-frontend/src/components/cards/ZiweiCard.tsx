import type { ZiweiPanel } from '../../types';
import { PanelCard } from './PanelCard';

export function ZiweiCard({ panel }: { panel: ZiweiPanel }) {
  return (
    <PanelCard
      label="紫微"
      summary={panel.summary}
      detail={
        <div className="grid grid-cols-2 gap-y-1 gap-x-3 text-xs">
          <div className="flex justify-between border-b border-liorin-border/50 py-1">
            <span className="font-mono text-liorin-muted tracking-wide-1">主星</span>
            <span className="text-liorin-text font-mono">{panel.main_star}</span>
          </div>
          <div className="flex justify-between border-b border-liorin-border/50 py-1">
            <span className="font-mono text-liorin-muted tracking-wide-1">宫位</span>
            <span className="text-liorin-text font-mono">{panel.palace}</span>
          </div>
        </div>
      }
    />
  );
}
