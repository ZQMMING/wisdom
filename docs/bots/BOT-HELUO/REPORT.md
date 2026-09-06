# BOT-HELUO 审计报告（Phase 2 结果验证版）

**任务ID**: T-ENGINE-HELUO-004  
**审计时间**: 2026-09-05  
**审计人**: @bot-heluo  
**状态**: ✅ 完成（含 Phase 0 基准验证）

---

## 执行摘要

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 测试通过 | ✅ | 45 passed, 0 failed |
| Golden case 验证 | ✅ | 纪晓岚等全部通过 |
| Phase 0 八字入口依赖 | ✅ | 已确认 57 passed |
| Evidence 动态生成 | ⚠️ P2 | HeLuoEvidenceProducer 未接入 pipeline |
| deprecated 文件清理 | ⚠️ P2 | dayu.py/time_sequence.py 待 daily_state 重构后移除 |
| P0 阻塞 | ✅ | 无 |
| P1 阻塞 | ⚠️ | daily_state_service.py:79 HeluoCalculator 未定义 |

---

## 1. Phase 0 基准验证（已完成）

BOT-MASTER 已确认 Phase 0 八字排盘入口验证完成：

| Phase 0 项目 | 状态 |
|-------------|------|
| TimeResolver 真太阳时 | ✅ PASS |
| BaziAdapter 四柱排盘 | ✅ PASS |
| 子初换日规则 (23:00) | ✅ PASS |
| Golden Cases × 5+ | ✅ PASS |
| Phase 0 tests | 57 passed |
| 全量有效测试 | 157 passed |

**结论**: 八字排盘作为全系统共同的计算入口与基准状态已确立。

---

## 2. Heluo 生产调用链

### 2.1 活跃路径 ✅

```
pipeline_stages/compute_stage.py
  └── HeluoCanonical.calculate()        ← canonical.py (主线)
        ├── compute_dayun_liyao()       ← timeline_yun.py
        ├── compute_liunian()           ← timeline_yun.py
        ├── determine_prenatal_hexagram() ← prenatal.py
        ├── find_yuantang()             ← yuan_tang.py
        └── compute_postnatal()         ← postnatal.py

v_validation/end_to_end.py
  └── heluo_calculate()                 ← canonical.py

tests/test_heluo_canonical.py           ← 13 passed
tests/test_heluo_liunian_guji.py        ← 4 passed
tests/test_heluo_yuantang_qigong.py     ← 6 passed
tests/test_hl_schema.py                 ← 22 passed
```

### 2.2 断裂路径 ❌

```
src/tongshu/services/daily_state_service.py:79
  calculator = HeluoCalculator()    ← RuntimeError! (calculator.py 不存在)
  
应改为:
  from tongshu.engines.heluo.canonical import HeluoCanonical
  c = HeluoCanonical()
  result = c.calculate(bazi=..., gender=..., birth_hour=..., era=...)
```

---

## 3. Deprecated 文件分析

| 文件 | 状态 | 引用方 | 清理计划 |
|------|------|--------|----------|
| `dayu.py` | deprecated | `daily_state_service.py:21`, `test_heluo_dayu.py` | P2: 随 daily_state 重构移除 |
| `time_sequence.py` | deprecated | `daily_state_service.py:17`, `test_heluo_time_sequence.py` | P2: 随 daily_state 重构移除 |

两个文件均有 DeprecationWarning，但测试仍通过（兼容性保留）。

---

## 4. Evidence 链分析

### 4.1 设计架构

```
HeLuoEvidenceProducer.produce(heluo_result, birth_year)
  → list[EngineEvidence]
  → UUID-based evidence_id
  → rule_id: "HL_*"
  → temporal_scope: TemporalScope.BIRTH | LIUNIAN
```

### 4.2 现状

- `src/tongshu/engines/heluo/evidence_producer.py` — ✅ 已定义
- `data/evidence/heluo/` — ❌ 空目录（证据未写入）
- 调用方 — ❌ 无（pipeline 未接入）

### 4.3 修复建议（P2）

在 `compute_stage.py` 合适位置（如 compute_stage.run() 末尾）添加：

```python
from tongshu.engines.heluo.evidence_producer import HeLuoEvidenceProducer
producer = HeLuoEvidenceProducer()
evidences = producer.produce(result.heluo_result, birth_year=result.birth_year)
# 写入 data/evidence/heluo/ 或数据库
```

---

## 5. 河洛-易经互通

### 5.1 实际模块

- `heluo_yi_flow.py` — 桥接河洛理数与易经卦象
- 提供: `get_liunian_gua()`, `gua_direction()`, `heluo_yi_dir()`
- 依据: 《河洛理数·卷之四/五》+ 易经体用五行生克

### 5.2 测试问题

- `test_b01_heluo_yi_passthrough.py` — collect 失败（`ZiweiAdapter` 导入错误，非 heluo 问题）
- `test_heluo_yi_flow.py` — collect 失败（模块名路径问题）

### 5.3 耦合点

| 耦合 | 位置 | 状态 |
|------|------|------|
| TRIGRAM_ELEMENT 五行映射 | `heluo/numbers.py` → `heluo_yi_flow.py` | ✅ 弱耦合，独立副本 |
| EVENT_SIGNAL 格式 | `yi_interpreter.py` | ✅ 互不依赖 |

---

## 6. 无生产调用者文件清单

| 文件 | 内容 | 建议 |
|------|------|------|
| `hexagram_state.py` | 卦象状态计算（动静/旺衰/体用） | 保留，诊断层预留 |
| `metrics_v2.py` | 解释质量评分 | 保留，评估工具 |
| `yi_interpreter.py` | EVENT_SIGNAL 解卦层 | 需接入 pipeline |

---

## 7. 问题汇总

### P0
无

### P1（阻塞）
- `daily_state_service.py:79` — `HeluoCalculator` 未定义，运行必崩
  - 修复方案：改用 `HeluoCanonical().calculate()` 或整块注释

### P2
- `HeLuoEvidenceProducer` 未接入生产 pipeline，`data/evidence/heluo/` 为空
- `dayu.py` / `time_sequence.py` deprecated 文件待 daily_state 服务重构后移除
- `yi_interpreter.py` EVENT_SIGNAL 解卦层未接入 pipeline

### Info
- `frozen_state.py` 不存在（H16-H17 已清理）
- `diagnosis_rule_graph.py` 不存在（计划未实现）
- `heluo_yi_passthrough` 模块名不存在，实际为 `heluo_yi_flow.py`

---

## 8. 验收标准（Phase 2 结果验证版）

| 标准 | 状态 |
|------|------|
| Phase 0 八字入口验证 | ✅ 57 passed |
| 测试通过 | ✅ 45 passed |
| Golden Dataset 无降级 | ✅ 纪晓岚等全部通过 |
| 证据 provenance 完整 | ⚠️ HeLuoEvidenceProducer 未接入 |
| 无遗留 P0 问题 | ✅ |
| 无遗留 P1 问题 | ❌ 1 个 P1 |

---

## 9. 与 BOT-YI 的耦合确认

```
data/tiaohou/          ← Yi 的典籍数据（64hex.json 等）
data/evidence/heluo/   ← Heluo 的证据目录（当前为空）

两者独立，无共享风险。
```

**结论**: Heluo 与 Yi 符合架构冻结要求的隔离原则。

---

*BOT-HELUO | 顺天项目 | 2026-09-05*
