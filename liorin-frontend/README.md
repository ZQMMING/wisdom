# LIORIN Frontend

顺天 LIORIN Personal Today 前端 — React + TypeScript + Tailwind CSS + GSAP

## 技术栈

- React 18.3 + TypeScript 5.6
- Tailwind CSS 3.4（自定义 design tokens）
- GSAP 3.12（动画）
- Vite 5.4

## 快速开始

```bash
npm install
npm run dev       # http://localhost:5173
npm run build
npm run typecheck
```

## 文件结构

```
src/
├── components/
│   ├── hero/            Hero 河洛 → 主卦 → 今日爻
│   │   ├── HetuEmblem.tsx
│   │   ├── HexagramSvg.tsx
│   │   └── HeroTransition.tsx
│   ├── shell/           AppShell + Header
│   │   ├── AppShell.tsx
│   │   └── Header.tsx
│   └── navigation/      BottomNav
│       └── BottomNav.tsx
├── hooks/
│   └── useHeroAnimation.ts    状态机 hook
├── lib/
│   └── tokens.ts              Design tokens
├── pages/
│   └── today/
│       └── PersonalToday.tsx
├── mock/
│   └── data.ts                MOCK ONLY
├── styles/
│   └── tailwind.css
├── types/
│   └── index.ts
├── App.tsx
└── main.tsx
```

## 设计 token

| Token | Value |
|---|---|
| `liorin-black` | `#000000` |
| `liorin-text` | `#e8e2d4` |
| `liorin-muted` | `#8a8279` |
| `liorin-accent` | `#e0b078`（古铜偏金） |
| `liorin-accent-glow` | `rgba(224, 176, 120, 0.28)` |
| `liorin-yang` | `#e8e2d4`（阳爻暖白） |
| `liorin-yang-dim` | `#6a6258`（阴爻暗灰） |

## Hero 动画

三段仪式式视觉转化（共享视觉中心 + 顺序时序）：

| 时间 | 阶段 | 动画 |
|---|---|---|
| 0.0s | hetu | 河洛稳定 1s |
| 1.0s | transition | 河洛旋转淡出 1.8s（`ease-in`） |
| 2.8s | gua | 主卦由小到大淡出 1.8s |
| 4.6s | breathing | 今日爻呼吸（6.6s 周期，"沉 → 聚 → 沉"） |

## 响应式

按 LIORIN_FRONTEND_SPEC_V1 §36-38 验证过的断点：

- iPhone 320×568 (mobile portrait)
- iPhone 375×812 (mobile portrait)
- iPhone 430×932 (mobile large)
- iPhone 812×375 (mobile landscape)
- iPad 768×1024 (tablet)
- Desktop 1024+ / 1440 (desktop)

同一套组件，CSS custom properties + media queries 流式缩放。

## 数据契约

前端禁计算（SPEC §5）。所有 `cycle`、`active_yao`、`yaos`、`guidance` 由后端 canonical state 提供，
前端只 consume → render。

当前使用 `src/mock/data.ts` 作为占位（MOCK ONLY — NOT PRODUCTION）。

## 相关资源

- 视觉参考原型：`liorin-hero/`（单 HTML）
- 前端总规范：`LIORIN_FRONTEND_SPEC_V1.md`
- 设计规范：`frontend/DESIGN_SPEC.md`
