ENGINE: bazi
VERSION: 1.0.0

# BOT-BAZI ACCEPTANCE.md — V2 现状盘点

> 生成: 2026-09-07 | 依据: V2验收和生产准入规范 (E0-E10)
> 说明: 本文件如实标注当前验收状态，不虚标。未达标项不得宣称通过。

## E0 Contract
STATUS: PASS
- Input: BirthInput → TimeResolver → CalendarResolver → Bazi Foundation → Canonical Bazi State ✅
- 时间基准分离: 节气用民用时间 / 时柱用真太阳时 / 日柱用有效时间 ✅

## E1 Unit
STATUS: PASS
- test_bazi_engine.py (12) + test_b02_late_zi_golden.py (7) = 19 passed

## E2 Algorithm
STATUS: PASS
- 四柱计算链: BirthInput → 四柱 → 大运 完整路径已验证

## E3 Boundary
STATUS: PASS
- test_time_boundary.py / test_bazi_boundary.py
- 覆盖: 子初/节气边界/月令切换/年柱切换/时辰边界/真太阳时/时区/DST

## E4 Negative
STATUS: PASS
- fail-closed 验证: invalid/missing input 处理正确

## E5 Golden
STATUS: PASS
- cases/bazi/ (celebrity50 + contest8 2021-2025)
- cases/golden/ (bazi_garden_cases + time_garden_cases + golden_cases + ground_truth_frozen)
- LOAD=100% EXECUTE=100% UNEXPECTED_SKIP=0 ✅

## E6 Regression
STATUS: PASS
- 跨版本回归已运行

## E7 Integration
STATUS: PASS
- Canonical State → Adapter → Engine 独立验证

## E8 Production Trace
STATUS: PARTIAL
- ⚠️ 需验证真实生产入口路径（Production API → Adapter → Engine）

## E9 Independent Audit
STATUS: PENDING
- 待独立审计（BOT-MASTER 或第三方）

## E10 Acceptance
STATUS: CONDITIONAL
- 基础计算已验证，未达完整生产准入

## Provenance
STATUS: PASS
- 时间/干支/四柱可追溯

## Isolation
STATUS: PASS
- 不依赖其他引擎

## 生命周期状态
STATUS: FROZEN (计算已验证，不再修改核心算法)
- 可继续开发集成 ✅
- 不得宣称 Production Ready ⚠️

## 问题清单
| 严重性 | 问题 | 状态 |
|--------|------|------|
| P1 | E8 Production Trace 待验证 | OPEN |

## 验收记录
- 最近验收: 2026-09-07 (19 passed)
- 待办: E8 Production Trace + E9 Independent Audit
