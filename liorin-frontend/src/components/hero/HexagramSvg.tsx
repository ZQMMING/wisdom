/**
 * 卦象渲染：6 爻，今日动爻用古铜金 + 光晕
 * 阳爻：暖白实线  / 阴爻：暗灰断线
 */

import type { Yao } from '../../types';

interface Props {
  yaos: Yao[];
  ariaLabel?: string;
}

const VB_W = 120;
const VB_H = 168;
const LINE_H = 10;
const GAP = 8;
const X = 10;
const WIDTH = 100;
const GAP_W = 16;

export function HexagramSvg({ yaos, ariaLabel }: Props) {
  const totalH = yaos.length * (LINE_H + GAP) - GAP;
  const startY = (VB_H - totalH) / 2;

  return (
    <svg viewBox={`0 0 ${VB_W} ${VB_H}`} role="img" aria-label={ariaLabel ?? '卦象'}>
      {yaos.map((yao, i) => {
        const yPos = startY + i * (LINE_H + GAP);
        const isActive = yao.active === true;
        const todayAttrs = isActive ? { 'aria-label': '今日动爻' } : {};

        if (yao.type === 'yang') {
          return (
            <rect
              key={i}
              className={isActive ? 'gua-rect gua-rect--active today-yao' : 'gua-rect'}
              x={X}
              y={yPos}
              width={WIDTH}
              height={LINE_H}
              rx={1}
              {...todayAttrs}
            />
          );
        }

        const segW = (WIDTH - GAP_W) / 2;
        const leftCls  = isActive ? 'gua-rect gua-rect--active gua-rect--yin today-yao' : 'gua-rect gua-rect--yin';
        const rightCls = isActive ? 'gua-rect gua-rect--active gua-rect--yin' : 'gua-rect gua-rect--yin';
        return (
          <g key={i}>
            <rect
              className={leftCls}
              x={X}
              y={yPos}
              width={segW}
              height={LINE_H}
              rx={1}
              {...todayAttrs}
            />
            <rect
              className={rightCls}
              x={X + segW + GAP_W}
              y={yPos}
              width={segW}
              height={LINE_H}
              rx={1}
            />
          </g>
        );
      })}
    </svg>
  );
}
