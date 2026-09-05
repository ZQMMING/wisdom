/**
 * Hero 入场动画状态机
 *
 *   0.0s   hetu        河洛稳定 1s
 *   1.0s   transition  河洛旋转淡出 1.8s (ease-in)
 *   2.8s   gua         卦由小到大淡出 1.8s
 *   4.6s   breathing   今日爻开始呼吸 (6.6s 周期)
 *
 * 复用 Tailwind keyframes：
 *   - .hero-transition--transition / --gua / --breathing 触发对应动画
 *   - 河洛离场结束后显式写终态兜底，避免 forwards 在选择器断链后失效
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export type HeroStage = 'hetu' | 'transition' | 'gua' | 'breathing';

export interface UseHeroAnimationOptions {
  reducedMotion?: boolean;
}

export function useHeroAnimation({ reducedMotion = false }: UseHeroAnimationOptions = {}) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const [stage, setStage] = useState<HeroStage>('hetu');

  const setStageClass = useCallback((next: HeroStage) => {
    const root = rootRef.current;
    if (!root) return;
    root.classList.remove(
      'hero-transition--hetu',
      'hero-transition--transition',
      'hero-transition--gua',
      'hero-transition--breathing'
    );
    // 强制 reflow，让重播能重新触发动画
    void root.offsetWidth;
    root.classList.add(`hero-transition--${next}`);
    setStage(next);
  }, []);

  const play = useCallback(() => {
    if (reducedMotion) {
      setStageClass('breathing');
      return;
    }
    setStageClass('hetu');
    window.setTimeout(() => setStageClass('transition'), 1000);
    window.setTimeout(() => setStageClass('gua'),       2800);
    window.setTimeout(() => setStageClass('breathing'), 4600);
  }, [reducedMotion, setStageClass]);

  useEffect(() => {
    play();
  }, [play]);

  const replay = useCallback(() => play(), [play]);

  return { rootRef, stage, replay };
}
