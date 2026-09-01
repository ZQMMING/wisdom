"""
DTS 辨证代理（滴天髓）
====================
负责：旺衰气势辨证
核心观察维度：得令 / 得地 / 得势 / 受制 / 泄耗 / 气势流通
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .base import (
    BianAgent,
    Evidence,
    EvidenceDirection,
    AuthorizationLevel,
    VerificationStatus,
    CanonicalSource,
)


class DTSSBianAgent(BianAgent):
    """
    滴天髓辨证代理
    
    核心辨证目标：日主旺衰气势
    关键观察维度：得令、得地、得势、受制、泄耗
    """
    
    CLASSIC_ID = "di_tian_sui"
    CLASSIC_NAME = "滴天髓"
    
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
    
    def __init__(self, classics_data_dir: Path, evidence_output_dir: Path):
        super().__init__(classics_data_dir, evidence_output_dir)
        
    def _load_classic_entries(self) -> List[Dict]:
        """加载滴天髓原文数据"""
        # TODO: 实现具体加载逻辑
        return []
    
    def extract_seasonal_support(
        self,
        canonical_state: Dict,
        authorization_level: AuthorizationLevel = AuthorizationLevel.PARTIAL
    ) -> Evidence:
        """
        提取得令证据
        
        滴天髓·通神论·衰旺：
        "得令者旺，失令者衰"
        """
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type="SEASONAL_SUPPORT",
            direction=EvidenceDirection.SUPPORT,
            authorization_level=authorization_level,
            notes="滴天髓·通神论·衰旺 — 得令证据",
        )
        return evidence
    
    def extract_root_evidence(
        self,
        canonical_state: Dict,
        root_type: str = "MAIN_QI",
        authorization_level: AuthorizationLevel = AuthorizationLevel.AUTHORIZED
    ) -> Evidence:
        """
        提取得地证据
        
        滴天髓·通神论·衰旺：
        "根气者有力，无根者虚浮"
        """
        evidence_type = "ROOT_PRESENT" if root_type == "ANY" else "MAIN_QI_ROOT"
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type=evidence_type,
            direction=EvidenceDirection.SUPPORT,
            authorization_level=authorization_level,
            notes=f"滴天髓·通神论·衰旺 — {root_type}根气证据",
        )
        return evidence
    
    def extract_flow_evidence(
        self,
        canonical_state: Dict,
        flow_status: str = "SMOOTH",
        authorization_level: AuthorizationLevel = AuthorizationLevel.NONE
    ) -> Evidence:
        """
        提取气势流通证据

        滴天髓对气势流通有论述，但需要深入原典验证具体规则
        """
        evidence_type = "FLOW_SMOOTH" if flow_status == "SMOOTH" else "FLOW_BLOCKED"
        evidence = self.extract_evidence(
            canonical_state=canonical_state,
            evidence_type=evidence_type,
            direction=EvidenceDirection.CONTEXT,
            authorization_level=authorization_level,
            notes="滴天髓·通神论 — 气势流通证据（待深入原典验证）",
        )
        return evidence
