"""
滴天髓证据代理
==============
负责：旺衰气势辨证

职责范围：
- 从《滴天髓》原典中提取旺衰相关证据
- 观察维度：得令 / 得地 / 得势 / 受制 / 泄耗 / 气势流通
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
    EvidenceText,
    TextLayer,
    AuthorizationLevel,
)


class DTSEvidenceAgent(ClassicEvidenceAgent):
    """
    滴天髓证据代理
    
    核心辨证目标：日主旺衰气势
    关键观察维度：得令、得地、得势、受制、泄耗
    """
    
    CLASSIC_ID = "di_tian_sui"
    CLASSIC_NAME = "滴天髓"
    AGENT_NAME = "滴天髓辨证代理"
    
    # 滴天髓旺衰证据类型定义
    EVIDENCE_TYPES = {
        "SEASONAL_SUPPORT": "得令证据",
        "ROOT_PRESENT": "得地证据（根气存在）",
        "MAIN_QI_ROOT": "本气根证据",
        "RESOURCE_SUPPORT": "印生身证据",
        "PEER_SUPPORT": "比劫帮身证据",
        "OFFICER_CONTROL": "官杀制约证据",
        "OUTPUT_DRAIN": "食伤泄身证据",
        "WEALTH_DRAIN": "财星耗身证据",
        "FLOW_SMOOTH": "气势流通证据",
        "FLOW_BLOCKED": "气势阻滞证据",
    }
    
    def __init__(self, classics_data_dir: Path, assertion_output_dir: Path):
        super().__init__(classics_data_dir, assertion_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载滴天髓原文数据
        
        TODO: 实现具体加载逻辑，从 data/classics/original/DTS_滴天髓_段落数据.json 读取
        """
        return []
    
    def extract_seasonal_support(
        self,
        canonical_state: Dict,
        original_text: str,
        source_locator: SourceLocator,
        context_before: str = "",
        context_after: str = "",
        extraction_quality: float = 0.7,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取得令证据
        
        滴天髓·通神论·衰旺：
        "得令者旺，失令者衰"
        """
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="SEASONAL_SUPPORT",
            observation_dimension="得令",
            relation_semantics="SUPPORT",  # 原典关系语义，不是 direction
            original_text=original_text,
            source_locator=source_locator,
            context_before=context_before,
            context_after=context_after,
            text_layer=TextLayer.ORIGINAL.value,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes="滴天髓·通神论·衰旺 — 得令证据",
        )
    
    def extract_root_evidence(
        self,
        canonical_state: Dict,
        root_type: str = "MAIN_QI",
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        context_before: str = "",
        context_after: str = "",
        extraction_quality: float = 0.8,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取得地证据

        注意：original_text 不能为空，找不到原文时应调用 mark_insufficient_source()
        """
        if not original_text:
            return self.mark_insufficient_source(
                evidence_type="ROOT_PRESENT",
                observation_dimension="得地",
                notes=f"滴天髓·通神论·衰旺 — {root_type}根气证据：找不到原文",
            )
        
        if source_locator is None:
            source_locator = SourceLocator(
                classic=self.CLASSIC_ID,
                work=self.CLASSIC_NAME,
                chapter="通神论·衰旺",
                section="",
                paragraph="",
            )
        
        evidence_type = "ROOT_PRESENT" if root_type == "ANY" else "MAIN_QI_ROOT"
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type=evidence_type,
            observation_dimension="得地",
            relation_semantics="SUPPORT",
            original_text=original_text,
            source_locator=source_locator,
            context_before=context_before,
            context_after=context_after,
            text_layer=TextLayer.ORIGINAL.value,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes=f"滴天髓·通神论·衰旺 — {root_type}根气证据",
        )
    
    def extract_flow_evidence(
        self,
        canonical_state: Dict,
        flow_status: str = "SMOOTH",
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        extraction_quality: float = 0.5,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL,
    ) -> AssertionProvenance:
        """
        提取气势流通证据
        
        滴天髓对气势流通有论述，但需要深入原典验证具体规则
        """
        if not original_text:
            return self.mark_insufficient_source(
                evidence_type="FLOW_SMOOTH",
                observation_dimension="气势流通",
                notes="滴天髓·通神论 — 气势流通证据：待深入原典验证",
            )
        
        if source_locator is None:
            source_locator = SourceLocator(
                classic=self.CLASSIC_ID,
                work=self.CLASSIC_NAME,
                chapter="通神论·衰旺",
                section="",
                paragraph="",
            )
        
        evidence_type = "FLOW_SMOOTH" if flow_status == "SMOOTH" else "FLOW_BLOCKED"
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type=evidence_type,
            observation_dimension="气势流通",
            relation_semantics="CONTEXT",
            original_text=original_text,
            source_locator=source_locator,
            text_layer=TextLayer.ORIGINAL.value,
            extraction_quality=extraction_quality,
            authorization_level=authorization_level,
            notes="滴天髓·通神论 — 气势流通证据（待深入原典验证）",
        )
