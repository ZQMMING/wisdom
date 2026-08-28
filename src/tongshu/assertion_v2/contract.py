"""P6 Assertion Layer V2 Contract - 五引擎原生断言层.

核心原则:
1. 五大引擎各自拥有自己的原生断言层, 不共用统一断语模板
2. 断言层之后才进入统一Mapping / Cross-Engine聚合
3. 互补, 不比较; 各体系不能互相改写
4. 禁止: direction/polarity/pos/neg/confidence/vote/majority/SYSTEM_WEIGHTS
5. 每个NativeJudgment必须带provenance和mapping_hook
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from collections import Counter


class EngineName(str, Enum):
    ZI_PING = "ZI_PING"
    BLIND_SCHOOL = "BLIND_SCHOOL"
    ZI_WEI = "ZI_WEI"
    HE_LUO = "HE_LUO"
    YI_JING = "YI_JING"


class ZiPingJudgmentType(str, Enum):
    PATTERN = "PATTERN"
    DAY_TIME = "DAY_TIME"
    TUNING = "TUNING"
    FUWEN = "FUWEN"
    TEN_GOD = "TEN_GOD"
    STRENGTH = "STRENGTH"
    STEM_BRANCH = "STEM_BRANCH"
    PUNISHMENT_CLASH = "PUNISHMENT_CLASH"
    YEAR_LUCK = "YEAR_LUCK"
    TIMING = "TIMING"


class BlindSchoolJudgmentType(str, Enum):
    DOING_WORK = "DOING_WORK"
    GUEST_HOST = "GUEST_HOST"
    TEN_GOD_PALACE = "TEN_GOD_PALACE"
    PALACE_RELATION = "PALACE_RELATION"
    STEM_BRANCH_COMBO = "STEM_BRANCH_COMBO"
    PUNISHMENT_CLASH = "PUNISHMENT_CLASH"
    GRAVE = "GRAVE"
    BODY_USE = "BODY_USE"
    TIMING = "TIMING"
    MANTRA = "MANTRA"


class ZiWeiJudgmentType(str, Enum):
    TWELVE_PALACES = "TWELVE_PALACES"
    MAJOR_STARS = "MAJOR_STARS"
    MINOR_STARS = "MINOR_STARS"
    SIHUA = "SIHUA"
    PALACE_STAR = "PALACE_STAR"
    SANFANG_SIZHENG = "SANFANG_SIZHENG"
    OPPOSITE_PALACE = "OPPOSITE_PALACE"
    DA_LIMIT = "DA_LIMIT"
    FLOW_YEAR = "FLOW_YEAR"
    FLOW_MONTH = "FLOW_MONTH"
    FLOW_DAY = "FLOW_DAY"
    ANCIENT_MANTRA = "ANCIENT_MANTRA"


class HeLuoJudgmentType(str, Enum):
    PREHEAVEN_HEXAGRAM = "PREHEAVEN_HEXAGRAM"
    YUANTANG = "YUANTANG"
    POSTHEAVEN_HEXAGRAM = "POSTHEAVEN_HEXAGRAM"
    YEAR_HEXAGRAM = "YEAR_HEXAGRAM"
    MONTH_HEXAGRAM = "MONTH_HEXAGRAM"
    DAY_HEXAGRAM = "DAY_HEXAGRAM"
    MOMENT = "MOMENT"
    JIEHOU_HEXAGRAM = "JIEHOU_HEXAGRAM"
    HEXAGRAM_QI = "HEXAGRAM_QI"
    HEXAGRAM_POSITION = "HEXAGRAM_POSITION"
    NUMBER_LOGIC = "NUMBER_LOGIC"
    ANCIENT_MANTRA = "ANCIENT_MANTRA"


class YiJingJudgmentType(str, Enum):
    HEXAGRAM_TEXT = "HEXAGRAM_TEXT"
    YAO_TEXT = "YAO_TEXT"
    TUAN_TEXT = "TUAN_TEXT"
    DA_XIANG = "DA_XIANG"
    XIAO_XIANG = "XIAO_XIANG"
    HUMAN_AFFAIRS = "HUMAN_AFFAIRS"
    POSITION = "POSITION"
    ZHONG_ZHENG = "ZHONG_ZHENG"
    CHENG_CHENG_BI_YING = "CHENG_CHENG_BI_YING"
    CHANGED_HEXAGRAM = "CHANGED_HEXAGRAM"
    DECISION = "DECISION"


ENGINE_JUDGMENT_TYPES = {
    EngineName.ZI_PING: ZiPingJudgmentType,
    EngineName.BLIND_SCHOOL: BlindSchoolJudgmentType,
    EngineName.ZI_WEI: ZiWeiJudgmentType,
    EngineName.HE_LUO: HeLuoJudgmentType,
    EngineName.YI_JING: YiJingJudgmentType,
}


@dataclass(frozen=True)
class JudgmentProvenance:
    source_engine: EngineName
    source_rule_id: str
    source_evidence_ref: Optional[str] = None
    source_work: Optional[str] = None
    source_chapter: Optional[str] = None
    derivation_chain: list[str] = field(default_factory=list)
    calculation_version: str = "2026.08"


@dataclass(frozen=True)
class MappingHook:
    semantic_candidates: list[str] = field(default_factory=list)
    domain_candidates: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class NativeJudgment:
    judgment_id: str
    engine: EngineName
    judgment_type: str
    condition: dict[str, Any]
    canonical_text: str
    source: dict[str, Any] = field(default_factory=dict)
    provenance: JudgmentProvenance = field(default_factory=lambda: JudgmentProvenance(
        source_engine=EngineName.ZI_PING,
        source_rule_id="UNKNOWN",
    ))
    mapping_hook: MappingHook = field(default_factory=MappingHook)

    def __post_init__(self):
        if not self.provenance.source_rule_id or self.provenance.source_rule_id == "UNKNOWN":
            raise ValueError(f"Judgment {self.judgment_id}: provenance.source_rule_id不能为空")
        valid_types = ENGINE_JUDGMENT_TYPES.get(self.engine)
        if valid_types and self.judgment_type not in [t.value for t in valid_types]:
            raise ValueError(f"Judgment {self.judgment_id}: judgment_type '{self.judgment_type}' 不属于引擎 {self.engine.value}")


class JudgmentLibrary:
    def __init__(self):
        self._libraries: dict[EngineName, dict[str, NativeJudgment]] = {e: {} for e in EngineName}

    def add(self, judgment: NativeJudgment) -> None:
        self._libraries[judgment.engine][judgment.judgment_id] = judgment

    def get(self, engine: EngineName, judgment_id: str) -> Optional[NativeJudgment]:
        return self._libraries[engine].get(judgment_id)

    def get_by_engine(self, engine: EngineName) -> list[NativeJudgment]:
        return list(self._libraries[engine].values())

    def get_by_type(self, engine: EngineName, judgment_type: str) -> list[NativeJudgment]:
        return [j for j in self._libraries[engine].values() if j.judgment_type == judgment_type]

    def stats(self) -> dict[str, int]:
        return {e.value: len(lib) for e, lib in self._libraries.items()}


class UnifiedMappingLayer:
    def __init__(self):
        self._domains = ["CAREER", "FINANCE", "RELATIONSHIP", "FAMILY", "HEALTH", "GROWTH", "DECISION", "MIGRATION"]

    def map(self, judgments: list[NativeJudgment]) -> dict[str, Any]:
        clusters: dict[str, dict[str, Any]] = {}
        for j in judgments:
            for domain in j.mapping_hook.domain_candidates:
                if domain not in clusters:
                    clusters[domain] = {"domain": domain, "semantic_keys": set(), "judgments": [], "source_engines": set()}
                clusters[domain]["semantic_keys"].update(j.mapping_hook.semantic_candidates)
                clusters[domain]["judgments"].append(j.judgment_id)
                clusters[domain]["source_engines"].add(j.engine.value)
        result = {}
        for d, c in clusters.items():
            result[d] = {"domain": c["domain"], "semantic_keys": sorted(c["semantic_keys"]), "judgment_ids": c["judgments"], "source_engines": sorted(c["source_engines"]), "evidence_count": len(c["judgments"])}
        return result


class AssertionV2Validator:
    FORBIDDEN = ["direction", "polarity", "pos", "neg", "positive", "negative", "confidence", "score", "weight", "vote", "majority", "SYSTEM_WEIGHTS", "lucky", "unlucky", "good", "bad"]

    @classmethod
    def validate(cls, judgment: NativeJudgment) -> list[str]:
        errors = []
        for fn in ["condition", "source"]:
            fv = getattr(judgment, fn, {})
            if isinstance(fv, dict):
                for k in fv:
                    if k.lower() in cls.FORBIDDEN:
                        errors.append(f"Judgment {judgment.judgment_id}: 禁止字段 '{k}'")
        if not judgment.provenance.source_rule_id or judgment.provenance.source_rule_id == "UNKNOWN":
            errors.append(f"Judgment {judgment.judgment_id}: provenance无效")
        return errors

    @classmethod
    def validate_library(cls, library: JudgmentLibrary) -> dict[str, Any]:
        all_errors = []
        total = 0
        for e in EngineName:
            for j in library.get_by_engine(e):
                total += 1
                all_errors.extend(cls.validate(j))
        return {"valid": len(all_errors) == 0, "total": total, "error_count": len(all_errors), "errors": all_errors, "stats": library.stats()}


if __name__ == "__main__":
    print("P6 Assertion Layer V2 Contract - 快速测试")
    print("=" * 60)
    j = NativeJudgment(
        judgment_id="ZP-PATTERN-001",
        engine=EngineName.ZI_PING,
        judgment_type=ZiPingJudgmentType.PATTERN.value,
        condition={"day_master": "YI", "month": "XU", "pattern": "正财格"},
        canonical_text="乙木戌月，正财格，喜火土，忌水木。",
        source={"work": "子平真诠", "chapter": "论正财格"},
        provenance=JudgmentProvenance(source_engine=EngineName.ZI_PING, source_rule_id="ZP_PATTERN_ZHENG_CAI", source_work="子平真诠", source_chapter="论正财格"),
        mapping_hook=MappingHook(semantic_candidates=["RESOURCE", "STABILITY", "STRUCTURE"], domain_candidates=["CAREER", "FINANCE"]),
    )
    print(f"子平断言: {j.judgment_id} = {j.canonical_text}")
    lib = JudgmentLibrary()
    lib.add(j)
    print(f"断言库统计: {lib.stats()}")
    v = AssertionV2Validator.validate_library(lib)
    print(f"验证: valid={v['valid']}, errors={v['error_count']}")
    m = UnifiedMappingLayer()
    r = m.map([j])
    print(f"映射: {list(r.keys())}")
    print("\nP6 Assertion Layer V2 Contract 测试通过")
