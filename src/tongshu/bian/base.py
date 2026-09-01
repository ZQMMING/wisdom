"""
Bian 模块基础框架
==================
定义辨证代理的基类和数据结构

核心原则：
- Evidence ≠ Production Assertion
- 每条 Evidence 必须有完整 provenance
- 五个 Agent 互补，不比较、不投票
- confidence ≠ authorization ≠ production_status
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


class EvidenceDirection(str, Enum):
    """证据关系方向 — Evidence 层描述原典关系，不是 Signal direction"""
    SUPPORT = "SUPPORT"           # 支持/生成关系
    CONSTRAINT = "CONSTRAINT"     # 制约/克制关系
    MODIFIER = "MODIFIER"         # 修饰/调候关系
    CONTEXT = "CONTEXT"           # 上下文/中性关系
    NEUTRAL = "NEUTRAL"           # 无明确关系


class AuthorizationLevel(str, Enum):
    """授权级别 — 原典授权强度，与 confidence 完全分离"""
    NONE = "NONE"                      # 未授权
    PARTIAL = "PARTIAL"                # 部分授权（仅限定性描述）
    AUTHORIZED = "AUTHORIZED"          # 已授权（可进入候选）
    INSUFFICIENT_SOURCE = "INSUFFICIENT_SOURCE"  # 找不到原文


class VerificationStatus(str, Enum):
    """验证状态 — 由 CrossValidator 设置，Agent 不得自行提升"""
    UNVERIFIED = "UNVERIFIED"
    EXACT_MATCH = "EXACT_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"


class CanonicalSource(str, Enum):
    """经典来源"""
    DTS = "di_tian_sui"           # 滴天髓
    PZZQ = "ziping_zhenquan"      # 子平真诠
    QTBJ = "qiong_tong_bao_jian"  # 穷通宝鉴
    SMTH = "san_ming_tong_hui"    # 三命通会
    YHZP = "yuan_hai_zi_ping"     # 渊海子平


# ============================================================
# 数据结构
# ============================================================


@dataclass(frozen=True)
class SourceLocator:
    """
    证据源定位器 — 必须完整，缺一不可
    
    字段说明：
    - classic: 经典ID（如 di_tian_sui）
    - work: 经典名称（如 滴天髓）
    - chapter: 篇章（如 通神论·衰旺）
    - section: 段落编号（如 "第123段"）
    - passage_id: 权威段落ID（如 DTS_0001）
    - source_hash: 原文 sha256（防证据漂移）
    """
    classic: str
    work: str
    chapter: str
    section: str = ""
    passage_id: str = ""
    source_hash: str = ""
    
    def validate(self) -> List[str]:
        """验证 source_locator 完整性"""
        errors = []
        if not self.classic:
            errors.append("Missing required field: classic")
        if not self.work:
            errors.append("Missing required field: work")
        if not self.chapter:
            errors.append("Missing required field: chapter")
        if not self.passage_id:
            errors.append("Missing required field: passage_id")
        if not self.source_hash:
            errors.append("Missing required field: source_hash")
        return errors
    
    def to_dict(self) -> dict:
        return {
            "classic": self.classic,
            "work": self.work,
            "chapter": self.chapter,
            "section": self.section,
            "passage_id": self.passage_id,
            "source_hash": self.source_hash,
        }


@dataclass(frozen=True)
class EvidenceText:
    """
    原文证据 — 必须包含原文和上下文
    
    字段说明：
    - original_text: 原文（必填，不能是 fallback）
    - text_layer: 文本层次（原文/原注/后世注释）
    - context_before: 前文（可选）
    - context_after: 后文（可选）
    """
    original_text: str
    text_layer: str = "ORIGINAL"  # ORIGINAL / COMMENTARY / MODERN
    context_before: str = ""
    context_after: str = ""
    
    def validate(self) -> List[str]:
        errors = []
        if not self.original_text:
            errors.append("original_text is empty")
        if self.text_layer not in ["ORIGINAL", "COMMENTARY", "MODERN"]:
            errors.append(f"Invalid text_layer: {self.text_layer}")
        return errors


@dataclass(frozen=True)
class Evidence:
    """
    辨证证据 — 单个证据项
    
    核心原则：
    - Evidence ≠ Assertion
    - Evidence 只是原典事实记录
    - 是否进入候选由验证层决定
    """
    evidence_id: str
    classic_id: str
    evidence_type: str
    observation_dimension: str
    relation_semantics: str  # 原典关系语义，不是 direction
    original_text: str
    source_locator: SourceLocator
    evidence_text: EvidenceText
    canonical_state: Dict
    authorization_level: AuthorizationLevel
    verification_status: VerificationStatus
    extraction_quality: float  # 重命名自 confidence
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def validate(self) -> List[str]:
        """验证 Evidence 完整性"""
        errors = []
        errors.extend(self.source_locator.validate())
        errors.extend(self.evidence_text.validate())
        if not self.evidence_id:
            errors.append("evidence_id is empty")
        if not self.classic_id:
            errors.append("classic_id is empty")
        if not self.evidence_type:
            errors.append("evidence_type is empty")
        if not self.observation_dimension:
            errors.append("observation_dimension is empty")
        if not self.authorization_level:
            errors.append("authorization_level is empty")
        # 禁止使用 direction 字段（与 AssertionV2 冲突）
        if hasattr(self, 'direction') and self.direction:
            errors.append("Evidence must not have 'direction' field")
        return errors


# ============================================================
# 基类
# ============================================================


class BianAgent:
    """
    辨证代理基类
    
    职责：
    - 从原典检索证据
    - 建立 provenance 链条
    - 生成 Evidence Candidate
    - 不做生产裁决
    
    禁止：
    - 自行决定生产状态
    - 跳过 provenance 链条
    - 为通过率强行授权
    """
    
    CLASSIC_ID: str = ""
    CLASSIC_NAME: str = ""
    EVIDENCE_TYPES: Dict[str, str] = {}
    
    def __init__(
        self,
        classics_data_dir: Path,
        evidence_output_dir: Path,
        enable_validation: bool = True,
    ):
        self.classics_data_dir = Path(classics_data_dir)
        self.evidence_output_dir = Path(evidence_output_dir)
        self.enable_validation = enable_validation
        self._entries: List[Dict] = []
        self._passage_index: Dict[str, List[Dict]] = {}
        self._validated = False
    
    def _load_classic_entries(self) -> List[Dict]:
        """加载本经典原文数据（子类实现）"""
        raise NotImplementedError
    
    def _build_passage_index(self) -> None:
        """构建段落索引（passage_id -> entries）"""
        self._passage_index = {}
        for entry in self._load_classic_entries():
            pid = entry.get("passage_id", "")
            if pid:
                self._passage_index.setdefault(pid, []).append(entry)
        self._validated = True
    
    def get_entry_by_passage_id(self, passage_id: str) -> Optional[List[Dict]]:
        """按 passage_id 获取条目"""
        return self._passage_index.get(passage_id)
    
    def search_entries(
        self,
        keywords: List[str],
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """关键词搜索"""
        results = []
        for entry in self._load_classic_entries():
            if category and entry.get("category") != category:
                continue
            text = entry.get("original_text", "")
            if any(kw in text for kw in keywords):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
    
    def extract_evidence(
        self,
        canonical_state: Dict,
        evidence_type: str,
        relation_semantics: str,
        original_text: str,
        source_locator: SourceLocator,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
        context_before: str = "",
        context_after: str = "",
        extraction_quality: float = 0.7,
        notes: str = "",
    ) -> Evidence:
        """
        提取证据 — 核心方法
        
        参数：
        - original_text: 必须是非空的原文，不能是 fallback
        - source_locator: 必须完整，包含 passage_id 和 source_hash
        - authorization_level: 必须显式指定，默认 PARTIAL
        - extraction_quality: 证据提取质量（0-1），与 authorization 分离
        """
        # 验证 original_text 不为空
        if not original_text:
            raise ValueError(
                f"{self.CLASSIC_NAME}: original_text 不能为空。"
                f"找不到原文时，应返回 INSUFFICIENT_SOURCE，不能生成 Evidence。"
            )
        
        # 验证 source_locator 完整性
        locator_errors = source_locator.validate()
        if locator_errors:
            raise ValueError(
                f"{self.CLASSIC_NAME}: source_locator 不完整: {locator_errors}"
            )
        
        # 创建 EvidenceText
        evidence_text = EvidenceText(
            original_text=original_text,
            text_layer="ORIGINAL",
            context_before=context_before,
            context_after=context_after,
        )
        
        # 生成 evidence_id
        evidence_id = f"E-{self.CLASSIC_ID}-{evidence_type}-{source_locator.passage_id}"
        
        # 创建 Evidence
        evidence = Evidence(
            evidence_id=evidence_id,
            classic_id=self.CLASSIC_ID,
            evidence_type=evidence_type,
            observation_dimension="",  # 由子类设置
            relation_semantics=relation_semantics,
            original_text=original_text,
            source_locator=source_locator,
            evidence_text=evidence_text,
            canonical_state=canonical_state,
            authorization_level=authorization_level,
            verification_status=VerificationStatus.UNVERIFIED,
            extraction_quality=extraction_quality,
            notes=notes,
        )
        
        # 验证
        validation_errors = evidence.validate()
        if validation_errors:
            raise ValueError(
                f"{self.CLASSIC_NAME}: Evidence 验证失败: {validation_errors}"
            )
        
        return evidence
    
    def save_evidence(self, evidence: Evidence) -> Path:
        """保存证据到输出目录"""
        output_dir = self.evidence_output_dir / self.CLASSIC_ID
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{evidence.evidence_id}.json"
        import json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(evidence.to_dict() if hasattr(evidence, 'to_dict') else {
                "evidence_id": evidence.evidence_id,
                "classic_id": evidence.classic_id,
                "evidence_type": evidence.evidence_type,
                "original_text": evidence.original_text,
                "source_locator": evidence.source_locator.to_dict(),
                "authorization_level": evidence.authorization_level.value,
                "verification_status": evidence.verification_status.value,
                "extraction_quality": evidence.extraction_quality,
                "notes": evidence.notes,
            }, f, ensure_ascii=False, indent=2)
        return output_path
    
    def mark_insufficient_source(self, canonical_state: Dict, evidence_type: str, notes: str = "") -> Evidence:
        """
        标记为INSUFFICIENT_SOURCE — 当找不到原文时调用
        
        这是唯一的"找不到原文"处理方式，不能跳过
        """
        source_locator = SourceLocator(
            classic=self.CLASSIC_ID,
            work=self.CLASSIC_NAME,
            chapter="",
            section="",
            passage_id="",
            source_hash="",
        )
        evidence_text = EvidenceText(
            original_text="",
            text_layer="ORIGINAL",
        )
        return Evidence(
            evidence_id=f"E-{self.CLASSIC_ID}-{evidence_type}-INSUFFICIENT",
            classic_id=self.CLASSIC_ID,
            evidence_type=evidence_type,
            observation_dimension="",
            relation_semantics="NEUTRAL",
            original_text="",
            source_locator=source_locator,
            evidence_text=evidence_text,
            canonical_state=canonical_state,
            authorization_level=AuthorizationLevel.INSUFFICIENT_SOURCE,
            verification_status=VerificationStatus.NOT_FOUND,
            extraction_quality=0.0,
            notes=notes or "找不到原文，标记为INSUFFICIENT_SOURCE",
        )


# ============================================================
# 工具函数
# ============================================================


def get_classic_short(classic_id: str) -> str:
    """经典ID → 简称"""
    mapping = {
        "di_tian_sui": "DTS",
        "ziping_zhenquan": "PZZQ",
        "qiong_tong_bao_jian": "QTBJ",
        "san_ming_tong_hui": "SMTH",
        "yuan_hai_zi_ping": "YHZP",
    }
    return mapping.get(classic_id, classic_id.upper())


def get_classic_full(classic_id: str) -> str:
    """经典ID → 全称"""
    mapping = {
        "di_tian_sui": "滴天髓",
        "ziping_zhenquan": "子平真诠",
        "qiong_tong_bao_jian": "穷通宝鉴",
        "san_ming_tong_hui": "三命通会",
        "yuan_hai_zi_ping": "渊海子平",
    }
    return mapping.get(classic_id, classic_id)
