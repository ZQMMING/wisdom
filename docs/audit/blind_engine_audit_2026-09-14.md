# 盲派引擎代码审计报告

**审计时间**: 2026-09-14  
**审计范围**: `src/tongshu/engines/blind*.py` 及相关测试  
**审计标准**: V2.2.2 FINAL §70/§90（盲派引擎独立性）

---

## 一、审计概览

| 项目 | 状态 |
|------|------|
| 核心文件 | ✅ 存在 |
| 测试覆盖率 | ✅ 93 passed |
| Golden测试 | ✅ 21 passed |
| 证据链 | ✅ 完整 |

---

## 二、文件统计

### 核心引擎文件（4,785行）

| 文件 | 行数 | 功能 |
|------|------|------|
| `blind_bazi_engine.py` | 2,544 | 主引擎（宾主/体用/做功） |
| `blind_interpretation.py` | 834 | 解读层 |
| `blind_judgment.py` | 347 | 事件判定层 |
| `blind_themes.py` | 394 | 主题分类 |
| `blind_yingqi.py` | 666 | 应期引擎 |
| **总计** | **4,785** | |

### 子目录结构

```
src/tongshu/engines/blind/
├── evidence_producer.py    # 证据生产者
├── palace.py               # 宫位模块
├── rules/
│   ├── graph.py           # 规则图
│   ├── matcher.py         # 匹配器
│   └── models.py          # 数据模型
├── workchain.py           # 做功链
└── workgraph.py           # 做功图
```

---

## 三、架构合规性检查

### ✅ V2.2.2 §70 独立引擎规则

```python
# L15-24: 架构铁律注释（禁止违规导入）
# 盲派引擎与子平引擎是【完全独立】的两个引擎：
#   - 唯一共同消费层 = 八字排盘引擎输出的基础事实
#   - 盲派引擎【禁止】import / 消费 / 复用子平辨层任何东西
```

**检查结果**：
- ✅ 盲派引擎仅导入 `bazi_engine.BaziChart`（L0事实层）
- ✅ 未导入 `ziping_v3.*` 模块
- ✅ 未导入 `yongshen.py`（喜用神）
- ✅ 未导入 `pattern_routes.py`（格局路线）

### ✅ 导入链路验证

```python
# blind_bazi_engine.py L31-36
from ..engines.bazi_engine import BaziEngine, BaziChart, STEM_ELEMENT, _branch_element, canonical_bazi_engine
from ..signal.canonical_signal import CanonicalSignal, SourceEngine, SignalLayer, SignalTemporalScope
from ..signal.adapters import BaseAdapter, AdapterContext
from ..spec.event_ontology_v1 import Domain, EventDirection
from ..reasoning.bazi_ten_gods import ten_god, BRANCH_HIDDEN_STEMS, GENERATES, CONTROLS
from ..reasoning.bazi_fixed_tables import road_branch, absolute_branch
```

**所有导入均为**：
- L0事实层（BaziChart, STEM_ELEMENT）
- 信号层（CanonicalSignal）
- 通用规则（ten_gods, fixed_tables）
- **无子平辨层**（旺衰/强弱/格局/用神）

---

## 四、核心概念实现

### 1. 宾主体系（L8-9）

```python
# 日柱为「主」（我），其余为「宾」（外界）
```

**实现状态**：✅ 已实现于 `BlindBaziResult.workchain_signals`

### 2. 体用分类（L196-199）

```python
TI_TEN_GODS = {'比肩', '劫财', '偏印', '正印', '食神', '伤官'}   # 体（本钱/工具）
YONG_TEN_GODS = {'正财', '偏财', '正官', '七杀'}               # 用（目标：财官）
YONG_TEN_GODS_CONDITIONAL = {'伤官'}                          # 伤官条件角色
```

**实现状态**：✅ 已实现，支持"伤官双角色"

### 3. 做功方法（L10-11）

```python
# 制用 / 化用 / 生用 / 合用 / 墓用
```

**实现状态**：✅ 五法齐全，见 `BlindWorkMethod` 枚举

---

## 五、证据链审计

### 证据目录：`data/evidence/blind_seg/`

| 类别 | 文件数 | 状态 |
|------|--------|------|
| WORK_METHOD | 6条 | ✅ |
| WORK_TARGET | 5条 | ✅ |
| WORK_RELATION | 4条 | ✅ |
| WORK_EFFICIENCY | 3条 | ✅ |
| GUEST_HOST | 5条 | ✅ |
| BODY_USE | 6条 | ✅ |
| IMAGE | 6条 | ✅ |
| POWER_PARTY | 5条 | ✅ |
| YING_QI | 5条 | ✅ |
| EMPTY_USELESS | 6条 | ✅ |
| COMPLEX_WORK | 3条 | ✅ |
| **总计** | **59条** | ✅ |

### 元数据文件

```
manifest.json           # 总索引
provenance_final_status.json  # 来源状态
provenance_rules.json         # 来源规则
source_verification_*.json    # 来源验证报告
reclassification_matrix.json  # 重新分类矩阵
```

---

## 六、测试结果

### 6.1 全量测试

```bash
python -m pytest tests/test_blind_*.py -v
```

**结果**：
```
==================== 93 passed, 7 subtests passed in 0.74s ====================
```

### 6.2 Golden测试

```bash
python -m pytest tests/test_blind_golden.py -v
```

**结果**：
```
==================== 21 passed in 0.31s ====================
```

### 6.3 规则合规性测试

| 测试类 | 状态 |
|--------|------|
| TestBlindRuleCompliance | ✅ 22 passed |
| TestBlindSignalCompliance | ✅ 5 passed |
| TestBlindYingqiSeverityCompliance | ✅ 2 passed |
| TestBlindV30LiteratureRules | ✅ 5 passed |

---

## 七、V2.2.2合规项核对

| 规则项 | 状态 | 说明 |
|--------|------|------|
| §70 独立引擎 | ✅ | 无违规导入 |
| §90 ZIPING_DEPENDENCY | ✅ | FORBIDDEN规则已遵守 |
| §47 禁用比较算子 | ✅ | 使用枚举判等 |
| §49 身强身弱 | ✅ | 盲派用自己的体用体系 |
| Fail Closed | ✅ | UNDETERMINED默认 |
| 断语钩子 | ✅ | 使用五经原文词汇 |

---

## 八、风险项

### 低风险项

1. **注释中的"段建业盲派"**：方法论归属明确，非经典冲突
2. **五经原文引用**：如"渊海子平·地支六破"为引用，非消费

### 无需处理

- 无违禁符号
- 无绝对路径
- 无LLM调用
- 无跨引擎依赖

---

## 九、结论

| 维度 | 评级 |
|------|------|
| 代码结构 | ✅ PASS |
| 架构合规 | ✅ PASS |
| 测试覆盖 | ✅ PASS |
| 证据链 | ✅ PASS |
| V2.2.2符合性 | ✅ PASS |

**综合评定**：**BASIC_VALIDATED** ✅

---

## 十、附录

### A. 测试文件清单

```
tests/test_blind_golden.py              # 21 cases
tests/test_blind_integration_bazi.py    # 9 cases
tests/test_blind_negative.py            # 6 cases
tests/test_blind_rule_compliance.py     # 22 cases
tests/test_blind_signal_regression.py   # 5 cases
tests/test_blind_themes.py              # 12 cases
tests/test_blind_yingqi.py              # 14 cases
tests/test_mingli_bench_blind.py        # 4 cases
```

### B. 关键文件SHA256

```
blind_bazi_engine.py: 已审计（2,544行）
blind_judgment.py: 已审计（347行）
```

---

**审计员**: BOT-MASTER  
**日期**: 2026-09-14
