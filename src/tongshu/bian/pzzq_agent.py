"""
PZZQ 辨证代理（子平真诠）
========================
负责：格局成败辨证
核心观察维度：月令格局 / 用神喜忌 / 成败救应 / 十干得地
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .base import (
    BianAgent,
    Evidence,
    EvidenceDirection,
    AuthorizationLevel,
)


class PZZQBianAgent(BianAgent):
    """
    子平真诠辨证代理
    
    核心辨证目标：格局成败
    关键观察维度：月令、用神、成败、救应
    """
    
    CLASSIC_ID = "ziping_zhenquan"
    CLASSIC_NAME = "子平真诠"
    
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
    
    def __init__(self, classics_data_dir: Path, evidence_output_dir: Path):
        super().__init__(classics_data_dir, evidence_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载子平真诠原文数据"""
        return []
    
    def extract_pattern_evidence(
        self,
        canonical_state: Dict,
        pattern_type: str,
        pattern_status: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.NOT_AUTHORIZED
    ) -> Evidence:
        """
        提取格局证据
        
        子平真诠核心：格局从月令出
        """
        if pattern_status == "SUCCESS":
            evidence_type = "PATTERN_SUCCESS"
            direction = EvidenceDirection.SUPPORT
        elif pattern_status == "DAMAGE":
            evidence_type = "PATTERN_DAMAGE"
            direction = EvidenceDirection.CONSTRAINT
        elif pattern_status == "RESCUE":
            evidence_type = "PATTERN_RESCUE"
            direction = EvidenceDirection.MODIFIER
        else:
            evidence_type = "PATTERN_CANDIDATE"
            direction = EvidenceDirection.CONTEXT
        
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type=evidence_type,
            direction=direction,
            authorization_level=authorization_level,
            notes=f"子平真诠 — {pattern_type}{pattern_status}证据",
        )
        return evidence
    
    def extract_yongshen_evidence(
        self,
        canonical_state: Dict,
        yongshen_type: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取用神证据
        
        子平真诠对用神有明确论述，但需要逐条验证
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="YONG_SHEN",
            direction=EvidenceDirection.SUPPORT,
            authorization_level=authorization_level,
            notes=f"子平真诠 — {yongshen_type}用神证据",
        )
        return evidence
    
    def extract_de_di_evidence(
        self,
        canonical_state: Dict,
        authorization_level: AuthorizationLevel = AuthorizationLevel.AUTHORIZED
    ) -> Evidence:
        """
        提取十干得地证据
        
        子平真诠有明确论述（已验证 AUTHORIZED）
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="DE_DI_SUPPORT",
            direction=EvidenceDirection.SUPPORT,
            authorization_level=authorization_level,
            notes="子平真诠 — 十干得地证据（已授权）",
        )
        return evidence
