/**
 * Personal Today Page
 * SPEC §3 Authenticated Personal Layer + §37 Mobile / §38 Desktop
 *
 * Mobile:  Header → Hero → Today's Yao → Cycle Track → 河洛 → 易经 → 紫微 → Insight → Action → Evidence
 * Desktop: Header → centered Hero → Today's Yao → Cycle Track → [3-col: 河洛/易经/紫微] → Insight → Action → Evidence
 */

import { useEffect, useState } from 'react';
import { HeroTransition } from '../../components/hero/HeroTransition';
import { BottomNav } from '../../components/navigation/BottomNav';
import { CycleTrack } from '../../components/cards/CycleTrack';
import { HeluoCard } from '../../components/cards/HeluoCard';
import { YijingCard } from '../../components/cards/YijingCard';
import { ZiweiCard } from '../../components/cards/ZiweiCard';
import { InsightCard } from '../../components/cards/InsightCard';
import { ActionCard } from '../../components/cards/ActionCard';
import { EvidenceCard } from '../../components/cards/EvidenceCard';
import { MOCK_PERSONAL_DAY3 } from '../../mock/data';
import type { ViewModel } from '../../types';

export function PersonalToday() {
  const [vm, setVm] = useState<ViewModel | null>(null);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    setVm(MOCK_PERSONAL_DAY3);
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  if (!vm) {
    return (
      <div className="flex-1 flex items-center justify-center text-liorin-muted font-mono text-xs">
        加载中…
      </div>
    );
  }

  const { today } = vm;
  const activeYao = today.active_yao;

  return (
    <>
      <div className="flex-1 flex flex-col items-center px-4 pt-6 pb-12 max-w-3xl mx-auto w-full">
        {/* Meta */}
        <div className="text-center mb-5">
          <span className="block font-mono text-[0.65rem] tracking-wide-2 text-liorin-muted mb-1">
            PERSONAL FLOW
          </span>
          <span className="font-display text-base text-liorin-text tracking-wide-1">
            {today.cycle.hexagram_name} · 第 {today.cycle.cycle_day} 日
          </span>
        </div>

        {/* Hero */}
        <HeroTransition
          yaos={today.yaos}
          hexagramName={today.cycle.hexagram_name}
          reducedMotion={reducedMotion}
        />

        {/* Today's Yao + Cycle Track */}
        <div className="flex flex-col items-center">
          <div className="flex flex-col items-center gap-1 mt-2">
            <span className="font-mono text-xs tracking-wide-1 text-liorin-accent">
              TODAY
            </span>
            <span className="font-display text-2xl text-liorin-text">
              {activeYao.label}
            </span>
            <span className="font-mono text-sm text-liorin-muted">
              {today.cycle.cycle_day} / {today.cycle.total_days}
            </span>
          </div>

          <CycleTrack
            cycleDay={today.cycle.cycle_day}
            totalDays={today.cycle.total_days}
          />
        </div>

        {/* 三体系卡 — mobile 纵向 / desktop 3-col */}
        <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-3 mt-8">
          <HeluoCard panel={today.heluo} />
          <YijingCard panel={today.yijing} />
          <ZiweiCard panel={today.ziwei} />
        </div>

        {/* Insight + Action + Evidence */}
        <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-3 mt-6">
          <InsightCard items={today.insights} />
          <ActionCard items={today.actions} />
        </div>
        <div className="w-full mt-3">
          <EvidenceCard items={today.evidence} />
        </div>
      </div>

      <BottomNav active="today" />
    </>
  );
}
