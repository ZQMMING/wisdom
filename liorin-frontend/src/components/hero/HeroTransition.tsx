/**
 * Hero Transition — 河洛 → 主卦 → 今日爻呼吸
 *
 * 结构：
 *   .hero-transition        CSS Grid grid-area: 1/1（视觉中心共享）
 *   ├── .hero-transition__hetu  河洛 SVG
 *   └── .hero-transition__gua   主卦 SVG
 *
 * CSS animation 由 .hero-transition--{stage} class 触发
 */

import { useHeroAnimation } from '../../hooks/useHeroAnimation';
import { HetuEmblem } from './HetuEmblem';
import { HexagramSvg } from './HexagramSvg';
import type { Yao } from '../../types';

interface Props {
  yaos: Yao[];
  hexagramName: string;
  reducedMotion?: boolean;
}

export function HeroTransition({ yaos, hexagramName, reducedMotion }: Props) {
  const { rootRef, replay } = useHeroAnimation({ reducedMotion });

  return (
    <div
      ref={rootRef}
      className="hero-transition hero-transition--hetu group"
      onClick={replay}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          replay();
        }
      }}
      aria-label={`点击重播：${hexagramName} 入场动画`}
    >
      <HetuEmblem />
      <div className="hero-transition__gua">
        <HexagramSvg yaos={yaos} ariaLabel={`卦象 ${hexagramName}`} />
      </div>
    </div>
  );
}
