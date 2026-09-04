"""P6-C-3C-0 Judgment Architecture Reset - 体系/经典层级契约.

核心修正:
- 子平不能作为单一断言引擎, 必须拆成五部经典
- 五部经典各自拥有独立的规则/断言资产与索引路径
- 排盘计算只有一套(Bazi Feature Graph), 五部经典各自Resolver
- 不同经典的Matcher不能完全一样
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class DivinationSystem(str, Enum):
    ZI_PING = "ZI_PING"
    BLIND_SCHOOL = "BLIND_SCHOOL"
    ZI_WEI = "ZI_WEI"
    HE_LUO = "HE_LUO"
    YI_JING = "YI_JING"


class ZiPingSchool(str, Enum):
    DI_TIAN_SUI = "DI_TIAN_SUI"
    ZI_PING_ZHEN_QUAN = "ZI_PING_ZHEN_QUAN"
    QIONG_TONG_BAO_JIAN = "QIONG_TONG_BAO_JIAN"
    YUAN_HAI_ZI_PING = "YUAN_HAI_ZI_PING"
    SAN_MING_TONG_HUI = "SAN_MING_TONG_HUI"


ZIPING_SCHOOL_NAMES = {
    ZiPingSchool.DI_TIAN_SUI: "滴天髓",
    ZiPingSchool.ZI_PING_ZHEN_QUAN: "子平真诠",
    ZiPingSchool.QIONG_TONG_BAO_JIAN: "穷通宝鉴",
    ZiPingSchool.YUAN_HAI_ZI_PING: "渊海子平",
    ZiPingSchool.SAN_MING_TONG_HUI: "三命通会",
}


@dataclass(frozen=True)
class SchoolIndexPath:
    school: str
    name_zh: str
    core_features: list[str]
    judgment_types: list[str]
    matcher_types: list[str]
    description: str = ""


ZIPING_SCHOOL_INDEX_PATHS = {
    ZiPingSchool.DI_TIAN_SUI: SchoolIndexPath(
        school=ZiPingSchool.DI_TIAN_SUI.value, name_zh="滴天髓",
        core_features=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.FIVE_ELEMENT_BALANCE", "ZP.BRANCH_CLASH_MAP", "ZP.BRANCH_HE_MAP"],
        judgment_types=["STRENGTH", "QI_SHI", "STRUCTURE_LEVEL", "STEM_IMAGE"],
        matcher_types=["CONDITION", "COMPOSITE", "GRAPH"],
        description="日主 → 五行气势 → 强弱 → 结构层次 → 十干取象",
    ),
    ZiPingSchool.ZI_PING_ZHEN_QUAN: SchoolIndexPath(
        school=ZiPingSchool.ZI_PING_ZHEN_QUAN.value, name_zh="子平真诠",
        core_features=["ZP.MONTH_BRANCH", "ZP.MONTH_STEM", "ZP.DAY_MASTER", "ZP.BRANCH_SANHE_MAP"],
        judgment_types=["PATTERN", "PATTERN_SUCCESS", "PATTERN_FAILURE", "USE_GOD", "MONTH_ORDER"],
        matcher_types=["CONDITION", "EXACT", "COMPOSITE"],
        description="月令 → 格局 → 成败 → 用神",
    ),
    ZiPingSchool.QIONG_TONG_BAO_JIAN: SchoolIndexPath(
        school=ZiPingSchool.QIONG_TONG_BAO_JIAN.value, name_zh="穷通宝鉴",
        core_features=["ZP.DAY_MASTER", "ZP.MONTH_BRANCH", "ZP.YEAR_STEM", "ZP.HOUR_STEM"],
        judgment_types=["TUNING", "CLIMATE", "SEASON_ENVIRONMENT", "MONTH_TUNING"],
        matcher_types=["CONDITION", "EXACT", "COMPOSITE"],
        description="日主 → 月令 → 调候 → 寒暖燥湿",
    ),
    ZiPingSchool.YUAN_HAI_ZI_PING: SchoolIndexPath(
        school=ZiPingSchool.YUAN_HAI_ZI_PING.value, name_zh="渊海子平",
        core_features=["ZP.YEAR_STEM", "ZP.MONTH_STEM", "ZP.DAY_STEM", "ZP.HOUR_STEM", "ZP.DAY_BRANCH_MAIN_TEN_GOD"],
        judgment_types=["TEN_GOD", "TEN_GOD_STRUCTURE", "PATTERN_BASIC", "FU_WEN", "BASIC_METHOD"],
        matcher_types=["CONDITION", "SET", "COMPOSITE"],
        description="十神 → 格局 → 组合 → 赋文",
    ),
    ZiPingSchool.SAN_MING_TONG_HUI: SchoolIndexPath(
        school=ZiPingSchool.SAN_MING_TONG_HUI.value, name_zh="三命通会",
        core_features=["ZP.DAY_PILLAR", "ZP.HOUR_PILLAR", "ZP.DAY_STEM", "ZP.HOUR_STEM"],
        judgment_types=["DAY_TIME", "DAY_PILLAR", "HOUR_PILLAR", "SIXTY_JIAZI", "DAY_TIME_COMBO"],
        matcher_types=["EXACT", "CONDITION", "COMPOSITE"],
        description="日柱 → 时柱 → 组合 → 六十甲子 → 日时断",
    ),
}


class MatcherType(str, Enum):
    EXACT = "EXACT"
    SET = "SET"
    RANGE = "RANGE"
    ALL = "ALL"
    ANY = "ANY"
    GRAPH = "GRAPH"
    CONDITION = "CONDITION"
    COMPOSITE = "COMPOSITE"


@dataclass(frozen=True)
class SystemSchoolRegistry:
    system: str
    schools: dict[str, SchoolIndexPath] = field(default_factory=dict)

    def get_school(self, school: str) -> Optional[SchoolIndexPath]:
        return self.schools.get(school)

    def list_schools(self) -> list[str]:
        return list(self.schools.keys())

    def stats(self) -> dict[str, Any]:
        return {
            "system": self.system, "school_count": len(self.schools),
            "schools": {s: {"name_zh": p.name_zh, "judgment_types": p.judgment_types, "matcher_types": p.matcher_types, "core_features": p.core_features} for s, p in self.schools.items()},
        }


SYSTEM_REGISTRY: dict[str, SystemSchoolRegistry] = {
    DivinationSystem.ZI_PING.value: SystemSchoolRegistry(system=DivinationSystem.ZI_PING.value, schools={s.value: p for s, p in ZIPING_SCHOOL_INDEX_PATHS.items()}),
    DivinationSystem.BLIND_SCHOOL.value: SystemSchoolRegistry(system=DivinationSystem.BLIND_SCHOOL.value, schools={}),
    DivinationSystem.ZI_WEI.value: SystemSchoolRegistry(system=DivinationSystem.ZI_WEI.value, schools={}),
    DivinationSystem.HE_LUO.value: SystemSchoolRegistry(system=DivinationSystem.HE_LUO.value, schools={}),
    DivinationSystem.YI_JING.value: SystemSchoolRegistry(system=DivinationSystem.YI_JING.value, schools={}),
}


def get_ziping_index_paths_for_case(features: dict[str, Any]) -> dict[str, dict[str, Any]]:
    paths = {}
    paths["PATTERN_PATH"] = {"school": ZiPingSchool.ZI_PING_ZHEN_QUAN.value, "name_zh": "子平真诠 - 格局路径", "input_features": {"day_master": features.get("ZP.DAY_MASTER"), "month_branch": features.get("ZP.MONTH_BRANCH"), "month_stem": features.get("ZP.MONTH_STEM")}, "judgment_types": ["PATTERN", "PATTERN_SUCCESS", "PATTERN_FAILURE", "USE_GOD"], "matcher": "CONDITION"}
    paths["DAY_TIME_PATH"] = {"school": ZiPingSchool.SAN_MING_TONG_HUI.value, "name_zh": "三命通会 - 日时路径", "input_features": {"day_pillar": features.get("ZP.DAY_PILLAR"), "hour_pillar": features.get("ZP.HOUR_PILLAR"), "day_stem": features.get("ZP.DAY_STEM"), "hour_stem": features.get("ZP.HOUR_STEM")}, "judgment_types": ["DAY_TIME", "DAY_PILLAR", "HOUR_PILLAR"], "matcher": "EXACT"}
    paths["TUNING_PATH"] = {"school": ZiPingSchool.QIONG_TONG_BAO_JIAN.value, "name_zh": "穷通宝鉴 - 调候路径", "input_features": {"day_master": features.get("ZP.DAY_MASTER"), "month_branch": features.get("ZP.MONTH_BRANCH"), "year_stem": features.get("ZP.YEAR_STEM"), "hour_stem": features.get("ZP.HOUR_STEM")}, "judgment_types": ["TUNING", "CLIMATE", "SEASON_ENVIRONMENT"], "matcher": "CONDITION"}
    paths["TEN_GOD_PATH"] = {"school": ZiPingSchool.YUAN_HAI_ZI_PING.value, "name_zh": "渊海子平 - 十神路径", "input_features": {"year_stem": features.get("ZP.YEAR_STEM"), "month_stem": features.get("ZP.MONTH_STEM"), "day_stem": features.get("ZP.DAY_STEM"), "hour_stem": features.get("ZP.HOUR_STEM"), "day_branch_main_ten_god": features.get("ZP.DAY_BRANCH_MAIN_TEN_GOD")}, "judgment_types": ["TEN_GOD", "TEN_GOD_STRUCTURE", "FU_WEN"], "matcher": "SET"}
    paths["STRENGTH_PATH"] = {"school": ZiPingSchool.DI_TIAN_SUI.value, "name_zh": "滴天髓 - 强弱/气势路径", "input_features": {"day_master": features.get("ZP.DAY_MASTER"), "month_branch": features.get("ZP.MONTH_BRANCH"), "branch_clash_map": features.get("ZP.BRANCH_CLASH_MAP"), "branch_he_map": features.get("ZP.BRANCH_HE_MAP")}, "judgment_types": ["STRENGTH", "QI_SHI", "STRUCTURE_LEVEL", "STEM_IMAGE"], "matcher": "GRAPH"}
    return paths


if __name__ == "__main__":
    print("=" * 70)
    print("P6-C-3C-0 Judgment Architecture Reset")
    print("=" * 70)
    print("\n[1] 体系注册表:")
    for system, registry in SYSTEM_REGISTRY.items():
        print(f"  {system}: {registry.stats()['school_count']} 部经典")
        if system == DivinationSystem.ZI_PING.value:
            for school, path in registry.schools.items():
                print(f"    - {ZIPING_SCHOOL_NAMES[ZiPingSchool(school)]} ({school})")
                print(f"      核心索引: {path.description}")
                print(f"      断言类型: {path.judgment_types}")
                print(f"      Matcher: {path.matcher_types}")
    print("\n[2] 1983案例五条索引路径:")
    sample_features = {"ZP.DAY_MASTER": "YI", "ZP.MONTH_BRANCH": "XU", "ZP.MONTH_STEM": "REN", "ZP.DAY_PILLAR": "YI_WEI", "ZP.HOUR_PILLAR": "REN_WU", "ZP.DAY_STEM": "YI", "ZP.HOUR_STEM": "REN", "ZP.YEAR_STEM": "GUI", "ZP.DAY_BRANCH_MAIN_TEN_GOD": "正财"}
    paths = get_ziping_index_paths_for_case(sample_features)
    for path_key, path in paths.items():
        print(f"\n  {path_key}: {path['name_zh']}")
        print(f"    School: {path['school']}")
        print(f"    Matcher: {path['matcher']}")
        print(f"    Judgment Types: {path['judgment_types']}")
    print("\n" + "=" * 70)
    print("P6-C-3C-0 完成")
    print("=" * 70)
