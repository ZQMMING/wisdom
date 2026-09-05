/**
 * LIORIN Design Tokens
 * 对应 LIORIN_FRONTEND_SPEC_V1 §33 设计系统基础 + DESIGN_SPEC V2.0
 */

export const tokens = {
  color: {
    bg:          '#000000',
    surface:     '#141210',
    border:      '#2a2622',
    text:        '#e8e2d4',
    textMuted:   '#8a8279',
    yang:        '#e8e2d4',   // 暖白阳爻
    yangDim:     '#6a6258',   // 阴爻断线（暗一档）
    accent:      '#e0b078',   // 古铜偏金（今日爻高亮）
    accentSoft:  '#c9a578',
    accentGlow:  'rgba(224, 176, 120, 0.28)',
  },
  font: {
    display: '"Noto Serif SC", "Source Han Serif", Georgia, serif',
    body:    'Inter, "Noto Sans SC", system-ui, sans-serif',
    mono:    '"JetBrains Mono", "SF Mono", monospace',
  },
  motion: {
    hetuDuration:    1.8,    // s — 河洛离场
    guaDuration:     1.8,    // s — 主卦入场
    breathingCycle:  6.6,    // s — 今日爻呼吸周期
    stagesMs: {
      hetu:        0,
      transition:  1000,
      gua:         3000,
      breathing:   4800,
    },
  },
  size: {
    heroSizeMobile:  240,
    heroSizeTablet:  320,
    heroSizeDesktop: 380,
    touchMin:        44,
  },
} as const;

export type Tokens = typeof tokens;
