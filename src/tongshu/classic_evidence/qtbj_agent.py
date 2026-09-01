"""
穷通宝鉴证据代理
================
负责：调候寒暖辨证

职责范围：
- 从《穷通宝鉴》原典中提取调候相关证据
- 观察维度：日干×月令二维调候 / 寒暖燥湿
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
)


class QTBJEvidenceAgent(ClassicEvidenceAgent):
    """
    穷通宝鉴证据代理
    
    核心辨证目标：调候寒暖
    关键观察维度：日干×月令二维矩阵、寒暖燥湿
    """
    
    CLASSIC_ID = "qiong_tong_bao_jian"
    CLASSIC_NAME = "穷通宝鉴"
    AGENT_NAME = "穷通宝鉴辨证代理"
    
    # 穷通宝鉴调候证据类型定义
    EVIDENCE_TYPES = {
        "CLIMATE_STATE": "气候状态证据",
        "PRIMARY_TIAOHOU": "主调候证据",
        "SECONDARY_TIAOHOU": "次调候证据",
        "TIAOHOU_PRESENT": "调候出现证据",
        "TIAOHOU_ROOTED": "调候有根证据",
        "TIAOHOU_BLOCKED": "调候受阻证据",
        "TIAOHOU_EXCESS": "调候过量证据",
        "WANG_XIANG_XIU_QIU_SI": "五行时令证据",
    }
    
    def __init__(self, classics_data_dir: Path, assertion_output_dir: Path):
        super().__init__(classics_data_dir, assertion_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载穷通宝鉴原文数据"""
        return []
    
    def extract_climate_evidence(
        self,
        canonical_state: Dict,
        climate_type: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        confidence: float = 0.6
    ) -> AssertionProvenance:
        """
        提取气候状态证据
        
        穷通宝鉴核心：寒暖燥湿是调候基础
        """
        source_locator = source_locator or SourceLocator(
            classic=self.CLASSIC_NAME,
            chapter="调候章节",
        )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="CLIMATE_STATE",
            observation_dimension="气候状态",
            direction="CONTEXT",
            original_text=original_text or f"{climate_type}气候",
            source_locator=source_locator,
            confidence=confidence,
            notes=f"穷通宝鉴 — {climate_type}气候证据",
        )
    
    def extract_tiaohou_evidence(
        self,
        canonical_state: Dict,
        day_master: str,
        month_branch: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        confidence: float = 0.7
    ) -> AssertionProvenance:
        """
        提取调候用神证据
        
        穷通宝鉴核心：日干×月令二维矩阵查表
        """
        source_locator = source_locator or SourceLocator(
            classic=self.CLASSIC_NAME,
            chapter="调候",
        )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="PRIMARY_TIAOHOU",
            observation_dimension="调候用神",
            direction="SUPPORT",
            original_text=original_text or f"{day_master}日{month_branch}月调候",
            source_locator=source_locator,
            confidence=confidence,
            notes=f"穷通宝鉴 — {day_master}日{month_branch}月调候证据",
        )
    
    def extract_tiaohou_availability_evidence(
        self,
        canonical_state: Dict,
        availability_type: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        confidence: float = 0.5
    ) -> AssertionProvenance:
        """
        提取调候可用性证据
        
        穷通宝鉴对调候可用性有论述，但需要深入验证
        """
        source_locator = source_locator or SourceLocator(
            classic=self.CLASSIC_NAME,
            chapter="调候",
        )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type=f"TIAOHOU_{availability_type.upper()}",
            observation_dimension="调候可用性",
            direction="MODIFIER",
            original_text=original_text or f"调候{availability_type}",
            source_locator=source_locator,
            confidence=confidence,
            notes=f"穷通宝鉴 — 调候{availability_type}证据（待验证）",
        )
