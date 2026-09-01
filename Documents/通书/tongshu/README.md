# TONGSHU 通书 — Monorepo

生活通书：NFC 智能易经吊坠 · 德国市场 · 每日东方智慧

## 结构

```
tongshu/
├── packages/
│   ├── tongshu-calendar/   # 历法引擎（核心 11 模块）
│   ├── tongshu-bazi/       # 八字引擎（复用 bazi-tool MIT）
│   ├── tongshu-rules/      # 规则引擎（DSL 入口）
│   ├── tongshu-server/     # FastAPI 服务 — 待建
│   └── tongshu-web/        # Next.js PWA — 待建
├── tests/                  # 60 个 pytest 测试
└── docs/
```

## 已实现（M1-M4：完整后端内核）

### tongshu-calendar 核心模块（11 文件）

| 模块 | 功能 | 测试 |
|---|---|---|
| lunar.py | 农历转换 / 干支 / 纳音（lunar-python MIT） | 283 日期 100% |
| solar_terms.py | 节气计算（ephem 天文算法） | 2024/2026 对照 |
| almanac.py | 黄历要素（建除/彭祖/时辰吉凶/吉神方位/冲煞） | 42 测试 ✅ |
| bazi.py | 八字排盘（四柱/五行/大运/喜用神 v1/刑冲合害） | 9 测试 ✅ |
| rules.py | 规则引擎（神煞 DSL / 宜忌聚合 / 高风险过滤） | 3 测试 ✅ |
| output.py | 输出服务（4 模块德文模板 / 个性化匹配 / 养生） | 6 测试 ✅ |

### 一键验证

```python
from tongshu.calendar import build_daily_output
from datetime import date
out = build_daily_output(date(2026, 8, 13))
print(out.lunar, out.moduls[0]["title_de"])
```

### 测试

```bash
# 60 个测试全部通过
python -m pytest tests/ -v
```

## 路线图

| 里程碑 | 状态 |
|---|---|
| M1 历法引擎 | ✅ 完成 |
| M2 八字集成 + 喜用神 v1 | ✅ 完成 |
| M3 规则引擎（宜忌 DSL） | ✅ 完成 |
| M4 输出服务（4 模块） | ✅ 完成 |
| M5 FastAPI + PostgreSQL | ✅ 完成（8/8 API 测试） |
| M6 Next.js PWA | ✅ 完成（代码 + PWA manifest + SW） |