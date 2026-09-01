"""
子平真诠证据代理
================
负责：格局成败辨证

职责范围：
- 从《子平真诠》原典中提取格局相关证据
- 观察维度：月令格局 / 用神喜忌 / 成败救应 / 十干得地
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
)


class PZZQEvidenceAgent(ClassicEvidenceAgent):
    """
    子平真诠证据代理
    
    核心辨证目标：格局成败
    关键观察维度：月令、用神、成败、救应
    """
    
    CLASSIC_ID = "ziping_zhenquan"
    CLASSIC_NAME = "子平真诠"
    AGENT_NAME = "子平真诠辨证代理"
    
    # 子平真诠格局证据类型定义
    EVIDENCE_TYPES = {
        "PATTERN_CANDIDATE": "格局候选证据",
        "PATTERN_SUCCESS": "成格证据",
        "PATTERN_DAMAGE": "破格证据",
        "PATTERN_RESCUE": "救应证据",
        "YONG_SHEN": "用神证据",
        "XIANG_SHEN": "相神证据",
        "DE_DI_SUPPORT": "十干得地证据",
        "FIVE_COMBINE_PAIR": "五合配对证据",
    }
    
    def __init__(self, classics_data_dir: Path, assertion_output_dir: Path):
        super().__init__(classics_data_dir, assertion_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载子平真诠原文数据"""
        return []
    
    def extract_pattern_evidence(
        self,
        canonical_state: Dict,
        pattern_type: str,
        pattern_status: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        confidence: float = 0.6
    ) -> AssertionProvenance:
        """
        提取格局证据
        
        子平真诠核心：格局从月令出
        """
        if pattern_status == "SUCCESS":
            evidence_type = "PATTERN_SUCCESS"
            direction = "SUPPORT"
        elif pattern_status == "DAMAGE":
            evidence_type = "PATTERN_DAMAGE"
            direction = "CONSTRAINT"
        elif pattern_status == "RESCUE":
            evidence_type = "PATTERN_RESCUE"
            direction = "MODIFIER"
        else:
            evidence_type = "PATTERN_CANDIDATE"
            direction = "CONTEXT"
        
        source_locator = source_locator or SourceLocator(
            classic=self.CLASSIC_NAME,
            chapter="论用神成败救应",
        )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type=evidence_type,
            observation_dimension=f"格局{pattern_type}",
            direction=direction,
            original_text=original_text or f"格局{pattern_status}",
            source_locator=source_locator,
            confidence=confidence,
            notes=f"子平真诠 — {pattern_type}{pattern_status}证据",
        )
    
    def extract_yongshen_evidence(
        self,
        canonical_state: Dict,
        yongshen_type: str,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        confidence: float = 0.7
    ) -> AssertionProvenance:
        """
        提取用神证据
        
        子平真诠对用神有明确论述，但需要逐条验证
        """
        source_locator = source_locator or SourceLocator(
            classic=self.CLASSIC_NAME,
            chapter="论用神",
        )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="YONG_SHEN",
            observation_dimension="用神",
            direction="SUPPORT",
            original_text=original_text or f"{yongshen_type}用神",
            source_locator=source_locator,
            confidence=confidence,
            notes=f"子平真诠 — {yongshen_type}用神证据",
        )
    
    def extract_de_di_evidence(
        self,
        canonical_state: Dict,
        original_text: str = "",
        source_locator: Optional[SourceLocator] = None,
        confidence: float = 0.9
    ) -> AssertionProvenance:
        """
        提取十干得地证据
        
        子平真诠有明确论述（已验证 AUTHORIZED）
        """
        source_locator = source_locator or SourceLocator(
            classic=self.CLASSIC_NAME,
            chapter="论阴阳生死",
        )
        
        return self.extract_assertion_candidate(
            canonical_state=canonical_state,
            evidence_type="DE_DI_SUPPORT",
            observation_dimension="十干得地",
            direction="SUPPORT",
            original_text=original_text or "人之日主，不必生逢禄旺，即月令休囚，而年日时中，得长禄旺，便不为弱",
            source_locator=source_locator,
            confidence=confidence,
            notes="子平真诠 — 十干得地证据（已授权）",
        )
