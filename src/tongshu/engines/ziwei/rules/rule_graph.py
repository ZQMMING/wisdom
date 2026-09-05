# -*- coding: utf-8 -*-
"""ZiweiRuleGraph — 流派规则图谱（Z12）。

职责：
  - 承载各流派（三合/中州/飞星/钦天）的断事规则
  - 提供 pattern_match / sihua_match / palace_match 匹配引擎
  - 每条规则带 method_id，无 method_id=ALL
  - 输出：RuleMatch（含 matched_rules + evidence + qualifier）

设计原则：
  - RuleGraph 是纯数据+匹配逻辑，不产生最终判断
  - pattern_match → 格局规则（武贪格、杀破狼等）
  - sihua_match → 四化落宫规则
  - palace_match → 宫位主题规则
  - 规则前置条件 = FrozenZiweiChart 事实的子集
  - 规则输出 = RuleMatch（事实 + 置信度 + 限定条件）
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from ...ziwei_engine import FrozenZiweiChart, GAN_SIHUA, ZW_PALACES_ORDER
from ...ziwei_method_profile import (
    MethodId,
    RuleType,
    ConfidenceLevel,
    RuleSpec,
    EvidenceRef,
    ZiweiMethodProfile,
    get_profile,
)
from ...ziwei_palace_resolution import ZiweiPalaceResolver

logger = logging.getLogger(__name__)


# ============================================================================
# 规则匹配结果
# ============================================================================

@dataclass(frozen=True)
class RuleMatch:
    """单条规则匹配结果。"""
    rule_spec: RuleSpec
    facts: dict[str, Any]
    qualified: bool = True  # True=条件完全满足; False=条件部分满足需限定
    qualifier: str = ""     # 限定说明（如"逢煞减力"、"空宫借星打折"）

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_spec.rule_id,
            "method_id": self.rule_spec.method_id.value,
            "rule_type": self.rule_spec.rule_type.value,
            "confidence": self.rule_spec.confidence.value,
            "qualified": self.qualified,
            "qualifier": self.qualifier,
            "facts": self.facts,
        }


@dataclass(frozen=True)
class RuleMatchResult:
    """规则图匹配总结果。"""
    matched_rules: tuple[RuleMatch, ...] = field(default_factory=tuple)
    unmatched_patterns: tuple[str, ...] = field(default_factory=tuple)
    method_id: MethodId = MethodId.SANHE

    def to_dict(self) -> dict:
        return {
            "method_id": self.method_id.value,
            "matched_count": len(self.matched_rules),
            "matches": [m.to_dict() for m in self.matched_rules],
            "unmatched_patterns": list(self.unmatched_patterns),
        }


# ============================================================================
# 格局定义（三合派核心规则来源）
# ============================================================================

# (格局名, 命宫主星组合, 说明)
PATTERN_DEFS = [
    ("紫微独坐", {"紫微"}, "帝王星独坐，权威自显"),
    ("天府朝垣", {"紫微", "天府"}, "紫府同宫，稳重富贵"),
    ("极居卯酉", {"紫微", "贪狼"}, "紫贪在卯酉，桃花与权柄交织"),
    ("紫杀化权", {"紫微", "七杀"}, "紫杀同宫，威权显赫"),
    ("紫相同宫", {"紫微", "天相"}, "紫微辅印，贵气佐贰"),
    ("武贪格", {"武曲", "贪狼"}, "武贪不发少年人，晚发"),
    ("武杀同宫", {"武曲", "七杀"}, "武杀，刚毅决断"),
    ("武破同宫", {"武曲", "破军"}, "武破，变革开拓"),
    ("武府同宫", {"武曲", "天府"}, "武府，财库稳定"),
    ("日月并明", {"太阳", "太阴"}, "日月同宫，光明圆融"),
    ("机月同梁", {"天机", "天同"}, "机月同梁格，智谋安逸"),
    ("机梁善谈", {"天机", "天梁"}, "机梁善谈格，才智口才"),
    ("机巨同宫", {"天机", "巨门"}, "机巨，聪明多思"),
    ("月朗天门", {"天同", "太阴"}, "天同太阴，温和清贵"),
    ("天同天梁", {"天同", "天梁"}, "福荫安逸，逢凶化吉"),
    ("廉贪同宫", {"廉贞", "贪狼"}, "廉贪，桃花主才华风流"),
    ("廉杀同宫", {"廉贞", "七杀"}, "廉杀，刑狱之象"),
    ("廉破同宫", {"廉贞", "破军"}, "廉破，动荡变革"),
    ("府相朝垣", {"天府", "天相"}, "府相朝垣，辅佐之才"),
    ("杀破狼", {"七杀", "破军", "贪狼"}, "杀破狼格，大起大落"),
    ("七杀朝斗", {"七杀"}, "七杀坐命，威猛刚烈"),
    ("破军坐命", {"破军"}, "破军坐命，开创变革"),
    ("巨日同宫", {"巨门", "太阳"}, "巨日同宫，口才权威"),
    ("天相坐命", {"天相"}, "天相坐命，辅印协调"),
    ("天梁坐命", {"天梁"}, "天梁坐命，荫星逢凶化吉"),
    ("贪狼坐命", {"贪狼"}, "贪狼坐命，欲望桃花多才"),
    ("太阴坐命", {"太阴"}, "太阴坐命，内敛柔美"),
    ("太阳坐命", {"太阳"}, "太阳坐命，光明磊落"),
    ("天同坐命", {"天同"}, "天同坐命，福星安逸"),
    ("武曲坐命", {"武曲"}, "武曲坐命，财星刚毅"),
    ("天机坐命", {"天机"}, "天机坐命，智谋机变"),
    ("廉贞坐命", {"廉贞"}, "廉贞坐命，拘谨守正"),
    ("巨门坐命", {"巨门"}, "巨门坐命，口才是非"),
    ("天府坐命", {"天府"}, "天府坐命，财库稳重"),
    ("廉府同宫", {"廉贞", "天府"}, "廉府同宫，财官双美"),
    ("武相同宫", {"武曲", "天相"}, "武相同宫，财印相辅"),
    ("紫府同宫", {"紫微", "天府"}, "紫府同宫，尊贵稳重"),
    ("阳梁同宫", {"太阳", "天梁"}, "阳梁同宫，贵气荫庇"),
    ("同梁同宫", {"天同", "天梁"}, "同梁同宫，福荫安逸"),
    ("杀狼同宫", {"七杀", "贪狼"}, "杀狼同宫，威权欲望"),
    ("破狼同宫", {"破军", "贪狼"}, "破狼同宫，变革欲望"),
]

# 中文星名 → pinyin key 反向映射（用于规则匹配时从 chart 数据获取中文星名）
CHINESE_STAR_TO_KEY = {
    "紫微": "ZIWEI", "天府": "TIANFU", "太阳": "TAIYANG", "天梁": "TIANLIANG",
    "武曲": "WUQU", "太阴": "TAIYIN", "天同": "TIANTONG", "天机": "TIANJI",
    "贪狼": "TANLANG", "廉贞": "LIANZHEN", "破军": "POJUN", "七杀": "QISHA",
    "巨门": "JUMEN", "天相": "TIANXIANG",
}


# ============================================================================
# 规则图谱
# ============================================================================

class ZiweiRuleGraph:
    """紫微流派规则图谱。

    包含：
    - 格局规则（pattern rules）
    - 四化规则（sihua rules）
    - 宫位主题规则（palace rules）

    匹配引擎：
    - match_patterns(chart) → RuleMatchResult（格局匹配）
    - match_sihua(chart, stem) → RuleMatchResult（四化匹配）
    - match_all(chart, resolver) → RuleMatchResult（全量匹配）
    """

    def __init__(self, method_id: MethodId) -> None:
        self._method_id = method_id
        self._profile = get_profile(method_id)
        # 预编译规则（从 PATTERN_DEFS 生成 RuleSpec）
        self._pattern_rules: list[RuleSpec] = self._build_pattern_rules()
        self._sihua_rules: list[RuleSpec] = self._build_sihua_rules()
        self._palace_rules: list[RuleSpec] = self._build_palace_rules()

    # ── 规则构建 ────────────────────────────────────────────────────────────

    def _build_pattern_rules(self) -> list[RuleSpec]:
        """从 PATTERN_DEFS 构建格局规则。"""
        rules = []
        for name, stars, desc in PATTERN_DEFS:
            rules.append(RuleSpec(
                rule_id=f"{self._method_id.value.upper()}-PATTERN-{name}",
                method_id=self._method_id,
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
        """从 GAN_SIHUA + SIHUA_TABLE 构建四化规则。"""
        rules = []
        table = self._profile.get_sihua_table()
        for stem, (lu, quan, ke, ji) in table.items():
            rules.append(RuleSpec(
                rule_id=f"{self._method_id.value.upper()}-SIHUA-{stem}",
                method_id=self._method_id,
                rule_type=RuleType.SIHUA,
                condition={"stem": stem, "lu": lu, "quan": quan, "ke": ke, "ji": ji},
                operation={"action": "map_sihua_to_palaces"},
                confidence=ConfidenceLevel.HIGH,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-SIHUA-{stem}",
                    source_work="紫微斗数全书",
                    source_chapter="四化篇",
                    verification_status="canonical" if stem in GAN_SIHUA else "candidate",
                ),),
            ))
        return rules

    def _build_palace_rules(self) -> list[RuleSpec]:
        """构建宫位主题规则。"""
        rules = []
        palace_themes: dict[str, tuple[str, str]] = {
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
                rule_id=f"{self._method_id.value.upper()}-PALACE-{palace}",
                method_id=self._method_id,
                rule_type=RuleType.PALACE,
                condition={"palace": palace},
                operation={"action": "apply_palace_theme", "theme": theme, "domain": domain},
                confidence=ConfidenceLevel.MEDIUM,
                evidence_refs=(EvidenceRef(
                    rule_id=f"ZW-PALACE-{palace}",
                    source_work="紫微斗数全书",
                    source_chapter="十二宫",
                    verification_status="canonical",
                ),),
            ))
        return rules

    # ── 匹配引擎 ────────────────────────────────────────────────────────────

    def match_patterns(self, chart: FrozenZiweiChart,
                       include_sanfang: bool = False) -> RuleMatchResult:
        """匹配格局规则。

        Args:
            chart: FrozenZiweiChart
            include_sanfang: 是否扩展三方四正（三合派核心）
                             True → 格局匹配范围 = 命宫 + 三方四正星群
                             False → 仅命宫（飞星派常用）
        """
        matches: list[RuleMatch] = []
        unmatched: list[str] = []

        resolver = ZiweiPalaceResolver(chart, self._method_id)

        # 获取命宫主星（中文）
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
            match_stars = list(dict.fromkeys(sanfang_stars))  # 去重保序
        else:
            match_stars = ming_stars_zh

        ming_stars_set = set(match_stars)

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
            method_id=self._method_id,
        )

    def match_sihua(self, chart: FrozenZiweiChart, stem: str) -> RuleMatchResult:
        """匹配四化规则。

        Args:
            chart: FrozenZiweiChart
            stem: 天干（如"庚"），通常是生年干或大限干
        """
        matches: list[RuleMatch] = []
        profile_table = self._profile.get_sihua_table()
        sihua_stars = profile_table.get(stem)
        if not sihua_stars:
            return RuleMatchResult(method_id=self._method_id)

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

        # 构建匹配规则（每条四化一条）
        for sihua_name, star_name in [("化禄", lu), ("化权", quan), ("化科", ke), ("化忌", ji)]:
            palace = star_to_palace.get(star_name, "")
            matches.append(RuleMatch(
                rule_spec=RuleSpec(
                    rule_id=f"{self._method_id.value.upper()}-SIHUA-{stem}-{sihua_name}",
                    method_id=self._method_id,
                    rule_type=RuleType.SIHUA,
                    condition={"stem": stem, sihua_name: star_name},
                    operation={"action": "map_sihua_to_palace", "target_palace": palace},
                    confidence=ConfidenceLevel.HIGH,
                ),
                facts={**facts, "target_palace": palace},
            ))

        return RuleMatchResult(
            matched_rules=tuple(matches),
            method_id=self._method_id,
        )

    def match_all(self, chart: FrozenZiweiChart,
                  resolver: ZiweiPalaceResolver | None = None) -> RuleMatchResult:
        """全量匹配（格局 + 四化 + 宫位）。

        Args:
            chart: FrozenZiweiChart
            resolver: 可选的 PalaceResolver（用于借星逻辑）
        """
        if resolver is None:
            resolver = ZiweiPalaceResolver(chart, self._method_id)

        # 1. 格局匹配
        pattern_result = self.match_patterns(chart)

        # 2. 四化匹配（生年干）
        sihua_result = self._match_natal_sihua(chart)

        # 3. 宫位匹配（全部12宫）
        palace_result = self.match_palace_rules(chart)

        # 合并
        all_matches = list(pattern_result.matched_rules) + \
                      list(sihua_result.matched_rules) + \
                      list(palace_result.matched_rules)

        return RuleMatchResult(
            matched_rules=tuple(all_matches),
            method_id=self._method_id,
        )

    def _match_natal_sihua(self, chart: FrozenZiweiChart) -> RuleMatchResult:
        """匹配生年四化规则。

        生年干 = 出生年份天干，从 chart.birth_year 计算，与命宫宫干严格区分。
        命宫宫干 → 宫干飞化/自化，走飞星路径；不得混入生年四化。
        """
        if chart.birth_year <= 0:
            logger.warning(
                "[RuleGraph] birth_year 未设置，无法计算生年干四化。"
                "请使用 full_chart() 返回的 FrozenZiweiChart（含 birth_year）。"
            )
            return RuleMatchResult(method_id=self._method_id)
        birth_stem = self._stem_from_year(chart.birth_year)
        return self.match_sihua(chart, birth_stem)

    @staticmethod
    def _stem_from_year(year: int) -> str:
        """从西元年号计算天干（4 AD = 甲子）。"""
        stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        return stems[(year - 4) % 10]

    def match_palace_rules(self, chart: FrozenZiweiChart) -> RuleMatchResult:
        """匹配宫位主题规则。"""
        matches = []
        for rule in self._palace_rules:
            palace = rule.condition.get("palace", "")
            if palace in chart.palaces:
                matches.append(RuleMatch(
                    rule_spec=rule,
                    facts={"palace": palace,
                           "stars": chart.palaces[palace].get("major", [])},
                ))
        return RuleMatchResult(
            matched_rules=tuple(matches),
            method_id=self._method_id,
        )

    # ── 属性 ────────────────────────────────────────────────────────────────

    @property
    def method_id(self) -> MethodId:
        return self._method_id

    @property
    def profile(self) -> ZiweiMethodProfile:
        return self._profile

    @property
    def rule_count(self) -> int:
        return len(self._pattern_rules) + len(self._sihua_rules) + len(self._palace_rules)


# ============================================================================
# 工厂函数
# ============================================================================

def create_rule_graph(method_id: MethodId) -> ZiweiRuleGraph:
    """根据 MethodId 创建对应的 RuleGraph 实例。"""
    return ZiweiRuleGraph(method_id)


def batch_match(chart: FrozenZiweiChart,
                method_ids: list[MethodId] | None = None) -> dict[MethodId, RuleMatchResult]:
    """多流派批量匹配（用于同盘异法验证）。"""
    if method_ids is None:
        from ...ziwei_method_profile import MethodId as M
        method_ids = list(M)
    return {mid: create_rule_graph(mid).match_all(chart) for mid in method_ids}
