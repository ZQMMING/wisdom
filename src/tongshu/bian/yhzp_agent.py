"""
YHZP 辨证代理（渊海子平）
========================
负责：基础语义辨证
核心观察维度：月令重要性 / 格局从月令出 / 十神基础 / 生克制化
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


class YHZPBianAgent(BianAgent):
    """
    渊海子平辨证代理
    
    核心辨证目标：基础语义
    关键观察维度：月令、格局基础、十神基础、生克制化
    """
    
    CLASSIC_ID = "yuan_hai_zi_ping"
    CLASSIC_NAME = "渊海子平"
    
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
    
    def __init__(self, classics_data_dir: Path, evidence_output_dir: Path):
        super().__init__(classics_data_dir, evidence_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载渊海子平原文数据"""
        return []
    
    def extract_month_command_evidence(
        self,
        canonical_state: Dict,
        authorization_level: AuthorizationLevel = AuthorizationLevel.AUTHORIZED
    ) -> Evidence:
        """
        提取月令重要性证据
        
        渊海子平：月令为提纲，格局之本
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="MONTH_COMMAND",
            direction=EvidenceDirection.CONTEXT,
            authorization_level=authorization_level,
            notes="渊海子平 — 月令重要性证据（已授权）",
        )
        return evidence
    
    def extract_pattern_source_evidence(
        self,
        canonical_state: Dict,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取格局来源证据
        
        渊海子平：格局从月令出
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="PATTERN_FROM_MONTH",
            direction=EvidenceDirection.CONTEXT,
            authorization_level=authorization_level,
            notes="渊海子平 — 格局从月令出证据",
        )
        return evidence
    
    def extract_basic_relation_evidence(
        self,
        canonical_state: Dict,
        relation_type: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取基础关系证据
        
        渊海子平提供基础语义，与子平真诠有重叠
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type=relation_type,
            direction=EvidenceDirection.CONTEXT,
            authorization_level=authorization_level,
            notes=f"渊海子平 — {relation_type}基础证据",
        )
        return evidence
