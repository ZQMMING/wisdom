# -*- coding: utf-8 -*-
"""Z13: 飞星派规则图谱（FeixingRuleGraph）— 宫干飞化事实层

架构边界：
  - 本模块只负责"飞化事实计算与规则匹配"
  - 不产生最终判断（方向/polarity/strength/confidence 由辨层负责）
  - method_id = FEIXING，绝不与 SANHE/ZHONGZHOU 规则交叉读取

四层结构（Z13-A → Z13-D）：
  A. PalaceStemFact     — 宫干事实（十二宫 × 宫干）
  B. FlyingTransform   — 飞化计算（宫干 → 四化 → 落宫）
  C. FeixingRuleGraph  — 飞化规则图谱（飞化规则匹配）
  D. 生产路径集成       — 真实 chart 端到端验证
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ...ziwei_engine import FrozenZiweiChart, GAN_SIHUA
from ...ziwei_method_profile import MethodId, RuleType, ConfidenceLevel, EvidenceRef, RuleSpec, get_profile
from ...ziwei_palace_resolution import ZiweiPalaceResolver

logger = logging.getLogger(__name__)


# ============================================================================
# Z13-A: PalaceStemFact — 宫干事实层
# ============================================================================

@dataclass(frozen=True)
class PalaceStemFact:
    """单宫宫干事实：纯计算事实，无诊断语义。

    职责：回答"哪个宫位是什么干"，不回答"这个干意味着什么"。
    """
    palace_name: str           # 宫位名（如"命宫"）
    stem: str                  # 宫干（如"甲"）
    branch: str                # 地支（如"申"）
    major_stars: tuple[str, ...] = field(default_factory=tuple)
    minor_stars: tuple[str, ...] = field(default_factory=tuple)

    def has_stem(self) -> bool:
        return bool(self.stem)

    def to_dict(self) -> dict:
        return {
            "palace_name": self.palace_name,
            "stem": self.stem,
            "branch": self.branch,
            "major_stars": list(self.major_stars),
            "minor_stars": list(self.minor_stars),
        }


class PalaceStemContract:
    """宫干事实契约：从 FrozenZiweiChart 提取确定性宫干事实。

    Z13-A 独立层：不涉及任何飞化计算，只返回事实。
    """

    @staticmethod
    def extract(chart: FrozenZiweiChart) -> tuple[PalaceStemFact, ...]:
        """从 chart 提取全部 12 宫的宫干事实。

        Returns:
            (PalaceStemFact, ...) — 不可变元组
        """
        facts: list[PalaceStemFact] = []
        for palace_name, pd in chart.palaces.items():
            facts.append(PalaceStemFact(
                palace_name=palace_name,
                stem=pd.get("stem", ""),
                branch=pd.get("branch", ""),
                major_stars=tuple(pd.get("major", [])),
                minor_stars=tuple(pd.get("minor", [])),
            ))
        return tuple(facts)

    @staticmethod
    def get_palace_stem(chart: FrozenZiweiChart, palace_name: str) -> str:
        """安全获取指定宫位的宫干（空字符串表示无宫干）。"""
        return chart.palaces.get(palace_name, {}).get("stem", "")

    @staticmethod
    def has_self_mutagen(palace_fact: PalaceStemFact) -> bool:
        """判断某宫是否有自化（宫干四化落回本宫）。

        注意：此函数仅做事实判断，不产生诊断结论。
        """
        if not palace_fact.stem:
            return False
        sihua = GAN_SIHUA.get(palace_fact.stem, ())
        if not sihua:
            return False
        all_stars = set(palace_fact.major_stars) | set(palace_fact.minor_stars)
        return any(star in all_stars for star in sihua)


# ============================================================================
# Z13-B: FlyingTransform — 飞化事实层
# ============================================================================

@dataclass(frozen=True)
class FlyingTransformFact:
    """单次飞化事实：宫干 → 四化 → 落宫。

    例如：命宫(甲) → 廉贞化禄 → 子女宫
    这是纯事实，不含"事业好/坏"等判断。
    """
    source_palace: str         # 来源宫位
    source_stem: str           # 来源宫干
    transformation: str        # 四化名（"化禄"/"化权"/"化科"/"化忌"）
    target_star: str           # 化星（如"廉贞"）
    target_palace: str         # 目标宫位（化星所在宫）
    direction: Literal["in", "out", "self"]  # 入/出/自化

    def to_dict(self) -> dict:
        return {
            "source_palace": self.source_palace,
            "source_stem": self.source_stem,
            "transformation": self.transformation,
            "target_star": self.target_star,
            "target_palace": self.target_palace,
            "direction": self.direction,
        }


# ============================================================================
# Z13-C: FeixingRuleGraph — 飞化规则图谱
# ============================================================================

class FeixingRuleGraph:
    """飞星派规则图谱。

    核心原则：
      - 只消费 PalaceStemFact + FlyingTransformFact
      - 不消费 NatalSihua（生年四化走 Z12 路径）
      - 不消费 SanheProfile 规则
      - method_id 强制 = FEIXING
    """

    # 飞星派核心规则定义
    _FLYING_RULES = [
        # 飞入规则：某宫四化飞入他宫
        (
            "FEIXING-FLY-IN",
            "飞入规则",
            "宫干四化星落入他宫 → 该宫受他宫干影响",
            RuleType.SIHUA,
        ),
        # 飞出规则：某宫四化星从他宫飞出
        (
            "FEIXING-FLY-OUT",
            "飞出规则",
            "宫干四化星不在本宫 → 本宫能量飞出至他宫",
            RuleType.SIHUA,
        ),
        # 自化规则：宫干四化落回本宫（飞星派重视）
        (
            "FEIXING-SELF-MUTAGEN",
            "自化规则",
            "宫干四化星落入本宫主星/辅星 → 自化",
            RuleType.SIHUA,
        ),
        # 来因宫规则：某化忌的宫干来源
        (
            "FEIXING-LAIYIN",
            "来因宫规则",
            "化忌所在宫位即为来因宫（问题根源）",
            RuleType.SIHUA,
        ),
    ]

    def __init__(self) -> None:
        self._method_id = MethodId.FEIXING
        self._profile = get_profile(MethodId.FEIXING)
        # 预编译飞化规则
        self._flying_rules: list[RuleSpec] = self._build_flying_rules()

    def _build_flying_rules(self) -> list[RuleSpec]:
        rules = []
        for rule_id, title, desc, rtype in self._FLYING_RULES:
            rules.append(RuleSpec(
                rule_id=f"FEIXING-{rule_id}",
                method_id=MethodId.FEIXING,
                rule_type=rtype,
                condition={},  # 飞化规则条件动态构建
                operation={"action": f"match_{rule_id.lower().replace('-', '_')}"},
                confidence=ConfidenceLevel.MEDIUM,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-FEIXING-{rule_id}",
                    source_work="飞星派典籍",
                    source_chapter="宫干飞化",
                    verification_status="candidate",
                ),),
            ))
        return rules

    # ── 核心 API ────────────────────────────────────────────────────────────

    def compute_all_flying_transforms(
        self, chart: FrozenZiweiChart
    ) -> tuple[FlyingTransformFact, ...]:
        """计算全部宫干的飞化事实。

        流程：
          1. 提取 PalaceStemFact（12宫宫干）
          2. 对每个有宫干的宫，查 GAN_SIHUA 表
          3. 将四化星定位到目标宫位
          4. 标注 direction（入/出/自化）

        注意：此处绝不使用 natal stem（出生年干），只用宫干。
        """
        stem_contract = PalaceStemContract()
        stem_facts = stem_contract.extract(chart)

        transforms: list[FlyingTransformFact] = []
        # star_to_palace 反向索引
        star_to_palace: dict[str, str] = {}
        for pf in stem_facts:
            for star in pf.major_stars + pf.minor_stars:
                if star not in star_to_palace:
                    star_to_palace[star] = pf.palace_name

        for pf in stem_facts:
            if not pf.stem:
                continue
            sihua = GAN_SIHUA.get(pf.stem, ())
            if not sihua or len(sihua) < 4:
                continue

            for i, (sihua_name, star_name) in enumerate(zip(
                ("化禄", "化权", "化科", "化忌"), sihua[:4]
            )):
                target_palace = star_to_palace.get(star_name, "")
                if not target_palace:
                    continue

                # 判断方向
                if target_palace == pf.palace_name:
                    direction = "self"
                elif target_palace:
                    direction = "out"  # 本宫干飞出的星落入他宫
                else:
                    continue  # 化星不在十二宫，忽略

                transforms.append(FlyingTransformFact(
                    source_palace=pf.palace_name,
                    source_stem=pf.stem,
                    transformation=sihua_name,
                    target_star=star_name,
                    target_palace=target_palace,
                    direction=direction,
                ))

        return tuple(transforms)

    def match_flying_rules(
        self,
        chart: FrozenZiweiChart,
        transforms: tuple[FlyingTransformFact, ...] | None = None,
    ) -> list[dict[str, Any]]:
        """匹配飞化规则，返回 RuleMatch 格式（兼容 Z12 RuleMatchResult）。

        返回每条匹配规则的 facts 摘要，不含最终判断。
        """
        if transforms is None:
            transforms = self.compute_all_flying_transforms(chart)

        results: list[dict[str, Any]] = []

        # 飞入规则匹配
        for t in transforms:
            if t.direction == "in" and t.target_palace:
                results.append({
                    "rule_id": "FEIXING-FLY-IN",
                    "method_id": self._method_id.value,
                    "facts": t.to_dict(),
                    "confidence": "medium",
                    "verification_status": "candidate",
                })

        # 自化规则匹配
        for t in transforms:
            if t.direction == "self":
                results.append({
                    "rule_id": "FEIXING-SELF-MUTAGEN",
                    "method_id": self._method_id.value,
                    "facts": t.to_dict(),
                    "confidence": "high",
                    "verification_status": "candidate",
                })

        # 来因宫规则（化忌落在哪宫）
        ji_transforms = [t for t in transforms if t.transformation == "化忌"]
        for t in ji_transforms:
            results.append({
                "rule_id": "FEIXING-LAIYIN",
                "method_id": self._method_id.value,
                "facts": {
                    "ji_star": t.target_star,
                    "ji_palace": t.target_palace,
                    "source_palace": t.source_palace,
                    "source_stem": t.source_stem,
                },
                "confidence": "high",
                "verification_status": "candidate",
            })

        return results

    @property
    def method_id(self) -> MethodId:
        return self._method_id

    @property
    def profile(self) -> Any:
        return self._profile


# ============================================================================
# 工厂函数
# ============================================================================

def create_feixing_rule_graph() -> FeixingRuleGraph:
    """创建飞星派 RuleGraph 实例。"""
    return FeixingRuleGraph()
