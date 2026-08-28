"""P5-B Guidance Composer - 指引组装器.

将多个GuidanceAtom组装为完整的用户指引.

硬契约(4条红线):
  1. Renderer不得重新计算 - ComposedGuidance已经包含所有用户可见信息
  2. Composer不得创造Evidence - 只组装已有GuidanceAtom, 不新增判断
  3. 不允许从direction偷换成吉凶 - 只用"有利条件"/"需要注意"/"无明显偏移"
  4. 不引入AI自由推理 - 组装逻辑是deterministic的

组装逻辑:
  1. 按domain分组GuidanceAtom
  2. 生成总体概述(基于所有GuidanceAtom的direction和intensity统计)
  3. 优先级排序(基于intensity和direction: caution优先, supportive其次, neutral最后)
  4. 组装为ComposedGuidance, 保留所有可追溯信息
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

from .guidance_atom import GuidanceAtom, DIRECTION_LABELS, FORBIDDEN_TERMS

log = logging.getLogger(__name__)


# domain中文标签
DOMAIN_LABELS = {
    "CAREER": "事业与工作",
    "FINANCE": "财富与资源",
    "RELATIONSHIP": "感情与亲密关系",
    "FAMILY": "家庭与亲情",
    "HEALTH": "健康与精力",
    "GROWTH": "个人成长与学习",
    "DECISION": "决策与判断",
    "MIGRATION": "迁移与环境变化",
}

# direction优先级(caution优先, 因为需要用户注意)
DIRECTION_PRIORITY = {
    "需要注意": 1,
    "有利条件": 2,
    "无明显方向性偏移": 3,
}


@dataclass
class DomainGuidance:
    """一个人生维度的完整指引."""
    domain: str
    domain_label: str
    atoms: list[GuidanceAtom] = field(default_factory=list)
    direction_summary: dict[str, int] = field(default_factory=dict)
    priority_score: float = 0.0
    top_theme: str = ""

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "domain_label": self.domain_label,
            "atom_count": len(self.atoms),
            "direction_summary": self.direction_summary,
            "priority_score": self.priority_score,
            "top_theme": self.top_theme,
            "atoms": [a.to_dict() for a in self.atoms],
        }


@dataclass
class ComposedGuidance:
    """组装后的完整用户指引."""
    case_id: str
    overall_summary: str  # 总体概述
    key_themes: list[str]  # 关键主题(优先级排序)
    domains: list[DomainGuidance]  # 按维度分组的详细指引
    priorities: list[dict]  # 优先级排序的行动建议
    source_guidance_ids: list[str]  # 来源GuidanceAtom ID
    source_assertion_ids: list[str]  # 来源Assertion ID(可追溯)
    source_engines: list[str]  # 互补覆盖面(不是投票)
    direction_distribution: dict[str, int]  # direction分布
    temporal_scope: str = "birth"
    status: str = "P5_COMPOSED"

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "overall_summary": self.overall_summary,
            "key_themes": self.key_themes,
            "domain_count": len(self.domains),
            "domains": [d.to_dict() for d in self.domains],
            "priorities": self.priorities,
            "source_guidance_ids": self.source_guidance_ids,
            "source_assertion_ids": self.source_assertion_ids,
            "source_engines": self.source_engines,
            "direction_distribution": self.direction_distribution,
            "temporal_scope": self.temporal_scope,
            "status": self.status,
        }


class GuidanceComposer:
    """指引组装器 - 将多个GuidanceAtom组装为完整用户指引.

    硬契约:
      - 不创造Evidence, 只组装已有GuidanceAtom
      - 不引入AI自由推理, 组装逻辑deterministic
      - 不允许从direction偷换成吉凶
      - 所有内容可追溯回GuidanceAtom → Assertion → Evidence
    """

    def __init__(self):
        self._domain_labels = DOMAIN_LABELS
        self._direction_priority = DIRECTION_PRIORITY

    def compose(
        self,
        atoms: list[GuidanceAtom],
        case_id: str,
    ) -> ComposedGuidance:
        """将GuidanceAtom列表组装为ComposedGuidance.

        Args:
            atoms: GuidanceAtom列表
            case_id: 命例ID

        Returns:
            ComposedGuidance
        """
        if not atoms:
            return ComposedGuidance(
                case_id=case_id,
                overall_summary="当前没有可组装的指引信息。",
                key_themes=[],
                domains=[],
                priorities=[],
                source_guidance_ids=[],
                source_assertion_ids=[],
                source_engines=[],
                direction_distribution={},
                status="P5_EMPTY",
            )

        # 1. 按domain分组
        domain_groups = self._group_by_domain(atoms)

        # 2. 构建DomainGuidance列表
        domain_guidances = []
        for domain, domain_atoms in domain_groups.items():
            dg = self._build_domain_guidance(domain, domain_atoms)
            domain_guidances.append(dg)

        # 按priority_score排序
        domain_guidances.sort(key=lambda x: x.priority_score, reverse=True)

        # 3. 生成总体概述
        overall_summary = self._generate_overall_summary(atoms, domain_guidances)

        # 4. 生成关键主题(优先级排序)
        key_themes = self._generate_key_themes(domain_guidances)

        # 5. 生成优先级行动建议
        priorities = self._generate_priorities(domain_guidances)

        # 6. 收集来源信息(可追溯)
        source_guidance_ids = [a.guidance_id for a in atoms]
        source_assertion_ids = list(set(
            aid for a in atoms for aid in a.source_assertion_ids
        ))
        source_engines = list(set(
            eng for a in atoms for eng in a.source_engines
        ))

        # 7. direction分布
        from collections import Counter
        direction_distribution = dict(Counter(a.direction_label for a in atoms))

        # temporal_scope取第一个
        temporal_scope = atoms[0].temporal_scope if atoms else "birth"

        return ComposedGuidance(
            case_id=case_id,
            overall_summary=overall_summary,
            key_themes=key_themes,
            domains=domain_guidances,
            priorities=priorities,
            source_guidance_ids=source_guidance_ids,
            source_assertion_ids=source_assertion_ids,
            source_engines=source_engines,
            direction_distribution=direction_distribution,
            temporal_scope=temporal_scope,
            status="P5_COMPOSED",
        )

    def _group_by_domain(self, atoms: list[GuidanceAtom]) -> dict[str, list[GuidanceAtom]]:
        """按domain分组."""
        groups: dict[str, list[GuidanceAtom]] = defaultdict(list)
        for a in atoms:
            groups[a.domain].append(a)
        return dict(groups)

    def _build_domain_guidance(self, domain: str, atoms: list[GuidanceAtom]) -> DomainGuidance:
        """构建一个domain的完整指引."""
        from collections import Counter

        # direction分布
        direction_summary = dict(Counter(a.direction_label for a in atoms))

        # 优先级分数: caution权重最高, 其次supportive, intensity加权
        priority_score = 0.0
        for a in atoms:
            base_priority = 4 - self._direction_priority.get(a.direction_label, 3)
            priority_score += base_priority * (a.intensity / 100.0)

        # top_theme: 取intensity最高的atom的theme
        top_atom = max(atoms, key=lambda a: a.intensity)
        top_theme = top_atom.theme

        return DomainGuidance(
            domain=domain,
            domain_label=self._domain_labels.get(domain, domain),
            atoms=atoms,
            direction_summary=direction_summary,
            priority_score=round(priority_score, 2),
            top_theme=top_theme,
        )

    def _generate_overall_summary(
        self,
        atoms: list[GuidanceAtom],
        domain_guidances: list[DomainGuidance],
    ) -> str:
        """生成总体概述(deterministic, 不引入AI自由推理).

        基于direction分布和domain分布生成结构化概述.
        """
        from collections import Counter

        total = len(atoms)
        direction_counts = Counter(a.direction_label for a in atoms)

        caution_count = direction_counts.get("需要注意", 0)
        supportive_count = direction_counts.get("有利条件", 0)
        neutral_count = direction_counts.get("无明显方向性偏移", 0)

        # 主要domain
        top_domains = [dg.domain_label for dg in domain_guidances[:3]]

        # 构建概述
        parts = []

        # 开头
        parts.append(f"当前结构分析涵盖{len(domain_guidances)}个人生维度，共{total}项具体指引。")

        # direction分布
        if caution_count > 0:
            parts.append(f"其中{caution_count}项属于需要注意的结构性压力，建议优先处理。")
        if supportive_count > 0:
            parts.append(f"{supportive_count}项属于可利用的有利条件，适合主动推进。")
        if neutral_count > 0:
            parts.append(f"{neutral_count}项当前没有明显方向性偏移，可按常规节奏推进。")

        # 主要维度
        if top_domains:
            parts.append(f"重点关注维度：{'、'.join(top_domains)}。")

        # 结尾(不做吉凶判断)
        parts.append("以上为结构性分析，具体行动建议请参考各维度详情。")

        return "".join(parts)

    def _generate_key_themes(self, domain_guidances: list[DomainGuidance]) -> list[str]:
        """生成关键主题(优先级排序)."""
        themes = []
        for dg in domain_guidances:
            if dg.top_theme:
                themes.append(f"{dg.domain_label}：{dg.top_theme}")
        return themes

    def _generate_priorities(self, domain_guidances: list[DomainGuidance]) -> list[dict]:
        """生成优先级行动建议.

        按优先级排序:
        1. caution类的actions(需要注意的事项)
        2. supportive类的actions(可利用的机会)
        3. neutral类的actions
        """
        priorities = []

        for dg in domain_guidances:
            for atom in dg.atoms:
                priority_level = self._direction_priority.get(atom.direction_label, 3)

                # actions
                for action in atom.actions:
                    priorities.append({
                        "domain": dg.domain_label,
                        "theme": atom.theme,
                        "direction": atom.direction_label,
                        "type": "action",
                        "content": action,
                        "priority": priority_level,
                        "intensity": atom.intensity,
                        "source_guidance_id": atom.guidance_id,
                    })

                # avoid
                for avoid in atom.avoid:
                    priorities.append({
                        "domain": dg.domain_label,
                        "theme": atom.theme,
                        "direction": atom.direction_label,
                        "type": "avoid",
                        "content": avoid,
                        "priority": priority_level,
                        "intensity": atom.intensity,
                        "source_guidance_id": atom.guidance_id,
                    })

        # 按priority排序, 同priority按intensity排序
        priorities.sort(key=lambda x: (x["priority"], -x["intensity"]))

        return priorities

    def get_stats(self, composed: ComposedGuidance) -> dict:
        """统计ComposedGuidance信息."""
        return {
            "case_id": composed.case_id,
            "domain_count": len(composed.domains),
            "guidance_atom_count": len(composed.source_guidance_ids),
            "assertion_count": len(composed.source_assertion_ids),
            "engine_coverage": composed.source_engines,
            "direction_distribution": composed.direction_distribution,
            "priority_count": len(composed.priorities),
            "key_theme_count": len(composed.key_themes),
            "status": composed.status,
        }
