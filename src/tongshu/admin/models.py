"""Assertion Observatory - 数据模型.

9层完整链路:
  1. Input Snapshot      - 输入快照
  2. Engine Raw Result   - 引擎原始计算结果
  3. EngineEvidence      - 统一证据契约(P0)
  4. Semantic Atom       - 语义原子映射(P1)
  5. Canonical Assertion - 规范断言
  6. Assertion Cluster   - 断言聚类
  7. Mapping             - 维度映射
  8. Guidance            - 指引组装
  9. Final Render        - 最终渲染

权限分层:
  RAW ENGINE RESULT  -> READ ONLY
  ENGINE EVIDENCE    -> READ ONLY
  SEMANTIC ATOM      -> EDITABLE
  ASSERTION RULE     -> EDITABLE
  MAPPING            -> EDITABLE
  GUIDANCE TEMPLATE  -> EDITABLE
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# 版本信息
# ═══════════════════════════════════════════════════════════════════

@dataclass
class VersionInfo:
    """一次计算的版本快照. 用于审计'为什么同一个命例今天和上个月不一样'."""
    engine_version: str = "2026.08"
    semantic_version: str = "1.0.0"
    assertion_version: str = "1.0.0"
    mapping_version: str = "1.0.0"
    guidance_version: str = "1.0.0"
    computed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "engine_version": self.engine_version,
            "semantic_version": self.semantic_version,
            "assertion_version": self.assertion_version,
            "mapping_version": self.mapping_version,
            "guidance_version": self.guidance_version,
            "computed_at": self.computed_at,
        }


# ═══════════════════════════════════════════════════════════════════
# Layer 1: Input Snapshot
# ═══════════════════════════════════════════════════════════════════

@dataclass
class InputSnapshot:
    """命例输入快照. 只读, 不可修改."""
    case_id: str
    birth_date: tuple  # (year, month, day, hour)
    gender: str
    analysis_date: Optional[str] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None
    location: Optional[str] = None
    birth_minute: Optional[int] = None
    calendar_system: str = "solar"

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "birth_date": list(self.birth_date),
            "gender": self.gender,
            "analysis_date": self.analysis_date,
            "theme": self.theme,
            "timezone": self.timezone,
            "location": self.location,
            "birth_minute": self.birth_minute,
            "calendar_system": self.calendar_system,
        }


# ═══════════════════════════════════════════════════════════════════
# Layer 2: Engine Raw Result
# ═══════════════════════════════════════════════════════════════════

@dataclass
class EngineRawResult:
    """单个引擎的原始计算结果. 只读, 不可修改."""
    engine: str  # ZI_PING / BLIND_SCHOOL / ZI_WEI / HE_LUO / YI_JING
    status: str  # OK / ERROR / SKIPPED
    data: Any = None  # 原始结果(dict/dataclass)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        d = {"engine": self.engine, "status": self.status}
        if self.data is not None:
            if hasattr(self.data, "to_dict"):
                d["data"] = self.data.to_dict()
            elif isinstance(self.data, (dict, list, str, int, float, bool)) or self.data is None:
                d["data"] = self.data
            else:
                d["data"] = str(self.data)
        if self.error:
            d["error"] = self.error
        return d


# ═══════════════════════════════════════════════════════════════════
# Layer 3-4: Evidence + Semantic Atom
# ═══════════════════════════════════════════════════════════════════

@dataclass
class EvidenceAtomLink:
    """EngineEvidence -> Semantic Atom 的映射链.

    这是Observatory的核心: 管理员可以看到每条证据映射到了哪些语义原子.
    """
    evidence_rule_id: str
    evidence_value: Any
    engine: str
    temporal_scope: str
    mapped_atoms: list[str] = field(default_factory=list)  # atom_id列表
    mapping_method: str = "static"  # static / rule / dynamic
    mapping_notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "evidence_rule_id": self.evidence_rule_id,
            "evidence_value": self.evidence_value,
            "engine": self.engine,
            "temporal_scope": self.temporal_scope,
            "mapped_atoms": self.mapped_atoms,
            "mapping_method": self.mapping_method,
            "mapping_notes": self.mapping_notes,
        }


# ═══════════════════════════════════════════════════════════════════
# Layer 5-9: Assertion / Mapping / Guidance (现有架构桥接)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class AssertionTrace:
    """单条断言的完整追溯链.

    从最终断言一路追溯到原始计算:
      Guidance -> Mapping -> Assertion -> Semantic Atom -> Evidence -> Engine Raw
    """
    assertion_id: str
    domain: str  # CAREER / FINANCE / RELATIONSHIP / ...
    semantic: str  # OUTPUT_ACTIVATION / STRUCTURAL_CHANGE / ...
    direction: str  # supportive / caution / neutral
    intensity: int  # 0-100
    temporal_scope: str
    source_engine: str
    source_rule: str
    # 追溯链
    semantic_atoms: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    mapping_result: Optional[dict] = None
    guidance_items: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "assertion_id": self.assertion_id,
            "domain": self.domain,
            "semantic": self.semantic,
            "direction": self.direction,
            "intensity": self.intensity,
            "temporal_scope": self.temporal_scope,
            "source_engine": self.source_engine,
            "source_rule": self.source_rule,
            "semantic_atoms": self.semantic_atoms,
            "evidence_ids": self.evidence_ids,
            "mapping_result": self.mapping_result,
            "guidance_items": self.guidance_items,
        }


# ═══════════════════════════════════════════════════════════════════
# 完整Case快照
# ═══════════════════════════════════════════════════════════════════

@dataclass
class CaseSnapshot:
    """一个命例的完整9层快照. 这是Observatory的核心数据结构."""
    case_id: str
    version: VersionInfo
    # Layer 1
    input: InputSnapshot
    # Layer 2
    engine_raw: dict[str, EngineRawResult]  # engine_name -> raw_result
    # Layer 3
    evidence: list[dict]  # EngineEvidence.to_dict()列表
    evidence_summary: dict[str, int]  # engine -> count
    # Layer 4
    evidence_atom_links: list[EvidenceAtomLink]
    semantic_atom_summary: dict[str, int]  # atom_id -> occurrence_count
    # Layer 5-9 (从现有架构桥接)
    assertions: list[AssertionTrace]
    guidance: Optional[dict] = None
    final_render: Optional[str] = None
    # 状态
    status: str = "CALCULATED"  # CALCULATED / PARTIAL / ERROR

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "version": self.version.to_dict(),
            "status": self.status,
            "input": self.input.to_dict(),
            "engine_raw": {k: v.to_dict() for k, v in self.engine_raw.items()},
            "evidence": self.evidence,
            "evidence_summary": self.evidence_summary,
            "evidence_atom_links": [l.to_dict() for l in self.evidence_atom_links],
            "semantic_atom_summary": self.semantic_atom_summary,
            "assertions": [a.to_dict() for a in self.assertions],
            "guidance": self.guidance,
            "final_render": self.final_render,
        }


# ═══════════════════════════════════════════════════════════════════
# Playground
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PlaygroundResult:
    """Playground运行结果. CURRENT vs PREVIEW对比, 不写生产数据库."""
    case_id: str
    current: dict  # 当前映射的结果
    preview: dict  # 修改后映射的预览结果
    diff: dict  # 差异
    modified_mapping: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "current": self.current,
            "preview": self.preview,
            "diff": self.diff,
            "modified_mapping": self.modified_mapping,
        }


# ═══════════════════════════════════════════════════════════════════
# Rule Impact
# ═══════════════════════════════════════════════════════════════════

@dataclass
class RuleImpact:
    """规则→结果反向查询. 修改规则前查看影响范围."""
    rule_id: str
    produces_atoms: list[str]
    used_in_cases: list[str]
    produces_assertions: list[dict]  # [{domain, semantic, direction}]
    impact_level: str = "unknown"  # low / medium / high

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "produces_atoms": self.produces_atoms,
            "used_in_cases": self.used_in_cases,
            "produces_assertions": self.produces_assertions,
            "impact_level": self.impact_level,
        }
