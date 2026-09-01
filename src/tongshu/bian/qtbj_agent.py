"""
QTBJ 辨证代理（穷通宝鉴）
========================
负责：调候寒暖辨证
核心观察维度：日干×月令二维调候 / 寒暖燥湿
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


class QTBJBianAgent(BianAgent):
    """
    穷通宝鉴辨证代理
    
    核心辨证目标：调候寒暖
    关键观察维度：日干×月令二维矩阵、寒暖燥湿
    """
    
    CLASSIC_ID = "qiong_tong_bao_jian"
    CLASSIC_NAME = "穷通宝鉴"
    
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
    
    def __init__(self, classics_data_dir: Path, evidence_output_dir: Path):
        super().__init__(classics_data_dir, evidence_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载穷通宝鉴原文数据"""
        return []
    
    def extract_climate_evidence(
        self,
        canonical_state: Dict,
        climate_type: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取气候状态证据
        
        穷通宝鉴核心：寒暖燥湿是调候基础
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="CLIMATE_STATE",
            direction=EvidenceDirection.CONTEXT,
            authorization_level=authorization_level,
            notes=f"穷通宝鉴 — {climate_type}气候证据",
        )
        return evidence
    
    def extract_tiaohou_evidence(
        self,
        canonical_state: Dict,
        day_master: str,
        month_branch: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取调候用神证据
        
        穷通宝鉴核心：日干×月令二维矩阵查表
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="PRIMARY_TIAOHOU",
            direction=EvidenceDirection.SUPPORT,
            authorization_level=authorization_level,
            notes=f"穷通宝鉴 — {day_master}日{month_branch}月调候证据",
        )
        return evidence
    
    def extract_tiaohou_availability_evidence(
        self,
        canonical_state: Dict,
        availability_type: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.NONE
    ) -> Evidence:
        """
        提取调候可用性证据

        穷通宝鉴对调候可用性有论述，但需要深入验证
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type=f"TIAOHOU_{availability_type.upper()}",
            direction=EvidenceDirection.MODIFIER,
            authorization_level=authorization_level,
            notes=f"穷通宝鉴 — 调候{availability_type}证据（待验证）",
        )
        return evidence
