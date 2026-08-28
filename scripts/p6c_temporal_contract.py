"""P6-C Temporal Evaluation Contract.

Temporal Contract:
- 输入: Case + Target Year
- Temporal Context: target_year, 流年干支, 流年十神, 地支关系
- 接入现有P0-P5 Frozen Pipeline (P4 Structural Assertions)
- 输出: Temporal CanonicalAssertion {domain, semantic_family, direction, source_trace}
- 第一版禁止生成自然语言事件
- 不修改P4/P5既有语义
- 不迁移盲派/紫微
- 不修改Golden Ground Truth V2
- 不针对结果优化规则
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field
from typing import Optional
sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from tongshu.api.app import create_app
from tongshu.engines.bazi_engine import BaziEngine

app = create_app()
client = TestClient(app)

# 天干地支
HEAVENLY_STEMS = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
EARTHLY_BRANCHES = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]

# 十神关系 (日主天干 -> 流年天干 -> 十神)
TEN_GOD_MAP = {
    # 同我者: 比肩/劫财
    ("JIA", "JIA"): "BIJIAN", ("JIA", "YI"): "JIECAI",
    ("YI", "YI"): "BIJIAN", ("YI", "JIA"): "JIECAI",
    ("BING", "BING"): "BIJIAN", ("BING", "DING"): "JIECAI",
    ("DING", "DING"): "BIJIAN", ("DING", "BING"): "JIECAI",
    ("WU", "WU"): "BIJIAN", ("WU", "JI"): "JIECAI",
    ("JI", "JI"): "BIJIAN", ("JI", "WU"): "JIECAI",
    ("GENG", "GENG"): "BIJIAN", ("GENG", "XIN"): "JIECAI",
    ("XIN", "XIN"): "BIJIAN", ("XIN", "GENG"): "JIECAI",
    ("REN", "REN"): "BIJIAN", ("REN", "GUI"): "JIECAI",
    ("GUI", "GUI"): "BIJIAN", ("GUI", "REN"): "JIECAI",
    # 我生者: 食神/伤官
    ("JIA", "BING"): "SHISHEN", ("JIA", "DING"): "SHANGGUAN",
    ("YI", "DING"): "SHISHEN", ("YI", "BING"): "SHANGGUAN",
    ("BING", "WU"): "SHISHEN", ("BING", "JI"): "SHANGGUAN",
    ("DING", "JI"): "SHISHEN", ("DING", "WU"): "SHANGGUAN",
    ("WU", "GENG"): "SHISHEN", ("WU", "XIN"): "SHANGGUAN",
    ("JI", "XIN"): "SHISHEN", ("JI", "GENG"): "SHANGGUAN",
    ("GENG", "REN"): "SHISHEN", ("GENG", "GUI"): "SHANGGUAN",
    ("XIN", "GUI"): "SHISHEN", ("XIN", "REN"): "SHANGGUAN",
    ("REN", "JIA"): "SHISHEN", ("REN", "YI"): "SHANGGUAN",
    ("GUI", "YI"): "SHISHEN", ("GUI", "JIA"): "SHANGGUAN",
    # 我克者: 偏财/正财
    ("JIA", "WU"): "PIANCAI", ("JIA", "JI"): "ZHENGCAI",
    ("YI", "JI"): "PIANCAI", ("YI", "WU"): "ZHENGCAI",
    ("BING", "GENG"): "PIANCAI", ("BING", "XIN"): "ZHENGCAI",
    ("DING", "XIN"): "PIANCAI", ("DING", "GENG"): "ZHENGCAI",
    ("WU", "REN"): "PIANCAI", ("WU", "GUI"): "ZHENGCAI",
    ("JI", "GUI"): "PIANCAI", ("JI", "REN"): "ZHENGCAI",
    ("GENG", "JIA"): "PIANCAI", ("GENG", "YI"): "ZHENGCAI",
    ("XIN", "YI"): "PIANCAI", ("XIN", "JIA"): "ZHENGCAI",
    ("REN", "BING"): "PIANCAI", ("REN", "DING"): "ZHENGCAI",
    ("GUI", "DING"): "PIANCAI", ("GUI", "BING"): "ZHENGCAI",
    # 克我者: 七杀/正官
    ("JIA", "GENG"): "QISHA", ("JIA", "XIN"): "ZHENGGUAN",
    ("YI", "XIN"): "QISHA", ("YI", "GENG"): "ZHENGGUAN",
    ("BING", "REN"): "QISHA", ("BING", "GUI"): "ZHENGGUAN",
    ("DING", "GUI"): "QISHA", ("DING", "REN"): "ZHENGGUAN",
    ("WU", "JIA"): "QISHA", ("WU", "YI"): "ZHENGGUAN",
    ("JI", "YI"): "QISHA", ("JI", "JIA"): "ZHENGGUAN",
    ("GENG", "BING"): "QISHA", ("GENG", "DING"): "ZHENGGUAN",
    ("XIN", "DING"): "QISHA", ("XIN", "BING"): "ZHENGGUAN",
    ("REN", "WU"): "QISHA", ("REN", "JI"): "ZHENGGUAN",
    ("GUI", "JI"): "QISHA", ("GUI", "WU"): "ZHENGGUAN",
    # 生我者: 偏印/正印
    ("JIA", "REN"): "PIANYIN", ("JIA", "GUI"): "ZHENGYIN",
    ("YI", "GUI"): "PIANYIN", ("YI", "REN"): "ZHENGYIN",
    ("BING", "JIA"): "PIANYIN", ("BING", "YI"): "ZHENGYIN",
    ("DING", "YI"): "PIANYIN", ("DING", "JIA"): "ZHENGYIN",
    ("WU", "BING"): "PIANYIN", ("WU", "DING"): "ZHENGYIN",
    ("JI", "DING"): "PIANYIN", ("JI", "BING"): "ZHENGYIN",
    ("GENG", "WU"): "PIANYIN", ("GENG", "JI"): "ZHENGYIN",
    ("XIN", "JI"): "PIANYIN", ("XIN", "WU"): "ZHENGYIN",
    ("REN", "GENG"): "PIANYIN", ("REN", "XIN"): "ZHENGYIN",
    ("GUI", "XIN"): "PIANYIN", ("GUI", "GENG"): "ZHENGYIN",
}

# 地支六冲
BRANCH_CLASH = {
    "ZI": "WU", "WU": "ZI",
    "CHOU": "WEI", "WEI": "CHOU",
    "YIN": "SHEN", "SHEN": "YIN",
    "MAO": "YOU", "YOU": "MAO",
    "CHEN": "XU", "XU": "CHEN",
    "SI": "HAI", "HAI": "SI",
}

# 地支六合
BRANCH_HEXAGRAM = {
    "ZI": "CHOU", "CHOU": "ZI",
    "YIN": "HAI", "HAI": "YIN",
    "MAO": "XU", "XU": "MAO",
    "CHEN": "YOU", "YOU": "CHEN",
    "SI": "SHEN", "SHEN": "SI",
    "WU": "WEI", "WEI": "WU",
}

# 十神 -> domain/semantic_family/direction映射 (第一版基础映射)
TEN_GOD_TEMPORAL_MAP = {
    "SHANGGUAN": {"domain": "CAREER", "semantic_family": "OUTPUT_EXPRESSION", "direction": "supportive"},
    "SHISHEN": {"domain": "GROWTH", "semantic_family": "OUTPUT_EXPRESSION", "direction": "supportive"},
    "ZHENGCAI": {"domain": "FINANCE", "semantic_family": "RESOURCE_WEALTH", "direction": "supportive"},
    "PIANCAI": {"domain": "FINANCE", "semantic_family": "RESOURCE_WEALTH", "direction": "supportive"},
    "ZHENGGUAN": {"domain": "CAREER", "semantic_family": "CONSTRAINT_RULE", "direction": "caution"},
    "QISHA": {"domain": "CAREER", "semantic_family": "CHANGE_TRANSFORMATION", "direction": "caution"},
    "ZHENGYIN": {"domain": "GROWTH", "semantic_family": "STABILITY_SUPPORT", "direction": "supportive"},
    "PIANYIN": {"domain": "GROWTH", "semantic_family": "STABILITY_SUPPORT", "direction": "neutral"},
    "BIJIAN": {"domain": "CAREER", "semantic_family": "RELATION_CONNECTION", "direction": "neutral"},
    "JIECAI": {"domain": "FINANCE", "semantic_family": "CHANGE_TRANSFORMATION", "direction": "caution"},
}


@dataclass
class TemporalContext:
    """Temporal Context - 可追溯."""
    target_year: int
    year_stem: str  # 流年天干
    year_branch: str  # 流年地支
    day_master: str  # 日主天干
    ten_god: str  # 流年十神
    branch_relations: list[str] = field(default_factory=list)  # 与本命地支的关系
    source_evidence_ids: list[str] = field(default_factory=list)
    temporal_rule_ids: list[str] = field(default_factory=list)


@dataclass
class TemporalAssertion:
    """Temporal CanonicalAssertion - 结构化输出."""
    case_id: str
    target_year: int
    domain: str
    semantic_family: str
    direction: str  # supportive/caution/neutral
    ten_god: str
    branch_relations: list[str]
    source_trace: dict  # 完整追溯链
    status: str = "READY"  # READY/NOT_READY/UNRESOLVED


def compute_year_pillar(year: int) -> tuple[str, str]:
    """计算流年干支."""
    # 1984年是甲子年, 作为基准
    base_year = 1984
    offset = year - base_year
    stem_idx = offset % 10
    branch_idx = offset % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def compute_ten_god(day_master: str, year_stem: str) -> str:
    """计算流年十神."""
    return TEN_GOD_MAP.get((day_master, year_stem), "UNKNOWN")


def compute_branch_relations(year_branch: str, natal_branches: list[str]) -> list[str]:
    """计算流年地支与本命地支的关系."""
    relations = []
    for nb in natal_branches:
        if BRANCH_CLASH.get(year_branch) == nb:
            relations.append(f"CLASH_WITH_{nb}")
        if BRANCH_HEXAGRAM.get(year_branch) == nb:
            relations.append(f"HEXAGRAM_WITH_{nb}")
        if year_branch == nb:
            relations.append(f"FUYIN_{nb}")
    return relations


def generate_temporal_assertion(
    case_id: str,
    target_year: int,
    day_master: str,
    natal_branches: list[str],
) -> TemporalAssertion:
    """生成Temporal Assertion (第一版基础映射)."""
    year_stem, year_branch = compute_year_pillar(target_year)
    ten_god = compute_ten_god(day_master, year_stem)
    branch_relations = compute_branch_relations(year_branch, natal_branches)

    # 基础映射
    mapping = TEN_GOD_TEMPORAL_MAP.get(ten_god, {
        "domain": "GROWTH", "semantic_family": "REFLECTION_GROWTH", "direction": "neutral"
    })

    # 地支关系调整direction
    direction = mapping["direction"]
    if any("CLASH" in r for r in branch_relations):
        direction = "caution"
    elif any("FUYIN" in r for r in branch_relations):
        direction = "neutral"

    temporal_ctx = TemporalContext(
        target_year=target_year,
        year_stem=year_stem,
        year_branch=year_branch,
        day_master=day_master,
        ten_god=ten_god,
        branch_relations=branch_relations,
        temporal_rule_ids=[f"TEMPORAL_TEN_GOD_{ten_god}"],
    )

    return TemporalAssertion(
        case_id=case_id,
        target_year=target_year,
        domain=mapping["domain"],
        semantic_family=mapping["semantic_family"],
        direction=direction,
        ten_god=ten_god,
        branch_relations=branch_relations,
        source_trace={
            "temporal_context": temporal_ctx.__dict__,
            "mapping_rule": f"TEN_GOD_{ten_god}_TO_TEMPORAL",
            "branch_adjustment": branch_relations,
        },
        status="READY",
    )


def get_natal_info(case_id: str) -> tuple[str, list[str]]:
    """从已计算的case中获取日主和本命地支."""
    resp = client.get(f"/admin/cases/{case_id}")
    if resp.status_code != 200:
        return "YI", ["HAI", "XU", "WEI", "WU"]  # 默认

    data = resp.json()
    # 从evidence中提取日主和地支
    evidence = data.get("evidence", [])
    day_master = "YI"
    branches = []

    for ev in evidence:
        if ev.get("rule_id") == "ZP_DAY_MASTER" or "day_master" in ev.get("rule_id", "").lower():
            day_master = ev.get("value", "YI")
        if "branch" in ev.get("rule_id", "").lower() or "地支" in ev.get("value", ""):
            val = ev.get("value", "")
            for b in EARTHLY_BRANCHES:
                if b in val or b.lower() in val.lower():
                    if b not in branches:
                        branches.append(b)

    if not branches:
        branches = ["HAI", "XU", "WEI", "WU"]  # 默认

    return day_master, branches


if __name__ == "__main__":
    # 测试
    print("Temporal Contract测试:")
    for year in [1980, 1983, 1990, 2000, 2010, 2020, 2026]:
        stem, branch = compute_year_pillar(year)
        tg = compute_ten_god("YI", stem)
        print(f"  {year}: {stem}{branch}, 十神={tg}")
