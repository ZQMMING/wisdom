"""
Classic Evidence 模块基础框架
==============================
定义五经证据代理的基类和数据结构

与 bian/base.py 的区别：
- bian/ 是旧的辨证代理（用于内部推理）
- classic_evidence/ 是新的证据代理（用于生产资产生成）
- 两者共享相同的数据结构，但使用场景不同
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


# ============================================================
# 枚举定义
# ============================================================


class TextLayer(str, Enum):
    """文本层次"""
    ORIGINAL = "ORIGINAL"           # 原文
    COMMENTARY = "COMMENTARY"       # 原注
    MODERN = "MODERN"               # 现代注释


class AuthorizationLevel(str, Enum):
    """授权级别"""
    NONE = "NONE"
    PARTIAL = "PARTIAL"
    AUTHORIZED = "AUTHORIZED"
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"


class ProductionStatus(str, Enum):
    """生产状态 — Agent 不得自行提升"""
    CANDIDATE = "CANDIDATE"
    AUDIT_PENDING = "AUDIT_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ============================================================
# 数据结构
# ============================================================


@dataclass(frozen=True)
class SourceLocator:
    """
    证据源定位器 — 必须完整
    
    必填字段：classic, work, chapter, section, paragraph
    """
    classic: str
    work: str
    chapter: str
    section: str = ""
    paragraph: str = ""
    passage_id: str = ""
    source_hash: str = ""
    
    def validate(self) -> List[str]:
        errors = []
        for field_name in ["classic", "work", "chapter", "section", "paragraph"]:
            if not getattr(self, field_name):
                errors.append(f"Missing required field: {field_name}")
        return errors
    
    def to_dict(self) -> dict:
        return {
            "classic": self.classic,
            "work": self.work,
            "chapter": self.chapter,
            "section": self.section,
            "paragraph": self.paragraph,
            "passage_id": self.passage_id,
            "source_hash": self.source_hash,
        }


@dataclass(frozen=True)
class EvidenceText:
    """原文证据"""
    original_text: str
    text_layer: str = "ORIGINAL"
    context_before: str = ""
    context_after: str = ""
    
    def validate(self) -> List[str]:
        errors = []
        if not self.original_text:
            errors.append("original_text is empty")
        return errors


@dataclass(frozen=True)
class SemanticParse:
    """语义解析"""
    observation_dimension: str
    evidence_type: str
    relation_semantics: str  # 原典关系语义
    mapping_to_canonical: Dict = field(default_factory=dict)


@dataclass(frozen=True)
class AssertionProvenance:
    """
    断言溯源链 — 每条 Assertion 必须带完整 provenance
    """
    assertion_id: str
    source_system: str
    source_work: str
    chapter: str
    source_locator: SourceLocator
    evidence_text: EvidenceText
    semantic_parse: SemanticParse
    feature_mapping: Dict = field(default_factory=dict)
    trigger: str = ""
    judgment: str = ""
    modern_semantic: str = ""
    extraction_quality: float = 0.0  # 重命名自 confidence
    authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    production_status: ProductionStatus = ProductionStatus.CANDIDATE
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def validate(self) -> List[str]:
        errors = []
        errors.extend(self.source_locator.validate())
        errors.extend(self.evidence_text.validate())
        if not self.assertion_id:
            errors.append("assertion_id is empty")
        if not self.source_system:
            errors.append("source_system is empty")
        # 禁止 direction 字段
        if hasattr(self, 'direction') and getattr(self, 'direction'):
            errors.append("AssertionProvenance must not have 'direction' field")
        # production_status 不得由 Agent 自行提升
        if self.production_status == ProductionStatus.APPROVED:
            errors.append("production_status cannot be APPROVED by Agent")
        return errors


# ============================================================
# 基类
# ============================================================


class ClassicEvidenceAgent:
    """
    经典证据代理基类
    
    职责：
    - 原典证据提取
    - 规则提炼
    - 语义解析
    - 生成 Assertion Candidate
    
    禁止：
    - 自行入库生产
    - 跳过 provenance 链条
    - 为通过率强行授权
    """
    
    CLASSIC_ID: str = ""
    CLASSIC_NAME: str = ""
    AGENT_NAME: str = ""
    EVIDENCE_TYPES: Dict[str, str] = {}
    
    def __init__(self, classics_data_dir: Path, assertion_output_dir: Path):
        self.classics_data_dir = Path(classics_data_dir)
        self.assertion_output_dir = Path(assertion_output_dir)
        self._entries: List[Dict] = []
    
    def _load_classic_entries(self) -> List[Dict]:
        """加载原典数据（子类实现）"""
        raise NotImplementedError
    
    def extract_assertion_candidate(
        self,
        canonical_state: Dict,
        evidence_type: str,
        observation_dimension: str,
        relation_semantics: str,  # 重命名自 direction
        original_text: str,
        source_locator: SourceLocator,
        context_before: str = "",
        context_after: str = "",
        text_layer: str = TextLayer.ORIGINAL.value,
        extraction_quality: float = 0.7,  # 重命名自 confidence
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
        notes: str = "",
    ) -> AssertionProvenance:
        """
        生成 Assertion Candidate
        
        参数：
        - original_text: 必须是非空原文
        - source_locator: 必须完整
        - authorization_level: 必须显式指定
        - extraction_quality: 证据提取质量（与 authorization 分离）
        """
        # 验证 original_text
        if not original_text:
            raise ValueError(
                f"{self.CLASSIC_NAME}: original_text 不能为空。"
                f"找不到原文时，应返回 INSUFFICIENT_SOURCE。"
            )
        
        # 验证 source_locator
        locator_errors = source_locator.validate()
        if locator_errors:
            raise ValueError(
                f"{self.CLASSIC_NAME}: source_locator 不完整: {locator_errors}"
            )
        
        # 创建 EvidenceText
        evidence_text = EvidenceText(
            original_text=original_text,
            text_layer=text_layer,
            context_before=context_before,
            context_after=context_after,
        )
        
        # 创建 SemanticParse
        semantic_parse = SemanticParse(
            observation_dimension=observation_dimension,
            evidence_type=evidence_type,
            relation_semantics=relation_semantics,
            mapping_to_canonical={},
        )
        
        # 生成 assertion_id
        assertion_id = f"A-{self.CLASSIC_ID}-{evidence_type}-{source_locator.passage_id}"
        
        # 创建 AssertionProvenance
        assertion = AssertionProvenance(
            assertion_id=assertion_id,
            source_system=self.AGENT_NAME,
            source_work=self.CLASSIC_NAME,
            chapter=source_locator.chapter,
            source_locator=source_locator,
            evidence_text=evidence_text,
            semantic_parse=semantic_parse,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            production_status=ProductionStatus.CANDIDATE,
            notes=notes,
        )
        
        # 验证
        validation_errors = assertion.validate()
        if validation_errors:
            raise ValueError(
                f"{self.CLASSIC_NAME}: AssertionProvenance 验证失败: {validation_errors}"
            )
        
        return assertion
    
    def mark_insufficient_source(
        self,
        canonical_state: Dict,
        evidence_type: str,
        observation_dimension: str,
        notes: str = "",
    ) -> AssertionProvenance:
        """标记为INSUFFICIENT_SOURCE"""
        source_locator = SourceLocator(
            classic=self.CLASSIC_ID,
            work=self.CLASSIC_NAME,
            chapter="",
            section="",
            paragraph="",
            passage_id="",
            source_hash="",
        )
        evidence_text = EvidenceText(
            original_text="",
            text_layer=TextLayer.ORIGINAL.value,
        )
        semantic_parse = SemanticParse(
            observation_dimension=observation_dimension,
            evidence_type=evidence_type,
            relation_semantics="NEUTRAL",
        )
        return AssertionProvenance(
            assertion_id=f"A-{self.CLASSIC_ID}-{evidence_type}-INSUFFICIENT",
            source_system=self.AGENT_NAME,
            source_work=self.CLASSIC_NAME,
            chapter="",
            source_locator=source_locator,
            evidence_text=evidence_text,
            semantic_parse=semantic_parse,
            extraction_quality=0.0,
            authorization_level=AuthorizationLevel.INSUFFICIENT_SOURCE,
            production_status=ProductionStatus.CANDIDATE,
            notes=notes or "找不到原文，标记为INSUFFICIENT_SOURCE",
        )
    
    def save_assertion(self, assertion: AssertionProvenance) -> Path:
        """保存 Assertion 到输出目录"""
        output_dir = self.assertion_output_dir / self.CLASSIC_ID
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{assertion.assertion_id}.json"
        import json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "assertion_id": assertion.assertion_id,
                "source_system": assertion.source_system,
                "source_work": assertion.source_work,
                "chapter": assertion.chapter,
                "source_locator": assertion.source_locator.to_dict(),
                "evidence_text": {
                    "original_text": assertion.evidence_text.original_text,
                    "text_layer": assertion.evidence_text.text_layer,
                },
                "semantic_parse": {
                    "observation_dimension": assertion.semantic_parse.observation_dimension,
                    "evidence_type": assertion.semantic_parse.evidence_type,
                    "relation_semantics": assertion.semantic_parse.relation_semantics,
                },
                "extraction_quality": assertion.extraction_quality,
                "authorization_level": assertion.authorization_level.value,
                "production_status": assertion.production_status.value,
                "notes": assertion.notes,
            }, f, ensure_ascii=False, indent=2)
        return output_path


# ============================================================
# 工具函数
# ============================================================


def get_classic_short(classic_id: str) -> str:
    mapping = {
        "di_tian_sui": "DTS",
        "ziping_zhenquan": "PZZQ",
        "qiong_tong_bao_jian": "QTBJ",
        "san_ming_tong_hui": "SMTH",
        "yuan_hai_zi_ping": "YHZP",
    }
    return mapping.get(classic_id, classic_id.upper())


def get_classic_full(classic_id: str) -> str:
    mapping = {
        "di_tian_sui": "滴天髓",
        "ziping_zhenquan": "子平真诠",
        "qiong_tong_bao_jian": "穷通宝鉴",
        "san_ming_tong_hui": "三命通会",
        "yuan_hai_zi_ping": "渊海子平",
    }
    return mapping.get(classic_id, classic_id)
