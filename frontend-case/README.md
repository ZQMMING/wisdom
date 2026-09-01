# LIORIN Frontend Case

独立 UI Case 规范 — 符合《LIORIN 前端工程总规范 V1.0》

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:5173

右下角有状态切换按钮用于测试不同场景。

---

## Architecture

```
liorin-frontend-case/
├── src/
│   ├── animation/         # Hero state machine, breathing yao
│   ├── components/
│   │   ├── cards/         # Heluo, Yijing, Ziwei cards
│   │   ├── feedback/      # Profile gate, errors, loading
│   │   ├── hexagram/      # Hexagram renderer, flow, six-day cycle
│   │   ├── navigation/    # Bottom nav
│   │   ├── premium/       # Premium gate
│   │   ├── shell/         # Header + app layout
│   │   └── yao/           # Today's yao card
│   ├── design-system/     # Token definitions
│   ├── domain/            # Entitlement service
│   ├── mock/              # MOCK ONLY data — no calculations
│   ├── pages/             # Today, Guide, Insights, Me
│   ├── view-models/       # API → UI transformation
│   └── App.tsx
├── index.html
├── vite.config.ts
└── tsconfig.json
```

---

## Design Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `#10100E` | Page background |
| `--text-primary` | `#F1EDE3` | Main text |
| `--text-secondary` | `#9B988F` | Secondary text |
| `--text-muted` | `#5C5A54` | Labels, disabled |
| `--accent` | `#A34A3A` | Active yao, CTAs (cinnabar) |
| `--font-display` | Noto Serif SC | Headings, classical text |
| `--font-body` | Inter | Body text |
| `--font-mono` | JetBrains Mono | Dates, cycle days |

---

## Golden UI Cases

| Case | State | Description |
|------|-------|-------------|
| 01 | Public TODAY | Guest sees public hexagram + guidance |
| 02 | Personal DAY 1 | First day of six-day cycle |
| 03 | Personal DAY 3 | Active yao = 三爻 |
| 04 | Personal DAY 6 | Last day of cycle |
| 05 | New Cycle | Day 7 → new hexagram starts |
| 06 | Premium Gate | Authenticated but not premium |
| 07 | Private TODAY | Premium + valid profile |
| 08 | Calculation Error | Profile valid but data unavailable |
| 09 | Reduced Motion | prefers-reduced-motion enabled |
| 10 | Mobile | 375px viewport |

---

## Red Lines (spec section 56)

- ❌ No frontend calculation of active_yao, cycle_day, or hexagram
- ❌ No Personal → Public fallback
- ❌ No Legacy adapter or field guessing
- ❌ No LLM doing computation
- ❌ No gold/dragon/phoenix visual clichés
- ❌ No neon effects or game-like particles

---

## Dev Notes

The bottom-right corner has a state switcher for testing all golden cases:
- Public
- No Profile
- Incomplete
- Valid
- Premium
- Error

To switch language/timezone, use the header controls.
