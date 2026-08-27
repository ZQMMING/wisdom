"""P4-D Assertion Cluster - 断言聚类(互补, 不投票).

核心原则:
  - 聚类, 不投票
  - 不计算权重/分数/置信度
  - source_engines[] 表示互补覆盖面, 不是投票权重
  - evidence_count 表示证据数量, 不是概率

数据链:
  CanonicalAssertion[] (来自不同引擎)
    ↓ AssertionClusterer (按domain+semantic_family聚类)
  AssertionCluster[]

聚类逻辑:
  - 按domain分组(CAREER/FINANCE/RELATIONSHIP/...)
  - 按semantic_family分组(TRANSFORMATION/OUTPUT/RESOURCE/...)
  - 同一cluster内的assertions来自不同引擎, 表示互补印证
  - 不合并assertion的direction(每个assertion保留自己的direction)
  - cluster级别的direction_summary只是统计, 不是最终结论
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

from .assertion import CanonicalAssertion, AssertionDomain

log = logging.getLogger(__name__)


# 语义家族: 将相似的semantic归为同一family
# 用于聚类时把不同引擎的相似断言聚在一起
SEMANTIC_FAMILIES = {
    # 输出/表达类
    "OUTPUT_ACTIVATION": "OUTPUT_EXPRESSION",
    "EXPRESSION_ENHANCEMENT": "OUTPUT_EXPRESSION",
    "CREATIVITY_STIMULATION": "OUTPUT_EXPRESSION",
    "VISIBILITY_INCREASE": "OUTPUT_EXPRESSION",
    "AUTONOMY_EXPANSION": "OUTPUT_EXPRESSION",
    # 资源/财富类
    "RESOURCE_SUPPORT": "RESOURCE_WEALTH",
    "RESOURCE_AVAILABILITY": "RESOURCE_WEALTH",
    "ABUNDANCE_POTENTIAL": "RESOURCE_WEALTH",
    "WEALTH_ACCUMULATION": "RESOURCE_WEALTH",
    "ASSET_BUILDUP": "RESOURCE_WEALTH",
    # 稳定/支持类
    "STABILITY_STRENGTHEN": "STABILITY_SUPPORT",
    "ENDURANCE_BUILDUP": "STABILITY_SUPPORT",
    # 约束/规则类
    "CONSTRAINT_AWARENESS": "CONSTRAINT_RULE",
    "DISCIPLINE_REQUIRED": "CONSTRAINT_RULE",
    "RULE_NAVIGATION": "CONSTRAINT_RULE",
    "RESPONSIBILITY_INCREASE": "CONSTRAINT_RULE",
    # 变化/转型类
    "CHANGE_TRANSITION": "CHANGE_TRANSFORMATION",
    "TRANSFORMATION_PHASE": "CHANGE_TRANSFORMATION",
    "VOLATILITY_MANAGEMENT": "CHANGE_TRANSFORMATION",
    "DISRUPTION_EVENT": "CHANGE_TRANSFORMATION",
    # 反思/成长类
    "REFLECTION_PERIOD": "REFLECTION_GROWTH",
    "AWARENESS_EXPANSION": "REFLECTION_GROWTH",
    "INSIGHT_DEVELOPMENT": "REFLECTION_GROWTH",
    "CONTEMPLATION_PHASE": "REFLECTION_GROWTH",
    "INITIATIVE_TAKING": "REFLECTION_GROWTH",
    # 关系/感情类
    "RELATIONSHIP_DYNAMICS": "RELATION_CONNECTION",
    "SOCIAL_CONNECTION": "RELATION_CONNECTION",
    "CONNECTION_BUILDING": "RELATION_CONNECTION",
    "PARTNERSHIP_DEVELOPMENT": "RELATION_CONNECTION",
    "HARMONY_POTENTIAL": "RELATION_CONNECTION",
    "ATTRACT_OPPORTUNITY": "RELATION_CONNECTION",
    "RELATIONSHIP_RISK": "RELATION_CONNECTION",
    "TENSION_MANAGEMENT": "RELATION_CONNECTION",
    "CONFLICT_NAVIGATION": "RELATION_CONNECTION",
    # 行动/执行类
    "ACTION_INITIATIVE": "ACTION_EXECUTION",
    "EXECUTION_FOCUS": "ACTION_EXECUTION",
    "MOVEMENT_OPPORTUNITY": "ACTION_EXECUTION",
    # 健康类
    "HEALTH_RISK_AWARENESS": "HEALTH_CAUTION",
    "CAUTION_REQUIRED": "HEALTH_CAUTION",
    "PREVENTION_FOCUS": "HEALTH_CAUTION",
    "VULNERABILITY_NOTICE": "HEALTH_CAUTION",
}


@dataclass
class AssertionCluster:
    """断言聚类 - 互补, 不投票.

    一个cluster包含来自不同引擎的相似断言, 表示互补印证.
    不合并direction, 不计算权重, 只记录覆盖面和证据数量.
    """
    cluster_id: str
    case_id: str
    domain: str  # AssertionDomain值
    semantic_family: str  # 语义家族
    assertions: list[CanonicalAssertion] = field(default_factory=list)
    source_engines: list[str] = field(default_factory=list)  # 互补覆盖面, 不是投票
    evidence_count: int = 0  # 证据数量, 不是概率
    direction_summary: dict[str, int] = field(default_factory=dict)  # direction统计, 不是最终结论
    temporal_scope: str = "birth"  # 主要时间范围
    status: str = "P4_CLUSTERED"

    def to_dict(self) -> dict:
        return {
            "cluster_id": self.cluster_id,
            "case_id": self.case_id,
            "domain": self.domain,
            "semantic_family": self.semantic_family,
            "assertion_count": len(self.assertions),
            "assertions": [a.to_dict() for a in self.assertions],
            "source_engines": self.source_engines,
            "evidence_count": self.evidence_count,
            "direction_summary": self.direction_summary,
            "temporal_scope": self.temporal_scope,
            "status": self.status,
            "note": "互补聚类, 不投票; source_engines表示覆盖面, evidence_count表示证据数量, 均非权重/概率",
        }


class AssertionClusterer:
    """断言聚类器 - 按domain+semantic_family聚类, 互补不投票."""

    def __init__(self):
        self._families = SEMANTIC_FAMILIES

    def cluster(self, assertions: list[CanonicalAssertion]) -> list[AssertionCluster]:
        """将断言列表聚类.

        聚类逻辑:
          1. 按domain分组
          2. 按semantic_family分组(semantic映射到family)
          3. 同一cluster内的assertions来自不同引擎, 表示互补印证
          4. 不合并direction, 不计算权重
        """
        if not assertions:
            return []

        # 按(domain, semantic_family, temporal_scope)分组
        grouped: dict[tuple, list[CanonicalAssertion]] = defaultdict(list)
        for a in assertions:
            family = self._families.get(a.semantic, a.semantic)
            key = (a.domain, family, a.temporal_scope)
            grouped[key].append(a)

        # 构建cluster
        clusters = []
        for (domain, family, temporal_scope), group_assertions in grouped.items():
            cluster = self._build_cluster(
                case_id=group_assertions[0].case_id,
                domain=domain,
                semantic_family=family,
                temporal_scope=temporal_scope,
                assertions=group_assertions,
            )
            clusters.append(cluster)

        log.info(
            "AssertionClusterer: %d assertions → %d clusters",
            len(assertions), len(clusters),
        )
        return clusters

    def _build_cluster(
        self,
        case_id: str,
        domain: str,
        semantic_family: str,
        temporal_scope: str,
        assertions: list[CanonicalAssertion],
    ) -> AssertionCluster:
        """构建一个cluster."""
        # 收集来源引擎(互补覆盖面, 去重)
        source_engines = list(set(
            eng for a in assertions for eng in a.source_engines
        ))

        # 证据数量(所有assertion的source_signal_ids总数)
        evidence_count = sum(len(a.source_signal_ids) for a in assertions)

        # direction统计(不是最终结论, 只是分布)
        from collections import Counter
        direction_summary = dict(Counter(a.direction for a in assertions))

        cluster_id = f"CLS-{case_id[:8]}-{domain}-{semantic_family}-{temporal_scope}"

        return AssertionCluster(
            cluster_id=cluster_id,
            case_id=case_id,
            domain=domain,
            semantic_family=semantic_family,
            assertions=assertions,
            source_engines=source_engines,
            evidence_count=evidence_count,
            direction_summary=direction_summary,
            temporal_scope=temporal_scope,
        )

    def get_stats(self, clusters: list[AssertionCluster]) -> dict:
        """统计cluster信息."""
        from collections import Counter
        by_domain = Counter(c.domain for c in clusters)
        by_family = Counter(c.semantic_family for c in clusters)
        by_engine_coverage = Counter()
        for c in clusters:
            for eng in c.source_engines:
                by_engine_coverage[eng] += 1

        # 多引擎覆盖的cluster数量(互补印证强度)
        multi_engine_clusters = sum(1 for c in clusters if len(c.source_engines) >= 2)

        return {
            "total_clusters": len(clusters),
            "by_domain": dict(by_domain),
            "by_semantic_family": dict(by_family),
            "engine_coverage": dict(by_engine_coverage),
            "multi_engine_clusters": multi_engine_clusters,
            "single_engine_clusters": len(clusters) - multi_engine_clusters,
            "note": "multi_engine_clusters表示有多个引擎提供互补证据的cluster数量, 不是投票结果",
        }
