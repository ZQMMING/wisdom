ENGINE: ziping
VERSION: 0.9.0

# BOT-ZIPING ACCEPTANCE.md — V2 现状盘点

> 生成: 2026-09-07 | 依据: V2验收和生产准入规范 (E0-E10)
> 说明: 本文件如实标注当前验收状态，不虚标。

## E0 Contract
STATUS: PASS
- Input: Canonical State → ZiPingAdapter → ZiPing Engine → Judgment ✅
- 只消费BAZI字段，不重算十神 ✅

## E1 Unit
STATUS: PASS
- test_phase3_p0_judgment.py 14/14 + test_phase3_p0.py 1/1 = 15 passed

## E2 Algorithm
STATUS: PASS
- 三大域确定性算法: WANGSHUAI(四维评分) / GEJU(五级链) / YONGSHEN(五级优先级) ✅
- 变格无证据 → 返回UNKNOWN（fail-closed）✅

## E3 Boundary
STATUS: PARTIAL
- ⚠️ 需补充: 月令切换边界 / 十神边界 / 格局边界专项测试

## E4 Negative
STATUS: PASS
- 缺失context → UNKNOWN + 原因说明 ✅
- 引用真实性断言（不臆造evidence ID）✅

## E5 Golden
STATUS: PARTIAL
- ⚠️ 无正式ZIPING Golden Set（需建立经典案例集，覆盖旺衰/格局/用神三分支）
- 现有: 5个命例在 test_all_refs_resolve_to_real_files

## E6 Regression
STATUS: PARTIAL
- ⚠️ 版本回归未系统化

## E7 Integration
STATUS: PASS
- ✅ 辨层接线完成: BaziEngine.compute → ZipingBridge → JudgmentFactory
- test_ziping_bridge.py 6/6 (2026-09-07, commit d3cd7fba)

## E8 Production Trace
STATUS: PARTIAL
- ⚠️ 接线已验证，完整生产API路径待最终确认

## E9 Independent Audit
STATUS: PENDING

## E10 Acceptance
STATUS: CONDITIONAL (有条件通过，附约束)

## Provenance
STATUS: PASS
- rule_refs/evidence_refs 对应真实文件 ✅

## Isolation
STATUS: PASS
- 不修改BAZI，不混入盲派

## 生命周期状态
STATUS: 算法就绪，缺pipeline接线
- 不得宣称 Production Ready ⚠️

## 问题清单
| 严重性 | 问题 | 状态 |
|--------|------|------|
| ~~P0~~ | ~~E7 零生产调用方~~ | ✅ 已解决 (d3cd7fba) |
| P1 | E5 Golden Set未建立 | OPEN |
| P2 | 阳刃格取格标准（帝旺位口径） | 待User裁定 |
| P2 | 变格提前return跳过月令受冲检查 | OPEN |

## 验收记录
- 最近验收: 2026-09-07 (15 + 6 = 21 passed)
- 待办: Golden Set → 生产路径最终确认
