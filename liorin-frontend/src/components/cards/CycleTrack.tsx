/**
 * 6-day Cycle Track
 * SPEC §4.1 — Day 1 → 初爻, ..., Day 6 → 上爻
 * SPEC §37 Mobile + §38 Desktop — 始终显示在 Hero 下方
 */

interface Props {
  cycleDay: number;          // 1-6
  totalDays: number;         // 6
}

export function CycleTrack({ cycleDay, totalDays }: Props) {
  const days = Array.from({ length: totalDays }, (_, i) => i + 1);

  return (
    <nav
      className="flex items-center justify-center gap-2 mt-6 mb-2"
      aria-label={`6-day cycle: day ${cycleDay} of ${totalDays}`}
    >
      {days.map((d) => {
        const isPast    = d < cycleDay;
        const isCurrent = d === cycleDay;
        // const isFuture  = d > cycleDay;  // reserved for future use
        return (
          <div
            key={d}
            aria-current={isCurrent ? 'step' : undefined}
            aria-label={`Day ${d}${isCurrent ? ' (current)' : isPast ? ' (past)' : ' (upcoming)'}`}
            className={`w-9 h-9 flex items-center justify-center rounded-full font-mono text-[0.7rem] tracking-wide-1 transition-colors ${
              isCurrent
                ? 'border-2 border-liorin-accent text-liorin-accent bg-liorin-bg-alt'
                : isPast
                ? 'border border-liorin-disabled text-liorin-disabled'
                : 'border border-liorin-border text-liorin-muted'
            }`}
          >
            {String(d).padStart(2, '0')}
          </div>
        );
      })}
    </nav>
  );
}
