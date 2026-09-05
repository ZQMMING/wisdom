import type { YijingPanel } from '../../types';
import { PanelCard } from './PanelCard';

export function YijingCard({ panel }: { panel: YijingPanel }) {
  return (
    <PanelCard
      label="易经"
      summary={panel.summary}
      detail={
        <div className="space-y-2">
          <p className="font-display text-liorin-text leading-relaxed border-l-2 border-liorin-accent pl-3">
            {panel.hexagram_text}
          </p>
          <p className="text-liorin-muted leading-relaxed">
            {panel.line_text}
          </p>
        </div>
      }
    />
  );
}
