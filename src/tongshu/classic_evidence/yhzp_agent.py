"""
渊海子平证据代理
================
负责：基础语义辨证

职责范围：
- 从《渊海子平》原典中提取基础语义证据
- 观察维度：月令重要性 / 格局从月令出 / 十神基础 / 生克制化
- 生成 Assertion Candidate（默认 CANDIDATE 状态）
- 必须带完整 provenance 才能进入候选

禁止：
- 自行决定生产状态
- 跳过 provenance 链条
- 为通过率强行授权
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .base import (
    ClassicEvidenceAgent,
    AssertionProvenance,
    SourceLocator,
    TextLayer,
    AuthorizationLevel,
)


class YHZPEvidenceAgent(ClassicEvidenceAgent):
    """
    渊海子平证据代理
    
    核心辨证目标：基础语义
    关键观察维度：月令、格局基础、十神基础、生克制化
    """
    
    CLASSIC_ID = "yuan_hai_zi_ping"
    CLASSIC_NAME = "渊海子平"
    AGENT_NAME = "渊海子平辨证代理"
    
    # 渊海子平基础证据类型定义
    EVIDENCE_TYPES = {
        "MONTH_COMMAND": "月令重要性证据",
        "PATTERN_FROM_MONTH": "格局从月令出证据",
        "TEN_GOD_BASIC": "十神基础证据",
        "TEN_GOD_AUSPICIOUS": "十神吉凶证据",
        "SHENG_KE_ZHI_HUA": "生克制化证据",
        "XING_CHONG_HE_HAI": "刑冲合害证据",
        "WANG_XIANG_XIU_QIU_SI": "旺相休囚证据",
        "BASIC_SHASHA": "基础神煞证据",
    }
    
    def __init__(self, classics_data_dir: Path, assertion_output_dir: Path):
        super().__init__(classics_data_dir, assertion_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载渊海子平原文数据
        
        TODO: 实现具体加载逻辑
        """
        return []
    
    def extract_month_command_evidence(
        self,
        canonical_state: Dict,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        extraction_quality: float = 0.9,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取月令重要性证据
        
        渊海子平：月令为提纲，格局之本
        """
        if not original_text:
            return self.mark_insufficient_source(
                evidence_type="MONTH_COMMAND",
                observation_dimension="月令",
                notes="渊海子平 — 月令重要性证据：找不到原文",
            )
        
        if source_locator is None:
            source_locator = SourceLocator(
                classic=self.CLASSIC_ID,
                work=self.CLASSIC_NAME,
                chapter="论月令",
                section="",
                paragraph="",
            )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="MONTH_COMMAND",
            observation_dimension="月令",
            relation_semantics="CONTEXT",
            original_text=original_text,
            source_locator=source_locator,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes="渊海子平 — 月令重要性证据",
        )
    
    def extract_pattern_source_evidence(
        self,
        canonical_state: Dict,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        extraction_quality: float = 0.7,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取格局来源证据
        
        渊海子平：格局从月令出
        """
        if not original_text:
            return self.mark_insufficient_source(
                evidence_type="PATTERN_FROM_MONTH",
                observation_dimension="格局来源",
                notes="渊海子平 — 格局从月令出证据：找不到原文",
            )
        
        if source_locator is None:
            source_locator = SourceLocator(
                classic=self.CLASSIC_ID,
                work=self.CLASSIC_NAME,
                chapter="论格局",
                section="",
                paragraph="",
            )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="PATTERN_FROM_MONTH",
            observation_dimension="格局来源",
            relation_semantics="CONTEXT",
            original_text=original_text,
            source_locator=source_locator,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes="渊海子平 — 格局从月令出证据",
        )
    
    def extract_basic_relation_evidence(
        self,
        canonical_state: Dict,
        relation_type: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        extraction_quality: float = 0.6,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取基础关系证据
        
        渊海子平提供基础语义，与子平真诠有重叠
        """
        if not original_text:
            return self.mark_insufficient_source(
                evidence_type=relation_type,
                observation_dimension="基础关系",
                notes=f"渊海子平 — {relation_type}基础证据：找不到原文",
            )
        
        if source_locator is None:
            source_locator = SourceLocator(
                classic=self.CLASSIC_ID,
                work=self.CLASSIC_NAME,
                chapter="基础关系",
                section="",
                paragraph="",
            )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type=relation_type,
            observation_dimension="基础关系",
            relation_semantics="CONTEXT",
            original_text=original_text,
            source_locator=source_locator,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes=f"渊海子平 — {relation_type}基础证据",
        )
