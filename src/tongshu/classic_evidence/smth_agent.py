"""
三命通会证据代理
================
负责：关系转化辨证

职责范围：
- 从《三命通会》原典中提取关系相关证据
- 观察维度：刑冲合害 / 神煞 / 生克制化
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


class SMTHEvidenceAgent(ClassicEvidenceAgent):
    """
    三命通会证据代理
    
    核心辨证目标：关系转化
    关键观察维度：刑冲合害、神煞、生克制化
    """
    
    CLASSIC_ID = "san_ming_tong_hui"
    CLASSIC_NAME = "三命通会"
    AGENT_NAME = "三命通会辨证代理"
    
    # 三命通会关系证据类型定义
    EVIDENCE_TYPES = {
        "GENERATES": "相生证据",
        "CONTROLS": "相克证据",
        "TRANSFORMATION": "制化证据",
        "CLASH": "相冲证据",
        "COMBINE": "相合证据",
        "HARM": "相害证据",
        "PUNISH": "相刑证据",
        "TIANYI_GUIREN": "天乙贵人证据",
        "TEN_GOD_BASIC": "十神基础证据",
    }
    
    def __init__(self, classics_data_dir: Path, assertion_output_dir: Path):
        super().__init__(classics_data_dir, assertion_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载三命通会原文数据
        
        TODO: 实现具体加载逻辑
        """
        return []
    
    def extract_relation_evidence(
        self,
        canonical_state: Dict,
        relation_type: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        extraction_quality: float = 0.7,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取基础关系证据
        
        三命通会内容极其丰富，是资料汇编性质，需要逐条筛选
        """
        if not original_text:
            return self.mark_insufficient_source(
                canonical_state=canonical_state,
                evidence_type=relation_type,
                observation_dimension="基础关系",
                notes=f"三命通会 — {relation_type}关系证据：找不到原文",
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
            notes=f"三命通会 — {relation_type}关系证据",
        )
    
    def extract_shensha_evidence(
        self,
        canonical_state: Dict,
        shensha_type: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        extraction_quality: float = 0.4,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取神煞证据
        
        三命通会神煞数量众多，需要逐条验证是否进入辨证
        """
        if not original_text:
            return self.mark_insufficient_source(
                canonical_state=canonical_state,
                evidence_type=shensha_type,
                observation_dimension="神煞",
                notes=f"三命通会 — {shensha_type}神煞证据：需逐条验证",
            )
        
        if source_locator is None:
            source_locator = SourceLocator(
                classic=self.CLASSIC_ID,
                work=self.CLASSIC_NAME,
                chapter="神煞",
                section="",
                paragraph="",
            )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type=shensha_type,
            observation_dimension="神煞",
            relation_semantics="MODIFIER",
            original_text=original_text,
            source_locator=source_locator,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes=f"三命通会 — {shensha_type}神煞证据（需逐条验证）",
        )
    
    def extract_transformation_evidence(
        self,
        canonical_state: Dict,
        transformation_type: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        extraction_quality: float = 0.6,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取制化证据
        
        生克制化组合关系
        """
        if not original_text:
            return self.mark_insufficient_source(
                canonical_state=canonical_state,
                evidence_type="TRANSFORMATION",
                observation_dimension="制化",
                notes=f"三命通会 — {transformation_type}制化证据：找不到原文",
            )
        
        if source_locator is None:
            source_locator = SourceLocator(
                classic=self.CLASSIC_ID,
                work=self.CLASSIC_NAME,
                chapter="生克制化",
                section="",
                paragraph="",
            )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="TRANSFORMATION",
            observation_dimension="制化",
            relation_semantics="MODIFIER",
            original_text=original_text,
            source_locator=source_locator,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes=f"三命通会 — {transformation_type}制化证据",
        )
