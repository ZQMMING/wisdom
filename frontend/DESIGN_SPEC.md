# LIORIN 前端設計規範 V2.0

基於 Co-Star 設計語言 + LIORIN 產品規範

## 設計哲學

1. **Co-Star 極簡主義** — 去除所有不必要元素
2. **東方時間智能** — 靜謐、數學感、秩序感
3. **內容優先** — 裝飾性元素最小化

---

## 視覺系統

### 配色方案

```css
/* Primary Colors */
--black: #000000;           /* 純黑背景 */
--dark-gray: #1a1a1a;       /* 深色表面 */
--medium-gray: #5e5e5e;     /* 次要元素 */
--light-gray: #9b9b9b;      /* 邊緣文字 */

/* Text Colors */
--text-primary: #f7f7f7;    /* 主文字 */
--text-secondary: #a0a0a0;  /* 次要文字 */
--text-muted: #666666;      /* 輔助文字 */

/* Accent (謹慎使用) */
--accent: #c4a882;          /* 金色點綴 */
```

### 字體系統

```css
/* Display - Serif */
font-family: 'Noto Serif SC', Georgia, serif;

/* Body - Sans */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Mono - Numbers */
font-family: 'JetBrains Mono', monospace;
```

### 字級規範

```css
--size-xs: 9px;      /* Labels, badges */
--size-sm: 10-11px;  /* Buttons, nav */
--size-md: 12-14px;  /* Body text */
--size-lg: 18-24px;  /* Section titles */
--size-xl: 28-36px;  /* Hero titles */
```

---

## 按鈕設計（Co-Star 風格）

### Bordered Button

```css
.btn-bordered {
  background: none;
  border: 1px solid #555;
  color: #f5f5f5;
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-bordered:hover {
  background: #f5f5f5;
  color: #000;
  border-color: #f5f5f5;
}
```

### Text-Only Button

```css
.btn-text {
  background: none;
  border: none;
  color: #888;
  font-size: 10px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  cursor: pointer;
  padding: 8px 0;
  transition: color 0.15s;
}

.btn-text:hover {
  color: #f5f5f5;
}
```

---

## 頁面結構

### 一級導航（固定）

```
┌─────────────────────────────────────────┐
│ LIORIN                     🌐 中文 ◷ GMT+8 │
├─────────────────────────────────────────┤
│                                         │
│         今日之象 (Hero)                 │
│                                         │
│         ↓ 向下探索                      │
│                                         │
├─────────────────────────────────────────┤
│ State                                   │
│ ─────────────────────────────────────   │
│ Opportunity / Risk / Remediation        │
│ ─────────────────────────────────────   │
│ Action 01/02/03                         │
│ ─────────────────────────────────────   │
│ Evidence                                │
└─────────────────────────────────────────┘
│ Today Guide Insights Me               │
└─────────────────────────────────────────┘
```

### 頁面規則

| 頁面 | 內容 |
|------|------|
| **TODAY** | Hero + 狀態 + 機會/風險/調整 + 行動 + 依據 |
| **GUIDE** | 如何運作 / 理解時間 / 理解自己 / 閱讀洞察 |
| **INSIGHTS** | 周期分析 / 歷史記錄 / 深度洞察 |
| **ME** | 個人資料 / 設定 / 訂閱 |

---

## 禁止元素

❌ 大量金色龍鳳  
❌ 黑底金字  
❌ 道教宮觀風  
❌ 紫色玄學漸變  
❌ 發光八卦  
❌ 複雜祥雲  
❌ 賽博龐克  
❌ 遊戲化粒子  
❌ 滿屏五行彩虹色  

---

## 圓角規範

```css
/* 整體 */
--radius-sm: 0px;      /* 按鈕、卡片 */
--radius-md: 0px;      /* 輸入框 */
--radius-lg: 0px;      /* 大型容器 */

/* Hero/大型視覺可使用 */
--radius-xl: 24px;
```

---

## 動畫規範

### 狀態機（河洛→卦象）

```
IDLE
  ↓
HETU_LUOSHU (1000ms)
  ↓
NUMBER_FLOW (1000ms)
  ↓
NUMBER_CONVERGENCE (900ms)
  ↓
YAO_FORM (900ms)
  ↓
HEXAGRAM_FORM (700ms)
  ↓
HEXAGRAM_HOLD (1000ms)
  ↓
TODAY_REVEAL (500ms)
```

**總時長：約 6 秒**

### Reduced Motion

當 `prefers-reduced-motion: reduce` 時：
- 不播放完整 Morphing
- 直接顯示河洛靜態狀態 → 卦象淡入

---

## 文件位置

| 文件 | 說明 |
|------|------|
| `frontend/liorin-costar.html` | 主 prototype（Co-Star 風格） |
| `frontend/costar-reference.html` | Co-Star UI 參考手冊 |
| `frontend/liorin.html` | 原版設計 |
| `frontend/liorin-light.html` | 淺色版備用 |

---

## 使用方式

```bash
# 直接在瀏覽器打開
open wisdom/frontend/liorin-costar.html

# 或啟動 HTTP 服務器
cd wisdom/frontend
python -m http.server 8080
# 訪問 http://localhost:8080/liorin-costar.html
```

---

## 版本歷史

- **V1.0** - 初始設計，暗黑系 + 中式典雅
- **V2.0** - 融合 Co-Star 設計語言，純黑背景 + 無圓角 + 細線條按鈕
