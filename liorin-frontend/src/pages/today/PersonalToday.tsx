/**
 * Personal Today Page
 * SPEC §3 Authenticated Personal Layer
 *
 *   Hero · Today's Yao · Heluo · Yijing · Ziwei · 6-day cycle
 */

import { useEffect, useState } from 'react';
import { HeroTransition } from '../../components/hero/HeroTransition';
import { BottomNav } from '../../components/navigation/BottomNav';
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
      <div className="flex-1 flex flex-col items-center px-4 pt-6 pb-12 max-w-2xl mx-auto w-full">
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

        {/* Today's Yao */}
        <div className="flex flex-col items-center gap-1 mt-6">
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

        {/* 经典 / 现代 / 行动 — 给后续 cards 留位 */}
        <div className="mt-10 w-full max-w-md space-y-6">
          <div className="border border-liorin-border rounded-md p-4">
            <p className="font-display text-liorin-text leading-relaxed border-l-2 border-liorin-accent pl-3">
              {today.guidance.classical}
            </p>
            <p className="mt-3 text-sm text-liorin-muted leading-relaxed">
              {today.guidance.modern}
            </p>
            <p className="mt-3 text-sm bg-liorin-surface rounded p-3 text-liorin-text">
              <strong className="block font-mono text-[0.65rem] tracking-wide-1 text-liorin-muted mb-1">
                今日行动
              </strong>
              {today.guidance.action}
            </p>
          </div>
        </div>
      </div>

      <BottomNav active="today" />
    </>
  );
}
