"""
P0-① Canonical State — 辨证中间状态容器

依据整体裁决（2026-08-30）：
  canonical/ 目前只有 composer.py（最终输出SIR）+ validator.py，太薄。
  需要一个真正完整、封闭的 CanonicalState 作为中间事实/状态容器。

核心原则：
  1. 有数据 ≠ 有证，有证 ≠ 条件成立，条件成立 ≠ 可以直接推出最终判断
  2. 每个 State 必须可追溯：state → evidence → primitive → canonical facts → 原始命盘
  3. 禁止评分模型（strength_score / root_score / 五行计分→强弱）
  4. 整体旺衰保持 UNRESOLVED，除非有明确原典授权的综合规则
  5. CanonicalState 是只读容器，生产后不允许外部直接修改内部状态

与现有 CanonicalComposer 的关系：
  - CanonicalComposer 负责最终输出 SIR（Semantic Intermediate Representation）
  - CanonicalState 负责辨证中间状态容器
  - 两者互补，不互相替代

数据结构：
  CanonicalState
  ├── facts: List[Fact]              # L1 原始事实
  ├── relations: List[Relation]      # L1 关系
  ├── classical_states: List[ClassicalState]  # 经典局部状态
  ├── qualifiers: List[Qualifier]    # 限定条件
  ├── unresolved_reasons: List[UnresolvedReason]  # 未解决原因
  ├── provenance: Provenance         # 溯源信息
  └── overall_state: OverallState    # 整体状态（默认 UNRESOLVED）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime


# ============================================================
# 一、枚举定义
# ============================================================

class FactType(str, Enum):
    """L1 事实类型 — 纯事实，不含任何语义判断"""
    HEAVENLY_STEM = "heavenly_stem"           # 天干
    EARTHLY_BRANCH = "earthly_branch"         # 地支
    HIDDEN_STEM = "hidden_stem"               # 藏干
    TEN_GOD = "ten_god"                       # 十神
    WUXING = "wuxing"                         # 五行
    YINYANG = "yinyang"                       # 阴阳
    TWELVE_GROWTH = "twelve_growth"           # 十二长生
    POSITION = "position"                     # 位置（年/月/日/时）
    GANZHI_COMBO = "ganzhi_combo"             # 干支组合
    CLIMATE = "climate"                       # 气候（寒暖燥湿）
    OTHER = "other"                           # 其他


class RelationType(str, Enum):
    """L1 关系类型 — 事实之间的结构关系，不含价值判断"""
    SHENG = "sheng"                           # 生
    KE = "ke"                                 # 克
    TONG = "tong"                             # 同（同类）
    HE = "he"                                 # 合
    CHONG = "chong"                           # 冲
    XING = "xing"                             # 刑
    HAI = "hai"                               # 害
    PO = "po"                                 # 破
    HUI = "hui"                               # 会
    GEN = "gen"                               # 通根（藏干同干）
    POSITION_RELATION = "position_relation"   # 位置关系
    OTHER = "other"                           # 其他


class StateAuthorizationLevel(str, Enum):
    """经典状态授权等级 — 严格区分原典授权程度"""
    CLASSICAL_EXPLICIT = "classical_explicit"   # 原典明确
    CLASSICAL_IMPLICIT = "classical_implicit"   # 原典隐含
    REASONABLE_HYPOTHESIS = "reasonable_hypothesis"  # 合理假说
    ENGINEERING_DERIVED = "engineering_derived"     # 工程推导
    SOURCE_UNVERIFIED = "source_unverified"         # 来源未核验
    NOT_AUTHORIZED = "not_authorized"               # 未授权


class StateStatus(str, Enum):
    """经典状态状态"""
    CANDIDATE = "candidate"           # 候选
    QUALIFIED = "qualified"           # 有条件成立
    CONFIRMED = "confirmed"           # 已确认
    PARTIALLY_VERIFIED = "partially_verified"  # 部分核验
    UNRESOLVED = "unresolved"         # 未解决
    REJECTED = "rejected"             # 已否决


class OverallState(str, Enum):
    """整体状态 — 默认 UNRESOLVED，除非有明确原典授权的综合规则"""
    UNRESOLVED = "unresolved"         # 未解决（默认）
    NOT_DEFINED = "not_defined"       # 未定义
    CANDIDATE_STRONG = "candidate_strong"    # 候选偏强
    CANDIDATE_WEAK = "candidate_weak"        # 候选偏弱
    CANDIDATE_BALANCED = "candidate_balanced"  # 候选中和
    # 注意：最终身强/身弱不允许出现在这里，必须有明确原典授权


class QualifierType(str, Enum):
    """限定条件类型"""
    NECESSARY = "necessary"           # 必要条件
    SUFFICIENT = "sufficient"         # 充分条件
    SUPPORTING = "supporting"         # 辅助条件
    CONSTRAINING = "constraining"     # 制约条件
    BLOCKING = "blocking"             # 阻断条件
    QUALIFYING = "qualifying"         # 限定条件
    EXCEPTION = "exception"           # 例外条件


# ============================================================
# 二、核心数据结构
# ============================================================

@dataclass(frozen=True)
class Fact:
    """L1 原始事实 — 纯事实，不含任何语义判断

    示例：
      Fact(type=HIDDEN_STEM, subject="亥", value="甲", position="month")
      Fact(type=TEN_GOD, subject="甲", value="比肩", position="year")
    """
    fact_id: str                          # 事实ID
    fact_type: FactType                   # 事实类型
    subject: str                          # 主体（天干/地支/位置等）
    value: Any                            # 事实值
    position: Optional[str] = None        # 位置（年/月/日/时）
    source: str = "canonical_calculation"  # 来源
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> dict:
        return {
            "fact_id": self.fact_id,
            "fact_type": self.fact_type.value,
            "subject": self.subject,
            "value": self.value,
            "position": self.position,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class Relation:
    """L1 关系 — 事实之间的结构关系，不含价值判断

    示例：
      Relation(type=GEN, subject="壬", object="甲", relation="水生木")
      Relation(type=GEN, subject="亥中甲", object="甲", relation="通根")
    """
    relation_id: str                      # 关系ID
    relation_type: RelationType           # 关系类型
    subject: str                          # 主体
    object: str                           # 客体
    relation: str                         # 关系描述
    position: Optional[str] = None        # 位置
    source_facts: List[str] = field(default_factory=list)  # 来源事实ID
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> dict:
        return {
            "relation_id": self.relation_id,
            "relation_type": self.relation_type.value,
            "subject": self.subject,
            "object": self.object,
            "relation": self.relation,
            "position": self.position,
            "source_facts": self.source_facts,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class Provenance:
    """溯源信息 — 每个状态必须可追溯到原典和事实

    追溯链：state → evidence → primitive → canonical facts → 原始命盘
    """
    state_id: str                         # 状态ID
    classic: Optional[str] = None         # 经典名称（如"滴天髓阐微"）
    chapter: Optional[str] = None         # 章节（如"十七、衰旺"）
    source_text: Optional[str] = None     # 原典原文
    source_span: Optional[str] = None     # 原文定位
    text_type: Optional[str] = None       # 文本类型（ORIGINAL/COMMENTARY）
    author: Optional[str] = None          # 作者（如"任铁樵"）
    primitive_id: Optional[str] = None    # 关联Primitive ID
    evidence_ids: List[str] = field(default_factory=list)  # 关联Evidence ID
    fact_ids: List[str] = field(default_factory=list)      # 关联Fact ID
    relation_ids: List[str] = field(default_factory=list)  # 关联Relation ID
    authorization_level: StateAuthorizationLevel = StateAuthorizationLevel.SOURCE_UNVERIFIED
    verification_status: str = "unverified"  # 核验状态
    notes: str = ""                       # 备注

    def to_dict(self) -> dict:
        return {
            "state_id": self.state_id,
            "classic": self.classic,
            "chapter": self.chapter,
            "source_text": self.source_text,
            "source_span": self.source_span,
            "text_type": self.text_type,
            "author": self.author,
            "primitive_id": self.primitive_id,
            "evidence_ids": self.evidence_ids,
            "fact_ids": self.fact_ids,
            "relation_ids": self.relation_ids,
            "authorization_level": self.authorization_level.value,
            "verification_status": self.verification_status,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ClassicalState:
    """经典局部状态 — 从事实和关系中提取的经典语义状态

    这是"辨"的核心单元。每个状态都是局部判断，不等于整体判断。

    示例：
      ClassicalState(
        state_id="DTS-WS-005",
        name="有根",
        domain="wangshuai",
        classic="滴天髓阐微",
        value="ROOT_PRESENT",
        subject="甲木",
        status=CONFIRMED,
        authorization_level=CLASSICAL_EXPLICIT,
        provenance=Provenance(...),
      )
    """
    state_id: str                          # 状态ID
    name: str                              # 状态名称（如"有根"、"得时"）
    domain: str                            # 辨证域（如"wangshuai"、"pattern"、"climate"）
    classic: str                           # 经典来源
    value: Any                             # 状态值
    subject: str                           # 主体（如"甲木"、"日主"）
    status: StateStatus                    # 状态
    authorization_level: StateAuthorizationLevel  # 授权等级
    provenance: Provenance                 # 溯源
    qualifiers: List[str] = field(default_factory=list)  # 关联限定条件ID
    position: Optional[str] = None         # 位置
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> dict:
        return {
            "state_id": self.state_id,
            "name": self.name,
            "domain": self.domain,
            "classic": self.classic,
            "value": self.value,
            "subject": self.subject,
            "status": self.status.value,
            "authorization_level": self.authorization_level.value,
            "provenance": self.provenance.to_dict(),
            "qualifiers": self.qualifiers,
            "position": self.position,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class Qualifier:
    """限定条件 — 对经典状态的限定、制约、阻断等

    示例：
      Qualifier(
        qualifier_id="Q-001",
        type=BLOCKING,
        target_state="DTS-WS-001",
        condition="得时不旺",
        description="春木虽强，金太重而木亦危",
        source="滴天髓阐微·十七、衰旺",
      )
    """
    qualifier_id: str                      # 限定条件ID
    qualifier_type: QualifierType          # 限定条件类型
    target_state: str                      # 目标状态ID
    condition: str                         # 条件描述
    description: str = ""                  # 详细描述
    source: Optional[str] = None           # 来源
    source_text: Optional[str] = None      # 原典原文
    authorization_level: StateAuthorizationLevel = StateAuthorizationLevel.SOURCE_UNVERIFIED
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "qualifier_id": self.qualifier_id,
            "qualifier_type": self.qualifier_type.value,
            "target_state": self.target_state,
            "condition": self.condition,
            "description": self.description,
            "source": self.source,
            "source_text": self.source_text,
            "authorization_level": self.authorization_level.value,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class UnresolvedReason:
    """未解决原因 — 记录为什么某个状态或整体判断保持 UNRESOLVED

    这是项目治理的核心：不假装已经解决，明确记录未解决的原因。
    """
    reason_id: str                         # 原因ID
    target: str                            # 目标（状态ID或"overall"）
    reason: str                            # 原因描述
    category: str                          # 类别（如"原典未授权"、"关系未定义"、"数据不足"）
    blocking_items: List[str] = field(default_factory=list)  # 阻断项
    next_steps: List[str] = field(default_factory=list)      # 下一步
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "reason_id": self.reason_id,
            "target": self.target,
            "reason": self.reason,
            "category": self.category,
            "blocking_items": self.blocking_items,
            "next_steps": self.next_steps,
            "metadata": self.metadata,
        }


# ============================================================
# 三、CanonicalState 顶层容器
# ============================================================

@dataclass
class CanonicalState:
    """Canonical State — 辨证中间状态容器

    这是"算 → 辨"之间的核心数据结构。
    算层产出 Facts 和 Relations，辨层消费这些产出 ClassicalStates。

    核心约束：
      1. 整体状态默认 UNRESOLVED，不允许自动推导
      2. 每个 ClassicalState 必须有 Provenance，可追溯到原典和事实
      3. 禁止评分模型，所有状态都是结构化的，不是数字
      4. 未解决的原因必须显式记录，不允许假装解决

    与 CanonicalComposer 的关系：
      CanonicalState 是中间状态，CanonicalComposer 负责最终输出SIR。
      CanonicalComposer 可以消费 CanonicalState 来构建最终输出。
    """
    state_id: str                                             # 状态ID
    chart_id: str                                             # 命盘ID
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # L1 层
    facts: List[Fact] = field(default_factory=list)          # L1 原始事实
    relations: List[Relation] = field(default_factory=list)  # L1 关系

    # L2/L3 层（经典辨证）
    classical_states: List[ClassicalState] = field(default_factory=list)  # 经典局部状态
    qualifiers: List[Qualifier] = field(default_factory=list)              # 限定条件

    # 治理层
    unresolved_reasons: List[UnresolvedReason] = field(default_factory=list)  # 未解决原因

    # 整体状态（默认 UNRESOLVED）
    overall_state: OverallState = OverallState.UNRESOLVED
    overall_state_reason: Optional[str] = None  # 整体状态原因（如果不是UNRESOLVED，必须说明）

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ============================================================
    # 查询方法
    # ============================================================

    def get_facts_by_type(self, fact_type: FactType) -> List[Fact]:
        """按类型获取事实"""
        return [f for f in self.facts if f.fact_type == fact_type]

    def get_relations_by_type(self, relation_type: RelationType) -> List[Relation]:
        """按类型获取关系"""
        return [r for r in self.relations if r.relation_type == relation_type]

    def get_states_by_domain(self, domain: str) -> List[ClassicalState]:
        """按辨证域获取状态"""
        return [s for s in self.classical_states if s.domain == domain]

    def get_states_by_classic(self, classic: str) -> List[ClassicalState]:
        """按经典获取状态"""
        return [s for s in self.classical_states if s.classic == classic]

    def get_state_by_id(self, state_id: str) -> Optional[ClassicalState]:
        """按ID获取状态"""
        for s in self.classical_states:
            if s.state_id == state_id:
                return s
        return None

    def get_qualifiers_for_state(self, state_id: str) -> List[Qualifier]:
        """获取某个状态的所有限定条件"""
        return [q for q in self.qualifiers if q.target_state == state_id]

    def get_unresolved_for_target(self, target: str) -> List[UnresolvedReason]:
        """获取某个目标的未解决原因"""
        return [r for r in self.unresolved_reasons if r.target == target]

    # ============================================================
    # 验证方法
    # ============================================================

    def validate(self) -> List[str]:
        """验证 CanonicalState 的完整性和一致性

        返回错误列表，空列表表示验证通过。
        """
        errors: List[str] = []

        # 1. 每个 ClassicalState 必须有 Provenance
        for state in self.classical_states:
            if not state.provenance:
                errors.append(f"State {state.state_id} 缺少 Provenance")
            elif not state.provenance.fact_ids and not state.provenance.relation_ids:
                errors.append(f"State {state.state_id} 的 Provenance 缺少来源事实/关系")

        # 2. 整体状态如果不是 UNRESOLVED，必须有原因
        if self.overall_state != OverallState.UNRESOLVED and not self.overall_state_reason:
            errors.append("整体状态不是 UNRESOLVED，但缺少 overall_state_reason")

        # 3. Qualifier 的 target_state 必须存在
        valid_state_ids = {s.state_id for s in self.classical_states}
        for q in self.qualifiers:
            if q.target_state not in valid_state_ids:
                errors.append(f"Qualifier {q.qualifier_id} 的 target_state {q.target_state} 不存在")

        # 4. 禁止评分模型（检查metadata中是否有strength_score等）
        forbidden_keys = {"strength_score", "root_score", "wangshuai_score", "qiangruo_score", "wang_score"}
        for key in forbidden_keys:
            if key in self.metadata:
                errors.append(f"禁止评分模型：metadata 中发现 {key}")
        for state in self.classical_states:
            for key in forbidden_keys:
                if key in state.metadata:
                    errors.append(f"禁止评分模型：State {state.state_id} 的 metadata 中发现 {key}")

        return errors

    # ============================================================
    # 序列化
    # ============================================================

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "state_id": self.state_id,
            "chart_id": self.chart_id,
            "created_at": self.created_at,
            "facts": [f.to_dict() for f in self.facts],
            "relations": [r.to_dict() for r in self.relations],
            "classical_states": [s.to_dict() for s in self.classical_states],
            "qualifiers": [q.to_dict() for q in self.qualifiers],
            "unresolved_reasons": [r.to_dict() for r in self.unresolved_reasons],
            "overall_state": self.overall_state.value,
            "overall_state_reason": self.overall_state_reason,
            "metadata": self.metadata,
            "validation_errors": self.validate(),
        }

    def summary(self) -> dict:
        """生成摘要（不含详细内容，用于快速查看）"""
        return {
            "state_id": self.state_id,
            "chart_id": self.chart_id,
            "facts_count": len(self.facts),
            "relations_count": len(self.relations),
            "classical_states_count": len(self.classical_states),
            "qualifiers_count": len(self.qualifiers),
            "unresolved_reasons_count": len(self.unresolved_reasons),
            "overall_state": self.overall_state.value,
            "domains": list({s.domain for s in self.classical_states}),
            "classics": list({s.classic for s in self.classical_states}),
            "validation_errors": self.validate(),
        }
