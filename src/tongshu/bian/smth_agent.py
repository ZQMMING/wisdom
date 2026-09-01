"""
SMTH 辨证代理（三命通会）
========================
负责：关系转化辨证
核心观察维度：刑冲合害 / 神煞 / 生克制化
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


class SMTHBianAgent(BianAgent):
    """
    三命通会辨证代理
    
    核心辨证目标：关系转化
    关键观察维度：刑冲合害、神煞、生克制化
    """
    
    CLASSIC_ID = "san_ming_tong_hui"
    CLASSIC_NAME = "三命通会"
    
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
    
    def __init__(self, classics_data_dir: Path, evidence_output_dir: Path):
        super().__init__(classics_data_dir, evidence_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载三命通会原文数据"""
        return []
    
    def extract_relation_evidence(
        self,
        canonical_state: Dict,
        relation_type: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取基础关系证据
        
        三命通会内容极其丰富，是资料汇编性质，需要逐条筛选
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type=relation_type,
            direction=EvidenceDirection.CONTEXT,
            authorization_level=authorization_level,
            notes=f"三命通会 — {relation_type}关系证据",
        )
        return evidence
    
    def extract_shensha_evidence(
        self,
        canonical_state: Dict,
        shensha_type: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.NONE
    ) -> Evidence:
        """
        提取神煞证据

        三命通会神煞数量众多，需要逐条验证是否进入辨证
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type=shensha_type,
            direction=EvidenceDirection.MODIFIER,
            authorization_level=authorization_level,
            notes=f"三命通会 — {shensha_type}神煞证据（需逐条验证）",
        )
        return evidence
    
    def extract_transformation_evidence(
        self,
        canonical_state: Dict,
        transformation_type: str,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取制化证据
        
        生克制化组合关系
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="TRANSFORMATION",
            direction=EvidenceDirection.MODIFIER,
            authorization_level=authorization_level,
            notes=f"三命通会 — {transformation_type}制化证据",
        )
        return evidence
