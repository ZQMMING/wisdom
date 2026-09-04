# LIORIN · Hero Transition · 独立原型

顺天 LIORIN 的 Hero 区入场动画独立原型，专注三段仪式式视觉转化：

```
河洛旋转淡化消失 → 卦由小到大淡出 → 今日爻呼吸
```

## 特性

- **零依赖**：单 HTML 文件，内联 CSS / 内联 SVG / 内联 JS，浏览器直接打开即可
- **无构建**：不依赖 npm / vite / webpack，纯静态资源
- **响应式**：自适应视口宽度
- **无障碍**：尊重 prefers-reduced-motion，ARIA 标注

## 打开方式

### 方式 1：浏览器直接打开

```bash
# Windows
start index.html

# macOS
open index.html

# Linux
xdg-open index.html
```

> 注意：直接打开 file:// 协议下大多数浏览器可正常工作；若安全策略更严格，推荐方式 2。

### 方式 2：本地 HTTP 服务

```bash
# Python 3
python -m http.server 8080

# Node.js
npx http-server -p 8080
```

然后访问 http://localhost:8080/

## 视觉规范

- 背景：`#000000` 纯黑
- 文字：`#e8e2d4` 暖白
- 古铜金：`#e0b078`（今日爻高亮 + 光晕）
- 阳爻：暖白实线
- 阴爻：`#6a6258` 暗灰断线

## 动画时序

| 时间 | 阶段 | 状态 |
|------|------|------|
| 0.0s | `hetu` | 河洛稳定 1s |
| 1.0s | `transition` | 河洛旋转淡出 1.8s（`ease-in`） |
| 3.0s | `gua` | 卦由小到大淡出 1.8s（`cubic-bezier(.45,0,.25,1)`） |
| 4.8s | `breathing` | 今日爻开始呼吸（6.6s 周期，"沉 → 聚 → 沉"） |

## 关键设计

1. **河洛与主卦共享同一视觉中心** —— CSS Grid `grid-area: 1 / 1`
2. **顺序时序** —— 河洛彻底消失后，卦才出现
3. **沉 → 聚 → 沉呼吸** —— `opacity 1 → .65 → 1` + `scale 1 → .94 → 1` + `brightness 1 → .92 → 1`
4. **CSS animation forwards 兜底** —— 阶段切换时显式声明终态，避免元素回弹
5. **Reduced Motion** —— 直接显示终态，跳过全部过渡

## 控制按钮

- **重播入场动画** —— 重新触发整套时序
- **Reduced Motion** —— 演示无动画降级效果

## 相关资源

- 主工程（React + TS + Vite）：仓库根 `frontend-case/`
- 设计规范：仓库根 `frontend/DESIGN_SPEC.md`
- 前端规范 v1.0：仓库根 `LIORIN_FRONTEND_SPEC_V1.md`
