# 盲派引擎 V1 — Full Path Frozen / Expression Unlocked

封板日期：2026-09-17
封板commit：8617a848
状态：✅ FROZEN / PRODUCTION ADMITTED / FRONTEND UNLOCKED

---

## 完整链路

```
【算层】
Bazi / Canonical Fact         ✅
  ↓
Rule Evidence V3.2           🔒 FROZEN (29条Rule)
  ↓
Rule Registry                 ✅ PASS
  ↓
Assertion Engine              ✅ PASS (29条Assertion)
  ↓
【辨层】
Judgment Evidence V1.5        🔒 FROZEN (46条ESTABLISHED)
  ↓
Judgment Registry V1          ✅ PASS
  ↓
Judgment Engine V1.2          ✅ PRODUCTION ADMITTED
  ↓
───────────── Classical Boundary ─────────────
  ↓
【解层】
Mapping Registry V1           ✅ 46条
  ↓
Mapping Human Semantic Gate   ✅ 46/46 PASS
  ↓
Modern Semantic Engine V1     ✅ M-08 Gate 12项PASS
  ↓
Modern Engine Regression      ✅ R-01~R-08 ALL PASS
  ↓
M-09 Frontend Contract        ✅ 7条铁律封板
  ↓
Frontend Render Regression    ✅ FR-01~FR-07 ALL PASS
  ↓
🔓 FRONTEND EXPRESSION        ✅ UNLOCKED
```

---

## 各层封板状态

| 层 | 状态 | 说明 |
|---|---|---|
| 算层 | ✅ FROZEN | 排盘事实层，确定性计算 |
| Rule Registry | ✅ PASS | 29条Rule封板，布尔条件禁评分 |
| Assertion Engine | ✅ PASS | 29条Assertion，0泄漏 |
| Judgment Registry | ✅ PASS | 46条Judgment，fail-closed |
| Judgment Engine | ✅ PRODUCTION ADMITTED | Clause真实执行+Exclusion真执行 |
| Mapping Registry | ✅ PASS | 46条MappingRule，review_status全PASS |
| Modern Semantic Engine | ✅ PASS | 纯确定性查表，无LLM |
| Frontend Expression | 🔓 UNLOCKED | 只渲染不解释 |

---

## 铁律清单（永久封板）

1. 布尔条件规则禁评分/百分比
2. 原典原文优先
3. 盲派/子平独立引擎
4. 流年应期不判吉凶
5. 应期=时间窗口不是事件坐实
6. 案例不进引擎Rule
7. 不引入LLM加工
8. Case→Judgment Rule禁止
9. 财富等级NOT_ESTABLISHED
10. MUKU_OPENED≠WEALTH_GAIN
11. 身体象≠疾病诊断
12. 驿马≠搬家事件
13. 经典层按书直说不做现代化稀释
14. Modern Mapping单向隔离禁止反向污染

---

## 后续治理规则

1. 盲派V1架构冻结，后续修改必须走Evidence → Rule → Assertion → Judgment → Mapping全流程
2. 新增Rule必须先有Rule Evidence，不得从案例反推
3. 新增Judgment必须先有Judgment Evidence，不得从结构直接组合
4. 新增Mapping必须人工Semantic Gate审核
5. 前端只能渲染ModernExpressionResult，不得重新解释或判断
6. 任何修改必须跑全量Regression后才能合并

---

## 关键文件索引

- Rule Evidence母表：盲派Rule_Evidence母表_V3.md
- Judgment Evidence母表：盲派Judgment_Evidence母表_V1.md
- Case Golden母表：盲派Case_Golden母表_V2.md
- Rule Registry：src/tongshu/engines/blind_rule_registry.py
- Assertion Registry：src/tongshu/engines/blind_assertion_registry.py
- Judgment Registry：src/tongshu/engines/blind_judgment_registry.py
- Judgment Engine：src/tongshu/engines/blind_judgment_engine.py
- Mapping Registry：src/tongshu/engines/blind_mapping_registry.py
- Modern Semantic Engine：src/tongshu/engines/blind_modern_engine.py
- Frontend Contract：盲派Frontend_Expression_Contract_V1.md
