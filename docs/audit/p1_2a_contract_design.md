# P1.2-A — Contract Design: EngineEvidence → SemanticAtom → Assertion

**Date**: 2026-09-01  
**Owner**: Agnes (Subagent)  
**Branch**: main  
**Status**: 🟢 Final Design Document  

---

## 背景

当前生产路径违反 V13 第 1 条硬约束：

```
pipeline.py → ComputeStage → SignalEngine.build() → dict[str, list[Signal]]
```

`Signal`（`reasoning/signal_engine.py:110`）携带 `direction`/`polarity`/`strength`，这是 V13 **明确禁止**的。

V13 最终架构要求的数据链为：

```
Engine → EngineEvidence（纯事实）→ SemanticAtom → Assertion → Mapping → Guidance
```

本文档是 P1.2-A 的最终设计基线，定义 EngineEvidence / SemanticAtom / Assertion / Judgment 四个核心合约的边界与迁移路径。

---

## 1. EngineEvidence Schema

### 1.1 设计原则

1. **纯事实**：只描述客观计算结果（结构/数值/位置/时间/关系/状态）
2. **禁止价值判断**：无 `direction` / `polarity` / `strength` / `confidence`
3. **规则可追溯**：`rule_id` 稳定不变，可反查到具体规则文件
4. **引擎可识别**：`engine` 字段标识来源（ZI_PING / BLIND_SCHOOL / ZI_WEI / HE_LUO / YI_JING）
5. **时间可定位**：`temporal_scope` 标准化（birth / year / month / day / hour）

### 1.2 完整 Schema 定义

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Literal
from enum import Enum


class EngineName(str, Enum):
    """五大引擎枚举（V13 §三冻结）"""
    ZI_PING = "ZI_PING"
    BLIND_SCHOOL = "BLIND_SCHOOL"
    ZI_WEI = "ZI_WEI"
    HE_LUO = "HE_LUO"
    YI_JING = "YI_JING"


class TemporalScope(str, Enum):
    """时间粒度枚举（V13 §三冻结）"""
    BIRTH = "birth"       # 本命/先天结构
    YEAR = "year"         # 流年
    MONTH = "month"       # 流月
    DAY = "day"           # 流日
    HOUR = "hour"         # 流时


@dataclass(frozen=True)
class EngineEvidence:
    """V13 统一证据合约。所有引擎输出到此层。
    
    禁止字段：direction, polarity, strength, confidence
    """
    # 身份
    engine: EngineName
    rule_id: str                              # 稳定规则ID，禁止运行时变更语义
    
    # 核心事实
    value: Any                                # 原始计算值（天干/地支/十神/星曜/卦象等）
    temporal_scope: TemporalScope             # birth/year/month/day/hour
    
    # 附加属性（各引擎自有语义）
    attributes: dict[str, Any] = field(default_factory=dict)
    
    # 追溯字段（V13 §四强制要求）
    source_rule_ref: Optional[str] = None     # 规则文件引用（如 "rules/zp_zheng_cai.json"）
    source_field: Optional[str] = None        # 原始计算字段名（如 "ten_god", "branch_clash"）
    calculation_version: str = "2026.08"      # 计算版本（P0 冻结后禁止修改）
    
    def to_dict(self) -> dict:
        return {
            "engine": self.engine.value,
            "rule_id": self.rule_id,
            "value": self.value,
            "temporal_scope": self.temporal_scope.value,
            "attributes": dict(self.attributes),
            "source_rule_ref": self.source_rule_ref,
            "source_field": self.source_field,
            "calculation_version": self.calculation_version,
        }
```

### 1.3 示例

**子平伤官示例**（正确）：
```python
EngineEvidence(
    engine=EngineName.ZI_PING,
    rule_id="ZP_TEN_GOD_SHANG_GUAN",
    value="丙",
    temporal_scope=TemporalScope.BIRTH,
    attributes={
        "ten_god": "伤官",
        "element": "火",
        "stem": "丙",
        "position": "year",
    },
    source_rule_ref="rules/zp_ten_god.json",
    source_field="ten_god",
)
```

**紫微化忌示例**（正确）：
```python
EngineEvidence(
    engine=EngineName.ZI_WEI,
    rule_id="ZW_TRANS_HUA_JI",
    value="禄存",
    temporal_scope=TemporalScope.YEAR,
    attributes={
        "star": "禄存",
        "transformation": "化忌",
        "palace": "财帛宫",
    },
    source_rule_ref="rules/zw_sihua.json",
    source_field="transformation",
)
```

### 1.4 禁止示例（错误）

```python
# ❌ 禁止携带 value 附带价值判断
EngineEvidence(engine=..., rule_id=..., value="伤官", attributes={"polarity": "positive"})

# ❌ 禁止在 EngineEvidence 层计算 direction
EngineEvidence(engine=..., rule_id=..., value=..., attributes={"direction": "caution"})
```

---

## 2. SemanticAtom Schema

### 2.1 设计原则

1. **查表产物**：SemanticAtom 是 EngineEvidence 经过语义知识库查表后的产物
2. **无方向**：SemanticAtom 不产生 direction，仅携带语义键（semantic_keys）
3. **领域候选**：通过 `domain_candidates` 提供候选人生维度，不预分配 domain
4. **溯源到 EngineEvidence**：每个 SemanticAtom 必须保留 evidence_ref

### 2.2 完整 Schema 定义

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SemanticAtom:
    """语义原子层数据合约。从 EngineEvidence 经知识库查表后生成。
    
    禁止字段：direction, polarity
    """
    # 身份
    atom_id: str                                # 如 "TEN_GOD_SHANG_GUAN", "ZW_STAR_ZIWEI"
    engine: EngineName                          # 来源引擎
    evidence_ref: str                           # 追溯到 EngineEvidence.rule_id
    
    # 语义内容（无方向）
    semantic_keys: List[str] = field(default_factory=list)   # 如 ["EXPRESSION", "INNOVATION", ...]
    domain_candidates: List[str] = field(default_factory=list)  # 如 ["CAREER", "GROWTH", "DECISION"]
    
    # 附加元数据
    label_zh: str = ""                          # 中文标签（如 "伤官"）
    category: str = ""                          # 类别（如 "TEN_GOD", "FIVE_ELEMENT", "ZIWEI_MAJOR"）
    guidance_keys: List[str] = field(default_factory=list)  # 行为指引键
    
    def to_dict(self) -> dict:
        return {
            "atom_id": self.atom_id,
            "engine": self.engine.value,
            "evidence_ref": self.evidence_ref,
            "semantic_keys": list(self.semantic_keys),
            "domain_candidates": list(self.domain_candidates),
            "label_zh": self.label_zh,
            "category": self.category,
            "guidance_keys": list(self.guidance_keys),
        }
```

### 2.3 从 EngineEvidence → SemanticAtom 的映射规则

#### 规则 1：查表映射

```python
# 语义知识库路径（data/semantic_atoms/*.json）
SEMANTIC_ATOMS_PATH = "data/semantic_atoms/"

# 查表逻辑（伪代码）
def evidence_to_atom(evidence: EngineEvidence) -> SemanticAtom:
    """从 EngineEvidence 查找对应 SemanticAtom"""
    
    # 1. 确定知识库文件
    engine = evidence.engine
    if engine == EngineName.ZI_PING:
        if "ten_god" in evidence.attributes:
            atom_file = f"{SEMANTIC_ATOMS_PATH}ten_gods.json"
        elif "element" in evidence.attributes:
            atom_file = f"{SEMANTIC_ATOMS_PATH}five_elements.json"
        else:
            return None  # 未知类型
    elif engine == EngineName.ZI_WEI:
        if "star" in evidence.attributes:
            atom_file = f"{SEMANTIC_ATOMS_PATH}ziwei_stars.json"
        elif "transformation" in evidence.attributes:
            atom_file = f"{SEMANTIC_ATOMS_PATH}transformations.json"
        else:
            return None
    elif engine == EngineName.HE_LUO:
        atom_file = f"{SEMANTIC_ATOMS_PATH}he_luo.json"
    elif engine == EngineName.YI_JING:
        if "hexagram" in evidence.attributes:
            atom_file = f"{SEMANTIC_ATOMS_PATH}hexagrams.json"
        elif "yao_position" in evidence.attributes:
            atom_file = f"{SEMANTIC_ATOMS_PATH}yao.json"
        else:
            return None
    else:
        return None
    
    # 2. 加载知识库并匹配 atom_id
    atom = load_atom(atom_file, evidence.attributes)
    if atom is None:
        return None
    
    # 3. 构造 SemanticAtom（不带 direction）
    return SemanticAtom(
        atom_id=atom["atom_id"],
        engine=evidence.engine,
        evidence_ref=evidence.rule_id,
        semantic_keys=atom["semantic_keys"],
        domain_candidates=atom["domain_candidates"],
        label_zh=atom.get("label_zh", ""),
        category=atom["category"],
        guidance_keys=atom.get("guidance_keys", []),
    )
```

#### 规则 2：保留 EngineEvidence 原始值

以下字段从 EngineEvidence 透传到 SemanticAtom：
- `evidence_ref` → `evidence.rule_id`（必须）
- `engine` → 保留原始引擎标识

#### 规则 3：domain 不预分配

SemanticAtom 只提供 `domain_candidates`（候选列表），不选择最终 domain。domain 在 Assertion 层根据 context 确定。

### 2.4 关键设计决策

**Q: 是否需要 direction 的早期预标注？**

**A: 否**。direction 在 Assertion 层才产生。SemanticAtom 只携带语义键（semantic_keys），不做吉凶判断。

```
EngineEvidence（纯事实）
    ↓ 查表
SemanticAtom（语义键 + 候选 domain）
    ↓ 结合 context
Assertion（domain + direction + intensity）
```

---

## 3. Assertion Boundary

### 3.1 什么是 Assertion

**Assertion 是系统对某个命主状态的结构化断言**，包含：
- `domain`：人生维度（CAREER / FINANCE / RELATIONSHIP / ...）
- `semantic`：语义原子标签（如 OUTPUT_ACTIVATION）
- `direction`：方向（supportive / caution / neutral）
- `intensity`：强度（0-100）
- `temporal_scope`：时间范围
- `source_engine` / `source_rule`：追溯信息
- `evidence`：追溯到 EngineEvidence 的完整链

### 3.2 完整 Schema 定义

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional


class AssertionDirection(str, Enum):
    """V13 冻结的方向枚举（仅 3 值）"""
    SUPPORTIVE = "supportive"    # 支持性
    CAUTION = "caution"          # 警示性
    NEUTRAL = "neutral"          # 中性


@dataclass(frozen=True)
class CanonicalAssertion:
    """V13 Canonical Assertion 合约。
    
    direction 在此层才产生。
    """
    assertion_id: str
    subject: str                                    # case_id
    domain: str                                     # CAREER / FINANCE / RELATIONSHIP / FAMILY / SOCIAL / GROWTH / HEALTH / DECISION
    semantic: str                                   # 语义原子标签（如 OUTPUT_ACTIVATION）
    direction: AssertionDirection                   # supportive / caution / neutral
    intensity: int                                  # 0-100
    temporal_scope: str                             # birth / year / month / day / hour
    source_engine: str                              # ZI_PING / BLIND_SCHOOL / ...
    source_rule: str                                # rule_id
    evidence: dict                                  # 追溯到 EngineEvidence 的完整链
    
    def to_dict(self) -> dict:
        return {
            "assertion_id": self.assertion_id,
            "subject": self.subject,
            "domain": self.domain,
            "semantic": self.semantic,
            "direction": self.direction.value,
            "intensity": self.intensity,
            "temporal_scope": self.temporal_scope,
            "source_engine": self.source_engine,
            "source_rule": self.source_rule,
            "evidence": self.evidence,
        }
```

### 3.3 Assertion 边界问题解答

#### Q1: Assertion 何时产生 direction？

**A**: direction 在 Assertion 层产生，不在 EngineEvidence 或 SemanticAtom 层。

产生时机：
1. EngineEvidence 提供纯事实
2. SemanticAtom 提供语义键和候选 domain
3. ContextResolver（或 Mapping Layer）结合命主 context（旺衰/格局/用神/时间）决定 direction

```python
# 示例：断言生成
def generate_assertion(
    atom: SemanticAtom,
    context: TemporalContext,
    mapping: MappingLayer,
) -> CanonicalAssertion:
    # 1. 确定 domain（从 domain_candidates 中选）
    domain = mapping.select_domain(atom.domain_candidates, context)
    
    # 2. 确定 direction（结合 context，不投票）
    direction = mapping.determine_direction(atom, context)
    
    # 3. 确定 intensity（基于证据覆盖面）
    intensity = mapping.calculate_intensity(context)
    
    return CanonicalAssertion(
        assertion_id=f"AS-{atom.evidence_ref}-{domain}",
        subject=context.case_id,
        domain=domain,
        semantic=atom.atom_id,
        direction=direction,
        intensity=intensity,
        temporal_scope=context.temporal_scope,
        source_engine=atom.engine.value,
        source_rule=atom.evidence_ref,
        evidence={"evidence_ref": atom.evidence_ref},
    )
```

#### Q2: Assertion 的输入是什么？

**A**: `SemanticAtom + TemporalContext + Mapping`

- **SemanticAtom**：提供语义键和候选 domain
- **TemporalContext**：提供命主完整时序上下文（本命/大运/流年）
- **Mapping**：提供 domain 选择和 direction 确定逻辑

#### Q3: Assertion 的 `domain` 字段如何确定？

**A**: domain 由 Mapping Layer 从 `domain_candidates` 中选定，依据是：
1. SemanticAtom 提供的候选列表
2. TemporalContext 中的时序激活信息
3. Mapping 表的域映射规则

**禁止**：直接硬编码 domain 到 EngineEvidence 或 SemanticAtom 层。

#### Q4: Assertion 与 EngineEvidence 的追溯关系如何建立？

**A**: 通过 `evidence` 字段建立完整链：

```
Assertion.evidence.evidence_ref = EngineEvidence.rule_id
Assertion.evidence.engine = EngineEvidence.engine
Assertion.evidence.temporal_scope = EngineEvidence.temporal_scope
Assertion.evidence.value = EngineEvidence.value
Assertion.evidence.attributes = EngineEvidence.attributes
```

完整追溯链：
```
Assertion → SemanticAtom → EngineEvidence → rule file → original calculation
```

---

## 4. Judgment Boundary

### 4.1 什么是 Judgment

**Judgment 是对多个 Assertion 的结构性组织**，不是新的方向判断。

### 4.2 Judgment 与 Assertion 的区别

| 维度 | Assertion | Judgment |
|------|-----------|----------|
| 粒度 | 单个语义断言 | 多个 Assertion 的集合 |
| 方向 | 单个 direction | 无聚合方向 |
| 功能 | 描述具体状态 | 组织证据覆盖面 |
| 输入 | SemanticAtom + Context | 多个 Assertion |
| 输出 | domain + direction + intensity | evidence_count + source_engines |

### 4.3 Judgment 的边界

```python
@dataclass(frozen=True)
class AssertionCluster:
    """Assertion 聚类，用于证据覆盖面统计。
    
    注意：evidence_count 表示证据数量，不是可信度投票。
    """
    domain: str
    semantic: str
    assertions: List[CanonicalAssertion]
    evidence_count: int                     # 证据数量（非投票）
    source_engines: List[str]               # 哪些引擎提供了证据
    evidence_types: List[str]               # 哪些类型的证据
    
    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "semantic": self.semantic,
            "evidence_count": self.evidence_count,
            "source_engines": list(self.source_engines),
            "evidence_types": list(self.evidence_types),
            "assertion_ids": [a.assertion_id for a in self.assertions],
        }
```

### 4.4 关键设计决策

**Q1: Judgment 是否聚合多个 Assertion？**

**A**: 是，但只做结构性组织，不做方向聚合。`evidence_count` 表示"有多少个独立证据支持这个领域"，不代表"可信度"。

**Q2: Judgment 何时产生？**

**A**: 在 Assertion 层完成后，由 Mapping Layer 或专门的 ClusterBuilder 生成。

**Q3: Judgment 是否需要方向比较？**

**A**: 否。V13 §二明确规定："互补不比较，不投票、不评分、不多数决、不加权"。

各体系独立产生 Assertion，进入同一语义空间，不做跨体系方向比较。

---

## 5. Migration Map

### 5.1 当前生产路径

```
pipeline.py
    ↓
ComputeStage
    ↓
SignalEngine.build() → dict[str, list[Signal]]
    ↓
CrossAnalyzer.analyze(bazi_signals, ziwei_signals) → CrossResult
    ↓
CanonicalComposer.compose(signals, cross_result, ...) → CanonicalContent
```

**问题**：Signal 携带方向字段，违反 V13 第 5 条硬约束。

### 5.2 目标路径

```
pipeline.py
    ↓
ComputeStage
    ↓
EngineAdapter → list[EngineEvidence]
    ↓
SemanticAtomMapper → list[SemanticAtom]
    ↓
AssertionBuilder → list[CanonicalAssertion]
    ↓
MappingLayer → dict[str, AssertionCluster]
    ↓
GuidanceComposer → Guidance
```

### 5.3 字段迁移对照表

| 当前字段（Signal） | 迁移目标 | 说明 |
|-------------------|----------|------|
| `signal_id` | `EngineEvidence.rule_id` | 规则 ID 作为追溯锚点 |
| `ontology_type` | `SemanticAtom.atom_id` | 通过查表转换为语义原子 |
| `direction` | **废弃** | 禁止在 EngineEvidence 层携带 |
| `polarity` | **废弃** | 禁止在 EngineEvidence 层携带 |
| `strength` | **废弃** | 由 Assertion.intensity 替代 |
| `layer` | `TemporalScope` | 标准化为 birth/year/month/day/hour |
| `rule_refs` | `EngineEvidence.source_rule_ref` | 规范化引用 |
| `evidence_refs` | `SemanticAtom.evidence_ref` | 追溯到 EngineEvidence |

### 5.4 废弃字段清单

| 字段 | 位置 | 废弃原因 |
|------|------|----------|
| `Signal.direction` | `reasoning/signal_engine.py:110` | V13 §四明确废除 |
| `Signal.polarity` | `reasoning/signal_engine.py:110` | V13 §四明确废除 |
| `Signal.strength` | `reasoning/signal_engine.py:110` | V13 §四明确废除 |
| `CanonicalSignal.direction` | `spec/canonical_signal.py:73` | 新架构不携带方向 |
| `CanonicalSignal.confidence` | `spec/canonical_signal.py:74` | 新架构不携带置信度 |
| `CrossAnalyzer` 方向比较逻辑 | `reasoning/cross_analysis.py:83-99` | V13 §二禁止跨体系方向比较 |
| `ConvergenceArbiter` | `signal/convergence.py` | V13 §二禁止多体系方向比较 |

### 5.5 SignalEngine.build() 返回值类型变化

**当前**：
```python
def build(self, bazi, ziwei, huangli, gender, theme=None, heluo_result=None) -> dict:
    return {
        "BASELINE": list[Signal],
        "CYCLE_CONTEXT": list[Signal],
        "DAILY_ACTIVATION": list[Signal],
    }
```

**目标**：
```python
def build(self, bazi, ziwei, huangli, gender, theme=None, heluo_result=None) -> dict:
    return {
        "BASELINE": list[EngineEvidence],
        "CYCLE_CONTEXT": list[EngineEvidence],
        "DAILY_ACTIVATION": list[EngineEvidence],
    }
```

后续处理链：
```python
evidence_list = signal_engine.build(...)
atoms = semantic_mapper.to_atoms(evidence_list)
assertions = assertion_builder.build_atoms(atoms, context)
clusters = mapping_layer.cluster_assertions(assertions)
```

### 5.6 CrossAnalyzer 替代方案

**当前问题**：CrossAnalyzer 比较 Bazi 和 Ziwei 的方向是否一致（ALIGNED/CONFLICTED/PARTIAL），这违反 V13 §二"互补不比较"原则。

**替代方案**：

```python
class EvidenceCoverage:
    """证据覆盖面统计，替代 CrossAnalyzer。
    
    不做方向比较，只做结构性组织。
    """
    
    def __init__(self):
        self._clusters: dict[str, AssertionCluster] = {}
    
    def add_assertion(self, assertion: CanonicalAssertion):
        """添加 Assertion 到对应聚类。
        
        不再比较方向，只记录哪些引擎提供了哪些领域的证据。
        """
        key = f"{assertion.domain}:{assertion.semantic}"
        if key not in self._clusters:
            self._clusters[key] = AssertionCluster(
                domain=assertion.domain,
                semantic=assertion.semantic,
                assertions=[],
            )
        self._clusters[key].assertions.append(assertion)
    
    def get_coverage(self) -> dict:
        """返回证据覆盖面统计。
        
        返回格式：
        {
            "CAREER": {
                "OUTPUT_ACTIVATION": {
                    "evidence_count": 3,
                    "source_engines": ["ZI_PING", "BLIND_SCHOOL"],
                }
            }
        }
        """
        result = {}
        for cluster in self._clusters.values():
            domain = cluster.domain
            semantic = cluster.semantic
            if domain not in result:
                result[domain] = {}
            result[domain][semantic] = {
                "evidence_count": len(cluster.assertions),
                "source_engines": list(cluster.source_engines),
            }
        return result
```

---

## 6. Deletion List

### 6.1 必须删除的文件

| 文件路径 | 删除范围 | 原因 |
|----------|----------|------|
| `src/tongshu/reasoning/signal_engine.py` | 整个文件 | Signal class 违反 V13；需重写为 EngineAdapter |
| `src/tongshu/reasoning/cross_analysis.py` | 整个文件 | CrossAnalyzer 比较方向违反 V13 §二 |
| `src/tongshu/signal/convergence.py` | 整个文件 | ConvergenceArbiter 做跨体系方向比较 |
| `src/tongshu/signal/aggregator.py` | 整个文件 | 基于 Signal 的聚合逻辑需替换 |
| `src/tongshu/signal/legacy_adapter.py` | 整个文件 | 已在 9005c8e 标记 NON_PRODUCTION，零引用 |
| `src/tongshu/spec/canonical_signal.py` | 整个文件 | V1.2 旧 schema，将被 EngineEvidence 替代 |
| `src/tongshu/signal/canonical_signal.py` | 整个文件 | 扩展版 CanonicalSignal，无生产调用 |
| `src/tongshu/signal/normalizer.py` | 整个文件 | 基于旧方向逻辑的归一化 |

### 6.2 需要修改的代码引用

| 文件 | 修改内容 |
|------|----------|
| `src/tongshu/types.py` | 移除 Signal / CrossResult 引用，新增 EngineEvidence / SemanticAtom / CanonicalAssertion |
| `src/tongshu/pipeline.py` | 移除 CrossAnalyzer 实例化，改用 EvidenceCoverage |
| `src/tongshu/pipeline_stages/compute_stage.py` | 替换 SignalEngine 为 EngineAdapter，移除 CrossAnalyzer |
| `src/tongshu/canonical/composer.py` | 移除 Signal 格式化逻辑，改用 Assertion 序列化 |
| `src/tongshu/engines/annual_event_evaluator.py` | 移除 ConvergenceArbiter 引用（grep 确认无生产调用） |
| `src/tongshu/reasoning/__init__.py` | 移除 CrossAnalyzer / CrossResult 导出 |

### 6.3 可选保留的文件

| 文件 | 状态 | 说明 |
|------|------|------|
| `src/tongshu/assertion_v2/contract.py` | 保留 | 包含 NativeJudgment / JudgmentLibrary，可参考但需重构 |
| `src/tongshu/reasoning/temporal_context_contract.py` | 保留 | DerivedSignal / TemporalContext 可作为 context 输入 |
| `src/tongshu/feature_registry/contract.py` | 保留 | Feature 注册表可参考 |
| `data/semantic_atoms/*.json` | 保留 | 8 个语义知识库文件（缺 modern_concepts.json） |

### 6.4 待补充的语义原子文件

根据 V13 §八，以下文件缺失，需新建：
- `data/semantic_atoms/modern_concepts.json`（Mapping Layer 目标）

---

## 附录 A：V13 硬约束回顾

| 约束编号 | 内容 |
|----------|------|
| ① | 不再改引擎算法，只改中间链路 |
| ② | 不再做体系投票：互补不比较，不投票、不评分、不多数决、不加权 |
| ③ | 不让 LLM 判断方向：LLM 只负责自然语言表达 |
| ④ | 不让传统术语直接穿透到用户界面：必须经过 Semantic Atom → Modern Concept → Domain → Guidance |
| ⑤ | **EngineEvidence 不能有 polarity/direction**：只保留事实/数值/结构/位置/时间，方向在 Assertion 之后才产生 |
| ⑥ | SYSTEM_WEIGHTS 彻底删除 |
| ⑦ | 喜用神走同一条链 |
| ⑧ | AuditFlag 冻结（P0-P4 不主动触发） |

---

## 附录 B：数据流向图

```
┌──────────────────────────────────────────────────────────────────────┐
│ Deterministic Engine                                                │
│ 子平/盲派/紫微/河洛/易经                                             │
└───────────────────────┬──────────────────────────────────────────────┘
                        │ raw evidence（纯事实）
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│ EngineEvidence                                                      │
│ - engine: EngineName                                                │
│ - rule_id: str (stable)                                             │
│ - value: Any (事实值)                                                │
│ - temporal_scope: TemporalScope                                     │
│ - attributes: dict (十神/五行/天干/宫位等)                            │
│                                                                      │
│ ❌ 禁止: direction, polarity, strength, confidence                  │
└───────────────────────┬──────────────────────────────────────────────┘
                        │ 查表（data/semantic_atoms/*.json）
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│ SemanticAtom                                                        │
│ - atom_id: str                                                      │
│ - engine: EngineName                                                │
│ - evidence_ref: str                                                 │
│ - semantic_keys: List[str]                                          │
│ - domain_candidates: List[str]                                      │
│ - label_zh: str                                                     │
│ - category: str                                                     │
│                                                                      │
│ ❌ 无 direction                                                       │
└───────────────────────┬──────────────────────────────────────────────┘
                        │ 结合 TemporalContext
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│ CanonicalAssertion                                                  │
│ - assertion_id: str                                                 │
│ - subject: str (case_id)                                            │
│ - domain: str (CAREER/FINANCE/...)                                  │
│ - semantic: str (语义原子标签)                                        │
│ - direction: Literal["supportive", "caution", "neutral"]            │
│ - intensity: int (0-100)                                            │
│ - temporal_scope: str                                               │
│ - source_engine: str                                                │
│ - source_rule: str                                                  │
│ - evidence: dict (追溯到 EngineEvidence)                              │
│                                                                      │
│ ✓ direction 在此层产生                                               │
└───────────────────────┬──────────────────────────────────────────────┘
                        │ 聚类（不比较方向）
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│ AssertionCluster                                                    │
│ - domain: str                                                       │
│ - semantic: str                                                     │
│ - assertions: List[CanonicalAssertion]                              │
│ - evidence_count: int (证据数量，非投票)                              │
│ - source_engines: List[str]                                         │
│                                                                      │
│ ❌ 不做跨体系方向比较                                                 │
└───────────────────────┬──────────────────────────────────────────────┘
                        │ Mapping Layer
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Guidance                                                            │
│ - domain: str                                                       │
│ - headline: str                                                     │
│ - state: str                                                        │
│ - opportunities: List[str]                                          │
│ - cautions: List[str]                                               │
│ - actions: List[str]                                                │
│ - avoid: List[str]                                                  │
│ - evidence: List[str] (rule_id 列表)                                 │
└───────────────────────┬──────────────────────────────────────────────┘
                        │ LLM Renderer（只负责自然语言表达）
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 用户界面                                                            │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 附录 C：实施阶段对齐

| V13 阶段 | 内容 | 本文档覆盖 |
|----------|------|-----------|
| P0 | 接口统一 + 清除旧方向机制 | §5 Migration Map、§6 Deletion List |
| P1 | Semantic Atom 知识库建设 | §2 SemanticAtom Schema |
| P2 | Rules → Semantic Atoms | §1 EngineEvidence Schema |
| P3 | Signal → Semantic Signal | §5 Migration Map |
| P4 | Assertion Cluster | §4 Judgment Boundary |
| P5 | Mapping + Guidance Composer | （后续文档） |
| P6 | Golden Dataset / 真实案例验证 | （后续文档） |

---

*本文档为 P1.2-A 最终设计基线，依据 ARCHITECTURE_V13_FINAL.md §三~§四制定。*
