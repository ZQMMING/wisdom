"""
Zhongzhou RuleGraph 子包（P0-4-A）

公开入口：
- features.build_feature_bundle / ZhongzhouFeatureBundle
- combinations.P0_4_A_PRODUCTION_DETECTORS / DRAFT_DETECTORS / ZhongzhouCombination
- judgments.judge_combinations / ZhongzhouJudgment
- evidence.EVIDENCE_TABLE / ZhongzhouEvidence / get_evidence
- rule_graph.ZhongzhouRuleGraph / ZhongzhouRuleGraphResult / ZhongzhouRuleMatch
- rule_graph.make_zhongzhou_rule_graph

P0-4-A 状态：
- 10 条 production detect 已落
- 10 条 DRAFT/CANDIDATE 已留 (detect_*_draft 强制返回 None)
- implementation_status = "PARTIAL"
- evidence_grade 一律 = 1 (王亭之原文)
"""
from .combinations import (
    DRAFT_DETECTORS,
    P0_4_A_PRODUCTION_DETECTORS,
    ZhongzhouCombination,
)
from .evidence import EVIDENCE_TABLE, ZhongzhouEvidence, get_evidence
from .features import (
    ZhongzhouFeatureBundle,
    build_feature_bundle,
    find_star_palace,
    get_neighbor_palaces,
    get_palace_branch,
    get_stars_in_palace,
    get_stars_in_sanfang_sizheng,
)
from .judgments import ZhongzhouJudgment, judge_combinations
from .rule_graph import (
    ZhongzhouRuleGraph,
    ZhongzhouRuleGraphResult,
    ZhongzhouRuleMatch,
    make_zhongzhou_rule_graph,
)

__all__ = [
    # features
    "ZhongzhouFeatureBundle",
    "build_feature_bundle",
    "find_star_palace",
    "get_neighbor_palaces",
    "get_palace_branch",
    "get_stars_in_palace",
    "get_stars_in_sanfang",
    # combinations
    "ZhongzhouCombination",
    "P0_4_A_PRODUCTION_DETECTORS",
    "DRAFT_DETECTORS",
    # judgments
    "ZhongzhouJudgment",
    "judge_combinations",
    # evidence
    "ZhongzhouEvidence",
    "EVIDENCE_TABLE",
    "get_evidence",
    # rule_graph
    "ZhongzhouRuleGraph",
    "ZhongzhouRuleGraphResult",
    "ZhongzhouRuleMatch",
    "make_zhongzhou_rule_graph",
]
