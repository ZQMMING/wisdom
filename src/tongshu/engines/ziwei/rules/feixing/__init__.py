"""
Feixing Rules Subpackage — 飞星派规则子包（P0-5-A 入口）

Public API:
    FeixingRuleGraph     — 飞星派 RuleGraph（继承 BaseZiweiRuleGraph）
    FeixingRuleMatch     — 单条匹配结果 dataclass
    FeixingCombination   — 单条组合 detect 结果
    FeixingJudgment      — 单条判定结果
    FeixingEvidence      — 单条证据绑定
    FeixingFeatureBundle — 飞星派 Feature Bundle

P0-5-A 状态：
- 5 条 production 规则（grade=1 王亭之原文 / 飞星嫡系讲义）
- 5 条 DRAFT/CANDIDATE 规则占位（detect_*_draft 强制返回 None）
- 与中州派 / 三合派 / 钦天派严格隔离（不修改公共事实层）

架构对齐：
- P0-2 抽象（method_graphs.py BaseZiweiRuleGraph）— 4 派共用
- P0-3 中州 RuleGraph 已封板
- P0-4 中州 RuleGraph 升级 10 条生产
- P0-5-A 本子包把飞星 RuleGraph 从 SCAFFOLD 升级到 5 条生产
"""
from __future__ import annotations

from .combinations import (
    DRAFT_DETECTORS,
    P0_5_A_PRODUCTION_DETECTORS,
    FeixingCombination,
    detect_all_drafts,
    detect_all_production,
)
from .evidence import (
    EVIDENCE_TABLE,
    FeixingEvidence,
    all_evidence,
    evidence_grade,
    get_evidence,
)
from .features import (
    FeixingFeatureBundle,
    build_feature_bundle,
    find_star_palace,
    get_all_flying_transforms,
    get_major_stars_in_palace,
    get_neighbor_palaces,
    get_palace_branch,
    get_palace_stem,
    get_self_transforms,
    get_stars_in_palace,
)
from .judgments import FeixingJudgment, judge_all, judge_combination
from .rule_graph import FeixingRuleGraph, FeixingRuleMatch, FeixingRuleGraphResult, make_feixing_rule_graph


__all__ = [
    # 主入口
    "FeixingRuleGraph",
    "FeixingRuleMatch",
    "FeixingRuleGraphResult",
    "make_feixing_rule_graph",
    # 数据类
    "FeixingCombination",
    "FeixingJudgment",
    "FeixingEvidence",
    "FeixingFeatureBundle",
    # 查询函数
    "build_feature_bundle",
    "get_all_flying_transforms",
    "get_self_transforms",
    "get_stars_in_palace",
    "get_major_stars_in_palace",
    "get_palace_stem",
    "get_palace_branch",
    "get_neighbor_palaces",
    "find_star_palace",
    # 判定
    "judge_combination",
    "judge_all",
    # 证据
    "get_evidence",
    "all_evidence",
    "evidence_grade",
    # 调度
    "detect_all_production",
    "detect_all_drafts",
    # 注册表
    "P0_5_A_PRODUCTION_DETECTORS",
    "DRAFT_DETECTORS",
    "EVIDENCE_TABLE",
]