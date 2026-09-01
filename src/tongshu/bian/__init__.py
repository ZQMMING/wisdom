"""
Bian 模块 — 五部经典辨证代理包
================================

架构：
- base.py: 基础框架（Evidence 数据结构和 BianAgent 基类）
- dts_agent.py: 滴天髓辨证代理（旺衰气势）
- pzzq_agent.py: 子平真诠辨证代理（格局成败）
- qtbj_agent.py: 穷通宝鉴辨证代理（调候寒暖）
- smth_agent.py: 三命通会辨证代理（关系转化）
- yhzp_agent.py: 渊海子平辨证代理（基础语义）

使用示例：
    from tongshu.bian import DTSSBianAgent, PZZQBianAgent
    
    agent = DTSSBianAgent(classics_data_dir, evidence_output_dir)
    evidence = agent.extract_seasonal_support(canonical_state)
    agent.save_evidence(evidence)
"""

from .base import (
    BianAgent,
    Evidence,
    EvidenceDirection,
    AuthorizationLevel,
    VerificationStatus,
    CanonicalSource,
    get_classic_short,
    get_classic_full,
)
from .dts_agent import DTSSBianAgent
from .pzzq_agent import PZZQBianAgent
from .qtbj_agent import QTBJBianAgent
from .smth_agent import SMTHBianAgent
from .yhzp_agent import YHZPBianAgent


__all__ = [
    "BianAgent",
    "Evidence",
    "EvidenceDirection",
    "AuthorizationLevel",
    "VerificationStatus",
    "CanonicalSource",
    "get_classic_short",
    "get_classic_full",
    "DTSSBianAgent",
    "PZZQBianAgent",
    "QTBJBianAgent",
    "SMTHBianAgent",
    "YHZPBianAgent",
]
