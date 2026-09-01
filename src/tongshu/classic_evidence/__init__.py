"""
Classic Evidence 模块 — 五部经典证据代理包
==========================================

架构：
- base.py: 基础框架（AssertionProvenance 数据结构 + ClassicEvidenceAgent 基类）
- dts_agent.py: 滴天髓证据代理（旺衰气势）
- pzzq_agent.py: 子平真诠证据代理（格局成败）
- qtbj_agent.py: 穷通宝鉴证据代理（调候寒暖）
- smth_agent.py: 三命通会证据代理（关系转化）
- yhzp_agent.py: 渊海子平证据代理（基础语义）

使用示例：
    from tongshu.classic_evidence import DTSEvidenceAgent
    
    agent = DTSEvidenceAgent(classics_data_dir, assertion_output_dir)
    assertion = agent.extract_seasonal_support(canonical_state, original_text, source_locator)
    agent.save_candidate(assertion)

核心原则：
- 每条 Assertion 必须带完整 provenance
- Agent 默认生产状态为 CANDIDATE
- 最终必须经过 Independent Audit → GPT 裁决才能进入生产
- 推理强度 ≤ 原典授权强度
"""

from .base import (
    ClassicEvidenceAgent,
    AssertionProvenance,
    SourceLocator,
    EvidenceText,
    SemanticParse,
    AuthorizationLevel,
    ProductionStatus,
    TextLayer,
    EvidenceSearchResultRecord,
    get_classic_short,
    get_classic_full,
)
from .dts_agent import DTSEvidenceAgent
from .pzzq_agent import PZZQEvidenceAgent
from .qtbj_agent import QTBJEvidenceAgent
from .smth_agent import SMTHEvidenceAgent
from .yhzp_agent import YHZPEvidenceAgent


__all__ = [
    "ClassicEvidenceAgent",
    "AssertionProvenance",
    "SourceLocator",
    "EvidenceText",
    "SemanticParse",
    "AuthorizationLevel",
    "ProductionStatus",
    "TextLayer",
    "EvidenceSearchResultRecord",
    "get_classic_short",
    "get_classic_full",
    "DTSEvidenceAgent",
    "PZZQEvidenceAgent",
    "QTBJEvidenceAgent",
    "SMTHEvidenceAgent",
    "YHZPEvidenceAgent",
]
