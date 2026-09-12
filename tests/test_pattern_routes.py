# -*- coding: utf-8 -*-
"""P5 八族25路线召回 — 铁律合规 + 十神映射 + 召回行为 测试."""
import sys
sys.path.insert(0, ".")
import pytest
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3.pattern_routes import (
    ten_god_of, PatternRouteRecaller,
)

GAN = {"JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
       "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"}

# 手工对账基准 (乙日主)
YI_EXPECT = {"JIA": "劫财", "YI": "比肩", "BING": "伤官", "DING": "食神",
             "WU": "偏财", "JI": "正财", "GENG": "七杀", "XIN": "正官",
             "REN": "偏印", "GUI": "正印"}
# 丙日主
BING_EXPECT = {"JIA": "正印", "YI": "偏印", "BING": "比肩", "DING": "劫财",
               "WU": "食神", "JI": "伤官", "GENG": "正财", "XIN": "偏财",
               "REN": "正官", "GUI": "七杀"}


def test_ten_god_mapping():
    for s in GAN:
        assert ten_god_of("YI", s) == YI_EXPECT[s], f"乙日主 {s} 误"
        assert ten_god_of("BING", s) == BING_EXPECT[s], f"丙日主 {s} 误"


def test_unknown_day_master_fail_closed():
    assert ten_god_of("XX", "JIA") == ""


def test_recall_fail_closed_and_enum():
    BE = BaziEngine()
    rec = PatternRouteRecaller()
    c = BE.compute((1983, 11, 3, 12), gender="male")
    chart_info = {
        "day_master": c.day_pillar.heavenly_stem,
        "four_stems": [p.heavenly_stem for p in [c.year_pillar, c.month_pillar, c.day_pillar, c.hour_pillar]],
        "four_branches": [p.earthly_branch for p in [c.year_pillar, c.month_pillar, c.day_pillar, c.hour_pillar]],
        "hidden_stems": getattr(c, "hidden_stems", {}),
        "hour_known": True,
    }
    recalls = rec.recall(chart_info)
    # 状态枚举契约: 只能是三类
    for r in recalls:
        assert r.status in ("CANDIDATE", "PENDING_REVIEW", "NOT_TRIGGERED")
        # 有例外条款必标 fail-closed
        if r.exceptions_unlocated:
            assert r.status != "CANDIDATE"  # 例外未消解 → 不得直报 CANDIDATE
    # 1983 乙木局应有召回
    assert len(recalls) >= 1


def test_recall_empty_chart_not_triggered():
    rec = PatternRouteRecaller()
    # 空四柱 → full_chart 必失败 → 无召回
    assert rec.recall({"day_master": "YI", "four_stems": [], "hidden_stems": {}, "hour_known": True}) == []


if __name__ == "__main__":
    test_ten_god_mapping()
    test_unknown_day_master_fail_closed()
    test_recall_fail_closed_and_enum()
    test_recall_empty_chart_not_triggered()
    print("P5 路线召回测试 ALL PASS")
