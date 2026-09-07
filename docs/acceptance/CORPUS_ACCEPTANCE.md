ENGINE: corpus
VERSION: 1.0.0

# BOT-CORPUS ACCEPTANCE.md — V2 现状盘点

> 生成: 2026-09-07 | 依据: V2验收和生产准入规范 (E0-E10)
> 说明: 本文件如实标注当前验收状态。CORPUS为证据资产域，非计算引擎。

## E0 Contract
STATUS: PASS
- Evidence对象: id/classic_id/source_locator/provenance 结构完整 ✅
- Source → Evidence → Rule → Judgment 链可追踪 ✅

## E1 Unit
STATUS: PASS
- test_corpus_validation.py 14 + test_full_classification.py 11 = 25 passed

## E2 Algorithm
STATUS: N/A
- 证据域非算法引擎

## E3 Boundary
STATUS: PARTIAL
- ⚠️ 需补充: 证据边界/来源边界

## E4 Negative
STATUS: PARTIAL
- ⚠️ 需补充负向测试（缺来源/缺章节/缺定位符）

## E5 Golden
STATUS: PARTIAL
- ✅ 五经原典 7,039条 (100% EXACT_PRIMARY)
- ✅ 断语库 11,478条 (E-*-DUANYU-* 4,089条新证据)

## E6 Regression
STATUS: PARTIAL

## E7 Integration
STATUS: PASS
- 五经原典 → Evidence → Rule 全链路 ✅

## E8 Production Trace
STATUS: PENDING

## E9 Independent Audit
STATUS: PENDING
- ⚠️ 4,089条新断语证据待人工核验 (43条原有待核验)

## E10 Acceptance
STATUS: CONDITIONAL

## Provenance
STATUS: PARTIAL
- ✅ 原典 provenance 完整 (7,039条)
- ⚠️ 43条evidence待核验 + 4,089条新断语证据 UNVERIFIED

## Isolation
STATUS: PASS
- 证据域独立，不污染计算引擎 ✅

## 生命周期状态
STATUS: 证据核验中
- 不得宣称全部证据 VERIFIED ⚠️

## 问题清单
| 严重性 | 问题 | 状态 |
|--------|------|------|
| P1 | 43条evidence待人工核验 | OPEN |
| P1 | 4,089条新断语证据 UNVERIFIED（需授权+核验） | OPEN |
| P2 | 渊海子平原典覆盖率8.9%（缺123篇） | OPEN |

## 验收记录
- 最近验收: 2026-09-07 (25 passed)
- 待办: 证据授权核验 → DRAFT→ACTIVE Status Gate
