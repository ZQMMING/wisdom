ENGINE: meihua
VERSION: 1.0.0

# BOT-MEIHUA ACCEPTANCE.md — V2 现状盘点

> 生成: 2026-09-07 | 依据: V2验收和生产准入规范 (E0-E10)
> 说明: 本文件如实标注当前验收状态，不虚标。梅花为V2一级独立引擎。

## E0 Contract
STATUS: PARTIAL
- 双模式定义 ✅: Mode A Birth-based / Mode B Event-based
- ⚠️ 需确认 input_mode/calculation_method/provenance 字段实现

## E1 Unit
STATUS: PASS
- tests/heluo/test_meihua.py 19 + test_new_engines.py 梅花4 = 23 passed
- 功能: 时间起卦/数字起卦/字数起卦/本卦/变卦/互卦/体用

## E2 Algorithm
STATUS: PASS
- 起卦链: 时间/数字/外应三类起卦 → 动爻 → 变卦/互卦 → 体用关系 ✅
- 独立于河洛(无元堂/先天后天) ✅

## E3 Boundary
STATUS: PARTIAL
- ⚠️ 需补充: 起卦数字边界/时间起卦边界/动爻边界/体用边界/变卦边界/事件输入边界

## E4 Negative
STATUS: PARTIAL
- ⚠️ 需补充 fail-closed 负向测试

## E5 Golden
STATUS: FAIL
- ❌ 无正式Golden Set（需覆盖起卦方法/动爻边界/数字起卦/时间起卦/事件输入/体用关系/变卦/特殊边界）

## E6 Regression
STATUS: PASS
- ✅ scripts/golden_replay.py — 30/30 案例重放OK(含负向案例expected_exception), 基线hash稳定(1cf8f6f0)

## E7 Integration
STATUS: PARTIAL
- ⚠️ MeiHuaAdapter 未接入（双模式适配器待建）

## E8 Production Trace
STATUS: FAIL
- ❌ 未接入生产路径

## E9 Independent Audit
STATUS: PENDING

## E10 Acceptance
STATUS: CONDITIONAL

## Provenance
STATUS: FAIL
- ❌ data/evidence/meihua/ 不存在

## Isolation
STATUS: PASS
- 一级独立引擎，不归属易经/河洛 ✅

## 生命周期状态
STATUS: Bot已激活，代码就绪
- 不得宣称 Production Ready ⚠️

## 问题清单
| 严重性 | 问题 | 状态 |
|--------|------|------|
| P0 | E5 Golden Set未建立 | OPEN |
| P0 | E7 Adapter未接入 | OPEN |
| P0 | evidence/meihua/ 不存在 | OPEN |
| P1 | E3边界测试未建立 | OPEN |

## 验收记录
- 最近验收: 2026-09-07 (23 passed)
- 待办: Golden Set → Adapter → 证据目录
