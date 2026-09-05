# -*- coding: utf-8 -*-
"""派别独立 RuleGraph 骨架（Z14-FIX）。

目标：四个 MethodId 各有独立 RuleGraph 实现，不再共享同一个 create_rule_graph()。

当前状态：
  - SanheRuleGraph:     ✅ 完整（从原有 ZiweiRuleGraph 迁移）
  - ZhongzhouRuleGraph: 🟡 SCAFFOLD（共享 SanheRuleGraph 逻辑，标记为骨架）
  - FeixingRuleGraph:    ✅ 完整（飞化规则，已有独立实现）
  - QintianRuleGraph:    🟡 SCAFFOLD（标记为未实现）

架构要求：
  - 每个类必须有独立的 __class__.__name__
  - method_id 必须正确对应
  - 不能互相 import 对方实例
  - 空实现必须明确标记为 SCAFFOLD，不能伪装成真实运行
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from ...ziwei_engine import FrozenZiweiChart, GAN_SIHUA
from ...ziwei_method_profile import (
    MethodId,
    RuleType,
    ConfidenceLevel,
    EvidenceRef,
    RuleSpec,
    ZiweiMethodProfile,
    get_profile,
)
from ...ziwei_palace_resolution import ZiweiPalaceResolver

logger = logging.getLogger(__name__)


# ============================================================================
# 抽象基类：定义四派 RuleGraph 的统一接口
# ============================================================================

class BaseZiweiRuleGraph(ABC):
    """所有派别 RuleGraph 必须继承的抽象基类。

    核心契约：
      - method_id: 对应的方法标识
      - profile:   对应的流派契约
      - match_all(chart): 全量匹配，返回匹配结果
      - rule_count: 规则总数
    """

    @property
    @abstractmethod
    def method_id(self) -> MethodId:
        """派别标识。"""

    @property
    @abstractmethod
    def profile(self) -> ZiweiMethodProfile:
        """流派契约。"""

    @abstractmethod
    def match_all(self, chart: FrozenZiweiChart) -> Any:
        """全量匹配（格局 + 四化 + 宫位）。"""

    @property
    @abstractmethod
    def rule_count(self) -> int:
        """规则总数。"""

    @property
    def implementation_status(self) -> str:
        """实现状态：'FULL' | 'SCAFFOLD' | 'DRAFT'。

        FULL:    完整实现，可生产使用
        SCAFFOLD: 骨架实现，逻辑来自父类/共享实现，待完善
        DRAFT:   草稿，未实现
        """
        return "FULL"


# ============================================================================
# SanheRuleGraph — 三合派完整实现（从原有 ZiweiRuleGraph 迁移）
# ============================================================================

class SanheRuleGraph(BaseZiweiRuleGraph):
    """三合派规则图谱（完整实现）。

    特点：
      - 重视三方四正格局（include_sanfang=True）
      - 空宫借星策略 partial
      - 有流昌流曲
      - 有宫干自化规则（通过 SiHua 表）
      - pattern matching: 命宫主星 + 三方四正星群 + 空宫借星打折
      - natal sihua: 从 birth_year 计算生年干，与命宫宫干严格区分
    """

    METHOD_ID = MethodId.SANHE

    def __init__(self) -> None:
        self._profile = get_profile(MethodId.SANHE)
        self._pattern_rules = self._build_pattern_rules()
        self._sihua_rules = self._build_sihua_rules()
        self._palace_rules = self._build_palace_rules()

    @property
    def method_id(self) -> MethodId:
        return self.METHOD_ID

    @property
    def profile(self) -> ZiweiMethodProfile:
        return self._profile

    @property
    def rule_count(self) -> int:
        return len(self._pattern_rules) + len(self._sihua_rules) + len(self._palace_rules)

    def match_all(self, chart: FrozenZiweiChart) -> Any:
        from .rule_graph import RuleMatchResult
        resolver = ZiweiPalaceResolver(chart, self.METHOD_ID)
        pattern_result = self._match_patterns(chart, include_sanfang=True)
        sihua_result = self._match_natal_sihua(chart)
        palace_result = self.match_palace_rules(chart)
        all_matches = list(pattern_result.matched_rules) + \
                      list(sihua_result.matched_rules) + \
                      list(palace_result.matched_rules)
        return RuleMatchResult(
            matched_rules=tuple(all_matches),
            method_id=self.METHOD_ID,
        )

    def _match_patterns(self, chart: FrozenZiweiChart,
                        include_sanfang: bool = True) -> Any:
        """三合派格局匹配：命宫主星 + 空宫借星 + 三方四正星群。"""
        from .rule_graph import RuleMatchResult, RuleMatch
        resolver = ZiweiPalaceResolver(chart, self.METHOD_ID)

        # 获取命宫主星
        ming_data = chart.palaces.get("命宫", {})
        ming_stars_zh: list[str] = list(ming_data.get("major", []))

        # 空宫借星
        borrowed: list[str] = []
        if not ming_stars_zh:
            borrowed = resolver.resolve_empty_palace("命宫")
            ming_stars_zh = list(borrowed)

        if include_sanfang:
            # 三合派：格局匹配范围 = 命宫 + 三方四正星群
            sf = resolver.resolve_sanfang_sizheng("命宫")
            sanfang_stars: list[str] = []
            for palace_name in ["命宫"] + sf["supporting"]:
                pd = chart.palaces.get(palace_name, {})
                sanfang_stars.extend(pd.get("major", []))
            match_stars = list(dict.fromkeys(sanfang_stars))
        else:
            match_stars = ming_stars_zh

        ming_stars_set = set(match_stars)
        matches: list[RuleMatch] = []
        unmatched: list[str] = []

        for rule in self._pattern_rules:
            condition = rule.condition
            required_stars = set(condition.get("stars", []))
            if required_stars <= ming_stars_set:
                qualifier = ""
                qualified = True
                if borrowed and required_stars <= set(borrowed):
                    qualified = False
                    qualifier = "空宫借星，力量打折"
                matches.append(RuleMatch(
                    rule_spec=rule,
                    facts={
                        "pattern_name": condition["pattern_name"],
                        "stars": match_stars,
                        "borrowed": borrowed,
                        "soul_borrowed": bool(borrowed),
                        "sanfang_expanded": include_sanfang,
                    },
                    qualified=qualified,
                    qualifier=qualifier,
                ))
            else:
                unmatched.append(condition.get("pattern_name", ""))

        return RuleMatchResult(
            matched_rules=tuple(matches),
            unmatched_patterns=tuple(unmatched),
            method_id=self.METHOD_ID,
        )

    @staticmethod
    def _stem_from_year(year: int) -> str:
        """从西元年号计算天干（4 AD = 甲子）。"""
        stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        return stems[(year - 4) % 10]

    def _match_natal_sihua(self, chart: FrozenZiweiChart) -> Any:
        """生年四化匹配：从 birth_year 计算生年干，查四化表映射落宫。

        注意：生年干 ≠ 命宫宫干。命宫宫干走飞星路径，不得混入。
        """
        from .rule_graph import RuleMatchResult
        if chart.birth_year <= 0:
            logger.warning(
                "[SanheRuleGraph] birth_year 未设置，无法计算生年干四化。"
            )
            return RuleMatchResult(method_id=self.METHOD_ID)
        birth_stem = self._stem_from_year(chart.birth_year)
        return self._match_sihua(chart, birth_stem)

    def _match_sihua(self, chart: FrozenZiweiChart, stem: str) -> Any:
        """匹配四化规则：查四化表 → 找落宫 → 生成证据。"""
        from .rule_graph import RuleMatchResult, RuleMatch
        sihua_table = self._profile.get_sihua_table()
        sihua_stars = sihua_table.get(stem)
        if not sihua_stars:
            return RuleMatchResult(method_id=self.METHOD_ID)

        lu, quan, ke, ji = sihua_stars
        # 查找四化星落入的宫位
        star_to_palace: dict[str, str] = {}
        for palace_name, palace_data in chart.palaces.items():
            all_stars = palace_data.get("major", []) + palace_data.get("minor", [])
            for star in all_stars:
                if star not in star_to_palace:
                    star_to_palace[star] = palace_name

        facts = {
            "stem": stem,
            "lu_star": lu,
            "quan_star": quan,
            "ke_star": ke,
            "ji_star": ji,
            "lu_palace": star_to_palace.get(lu, ""),
            "quan_palace": star_to_palace.get(quan, ""),
            "ke_palace": star_to_palace.get(ke, ""),
            "ji_palace": star_to_palace.get(ji, ""),
        }

        matches: list[RuleMatch] = []
        for sihua_name, star_name in [("化禄", lu), ("化权", quan), ("化科", ke), ("化忌", ji)]:
            palace = star_to_palace.get(star_name, "")
            matches.append(RuleMatch(
                rule_spec=RuleSpec(
                    rule_id=f"{self.METHOD_ID.value.upper()}-SIHUA-{stem}-{sihua_name}",
                    method_id=self.METHOD_ID,
                    rule_type=RuleType.SIHUA,
                    condition={"stem": stem, sihua_name: star_name},
                    operation={"action": "map_sihua_to_palace", "target_palace": palace},
                    confidence=ConfidenceLevel.HIGH,
                    evidence_refs=(EvidenceRef(
                        rule_id=f"ZW-SIHUA-{stem}",
                        source_work="紫微斗数全书",
                        source_chapter="四化篇",
                        verification_status="canonical",
                    ),),
                ),
                facts={**facts, "target_palace": palace},
            ))

        return RuleMatchResult(matched_rules=tuple(matches), method_id=self.METHOD_ID)

    def match_palace_rules(self, chart: FrozenZiweiChart) -> Any:
        from .rule_graph import RuleMatchResult
        matches = []
        for rule in self._palace_rules:
            palace = rule.condition.get("palace", "")
            if palace in chart.palaces:
                from .rule_graph import RuleMatch
                matches.append(RuleMatch(
                    rule_spec=rule,
                    facts={"palace": palace,
                           "stars": chart.palaces[palace].get("major", [])},
                ))
        return RuleMatchResult(matched_rules=tuple(matches),
                               method_id=self.METHOD_ID)

    def _build_pattern_rules(self) -> list[RuleSpec]:
        from ...ziwei_engine import CHINESE_STAR_TO_KEY
        # 使用原 PATTERN_DEFS（与 SanheRuleGraph 一致）
        from .rule_graph import PATTERN_DEFS
        rules = []
        for name, stars, desc in PATTERN_DEFS:
            rules.append(RuleSpec(
                rule_id=f"SANHE-PATTERN-{name}",
                method_id=MethodId.SANHE,
                rule_type=RuleType.PATTERN,
                condition={"pattern_name": name, "stars": sorted(stars)},
                operation={"action": "recognize_pattern", "description": desc},
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-PATTERN-{name}",
                    source_work="紫微斗数全书",
                    source_chapter="格局篇",
                    verification_status="candidate",
                ),),
            ))
        return rules

    def _build_sihua_rules(self) -> list[RuleSpec]:
        rules = []
        for stem, (lu, quan, ke, ji) in GAN_SIHUA.items():
            rules.append(RuleSpec(
                rule_id=f"SANHE-SIHUA-{stem}",
                method_id=MethodId.SANHE,
                rule_type=RuleType.SIHUA,
                condition={"stem": stem, "lu": lu, "quan": quan,
                           "ke": ke, "ji": ji},
                operation={"action": "map_sihua_to_palaces"},
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-SIHUA-{stem}",
                    source_work="紫微斗数全书",
                    source_chapter="四化篇",
                    verification_status="canonical",
                ),),
            ))
        return rules

    def _build_palace_rules(self) -> list[RuleSpec]:
        rules = []
        palace_themes = {
            "命宫": ("自我/性格/先天格局", "DECISION"),
            "兄弟": ("兄弟关系/合伙人", "RELATIONSHIP"),
            "夫妻": ("婚姻/感情状态", "RELATIONSHIP"),
            "子女": ("子女缘分/下属关系", "CREATION"),
            "财帛": ("财运来源/收入方式", "FINANCE"),
            "疾厄": ("身体健康/意外", "HEALTH"),
            "迁移": ("外出机遇/人际格局", "SOCIAL"),
            "仆役": ("朋友圈/贵人与小人", "SOCIAL"),
            "官禄": ("事业成就/社会地位", "CAREER"),
            "田宅": ("不动产/家庭环境", "FAMILY"),
            "福德": ("精神享受/内心福分", "SPIRITUAL"),
            "父母": ("父母关系/文书契约", "DOCUMENTS"),
        }
        for palace, (theme, domain) in palace_themes.items():
            rules.append(RuleSpec(
                rule_id=f"SANHE-PALACE-{palace}",
                method_id=MethodId.SANHE,
                rule_type=RuleType.PALACE,
                condition={"palace": palace},
                operation={"action": "apply_palace_theme", "theme": theme,
                           "domain": domain},
                confidence=ConfidenceLevel.MEDIUM,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-PALACE-{palace}",
                    source_work="紫微斗数全书",
                    source_chapter="十二宫",
                    verification_status="canonical",
                ),),
            ))
        return rules


# ============================================================================
# ZhongzhouRuleGraph — 中州派骨架（共享逻辑，待充实）
# ============================================================================

class ZhongzhouRuleGraph(BaseZiweiRuleGraph):
    """中州派规则图谱（SCAFFOLD）。

    特点：
      - 戊干科星=太阳（与三合派不同）
      - 空宫借星策略 full
      - 有流昌流曲、小限
      - 目前格局规则与三合派共享（待资料充实后独立）
    """

    METHOD_ID = MethodId.ZHONGZHOU

    def __init__(self) -> None:
        self._profile = get_profile(MethodId.ZHONGZHOU)
        # SCAFFOLD: 暂时共享 Sanhe 的格局规则（戊干四化表不同）
        self._pattern_rules = self._build_pattern_rules()
        self._sihua_rules = self._build_sihua_rules()
        self._palace_rules = self._build_palace_rules()

    @property
    def method_id(self) -> MethodId:
        return self.METHOD_ID

    @property
    def profile(self) -> ZiweiMethodProfile:
        return self._profile

    @property
    def implementation_status(self) -> str:
        return "SCAFFOLD"

    @property
    def rule_count(self) -> int:
        return len(self._pattern_rules) + len(self._sihua_rules) + len(self._palace_rules)

    def match_all(self, chart: FrozenZiweiChart) -> Any:
        """中州派独立全量匹配：格局 + 四化 + 宫位，不依赖 SanheRuleGraph。"""
        from .rule_graph import RuleMatchResult, RuleMatch
        # 格局匹配（占位骨架，实际 match 逻辑待充实）
        pattern_result = RuleMatchResult(matched_rules=(), method_id=self.METHOD_ID)
        # 四化匹配（占位骨架）
        sihua_result = RuleMatchResult(method_id=self.METHOD_ID)
        # 宫位主题匹配（真实可用）
        palace_matches = []
        for rule in self._palace_rules:
            palace = rule.condition.get("palace", "")
            if palace in chart.palaces:
                palace_matches.append(RuleMatch(
                    rule_spec=rule,
                    facts={"palace": palace,
                           "stars": chart.palaces[palace].get("major", [])},
                ))
        palace_result = RuleMatchResult(
            matched_rules=tuple(palace_matches), method_id=self.METHOD_ID
        )
        all_matches = list(pattern_result.matched_rules) + \
                      list(sihua_result.matched_rules) + \
                      list(palace_result.matched_rules)
        return RuleMatchResult(
            matched_rules=tuple(all_matches),
            method_id=self.METHOD_ID,
        )

    def _build_pattern_rules(self) -> list[RuleSpec]:
        from ...ziwei_engine import CHINESE_STAR_TO_KEY
        from .rule_graph import PATTERN_DEFS
        rules = []
        for name, stars, desc in PATTERN_DEFS:
            rules.append(RuleSpec(
                rule_id=f"ZHONGZHOU-PATTERN-{name}",
                method_id=MethodId.ZHONGZHOU,
                rule_type=RuleType.PATTERN,
                condition={"pattern_name": name, "stars": sorted(stars)},
                operation={"action": "recognize_pattern", "description": desc},
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-PATTERN-{name}",
                    source_work="紫微斗数全书",
                    source_chapter="格局篇",
                    verification_status="candidate",
                ),),
            ))
        return rules

    def _build_sihua_rules(self) -> list[RuleSpec]:
        # 中州派戊干科星=太阳
        from ...ziwei_method_profile import SIHUA_TABLE_ZHONGZHOU
        rules = []
        for stem, (lu, quan, ke, ji) in SIHUA_TABLE_ZHONGZHOU.items():
            rules.append(RuleSpec(
                rule_id=f"ZHONGZHOU-SIHUA-{stem}",
                method_id=MethodId.ZHONGZHOU,
                rule_type=RuleType.SIHUA,
                condition={"stem": stem, "lu": lu, "quan": quan,
                           "ke": ke, "ji": ji},
                operation={"action": "map_sihua_to_palaces"},
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-SIHUA-{stem}-ZZ",
                    source_work="紫微斗数全书",
                    source_chapter="四化篇",
                    verification_status="candidate",
                ),),
            ))
        return rules

    def _build_palace_rules(self) -> list[RuleSpec]:
        rules = []
        palace_themes = {
            "命宫": ("自我/性格/先天格局", "DECISION"),
            "兄弟": ("兄弟关系/合伙人", "RELATIONSHIP"),
            "夫妻": ("婚姻/感情状态", "RELATIONSHIP"),
            "子女": ("子女缘分/下属关系", "CREATION"),
            "财帛": ("财运来源/收入方式", "FINANCE"),
            "疾厄": ("身体健康/意外", "HEALTH"),
            "迁移": ("外出机遇/人际格局", "SOCIAL"),
            "仆役": ("朋友圈/贵人与小人", "SOCIAL"),
            "官禄": ("事业成就/社会地位", "CAREER"),
            "田宅": ("不动产/家庭环境", "FAMILY"),
            "福德": ("精神享受/内心福分", "SPIRITUAL"),
            "父母": ("父母关系/文书契约", "DOCUMENTS"),
        }
        for palace, (theme, domain) in palace_themes.items():
            rules.append(RuleSpec(
                rule_id=f"ZHONGZHOU-PALACE-{palace}",
                method_id=MethodId.ZHONGZHOU,
                rule_type=RuleType.PALACE,
                condition={"palace": palace},
                operation={"action": "apply_palace_theme", "theme": theme,
                           "domain": domain},
                confidence=ConfidenceLevel.MEDIUM,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-PALACE-{palace}-ZZ",
                    source_work="紫微斗数全书",
                    source_chapter="十二宫",
                    verification_status="canonical",
                ),),
            ))
        return rules


# ============================================================================
# QintianRuleGraph — 钦天门草稿（待 Hermes 完成资料后充实）
# ============================================================================

class QintianRuleGraph(BaseZiweiRuleGraph):
    """钦天门规则图谱（DRAFT）。

    特点（预估）：
      - 立极宫为核心技法
      - 四化表与三合派兼容
      - 自化支持
      - 空宫策略 partial
    """

    METHOD_ID = MethodId.QINTIAN

    def __init__(self) -> None:
        self._profile = get_profile(MethodId.QINTIAN)

    @property
    def method_id(self) -> MethodId:
        return self.METHOD_ID

    @property
    def profile(self) -> ZiweiMethodProfile:
        return self._profile

    @property
    def implementation_status(self) -> str:
        return "DRAFT"

    @property
    def rule_count(self) -> int:
        return 0

    def match_all(self, chart: FrozenZiweiChart) -> Any:
        from .rule_graph import RuleMatchResult
        # DRAFT: 暂无规则
        return RuleMatchResult(method_id=self.METHOD_ID)
