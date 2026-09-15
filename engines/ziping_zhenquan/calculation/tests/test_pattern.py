"""PZZQ 月令取格派生测试（《子平真诠·论用神》）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from engines.ziping_zhenquan.calculation.pattern import derive_pattern  # noqa: E402


def test_benqi_cai_ge():
    """甲日丑月：丑本气己（正財）→ 財格。"""
    assert derive_pattern("甲", "丑") == "財格"


def test_benqi_zhengguan_ge():
    """甲日酉月：酉本气辛（正官）→ 正官格。"""
    assert derive_pattern("甲", "酉") == "正官格"


def test_benqi_qisha_ge():
    """乙日酉月：酉本气辛（七殺）→ 七煞格。"""
    assert derive_pattern("乙", "酉") == "七煞格"


def test_benqi_yin_ge():
    """甲日子月：子本气癸（正印）→ 印格。"""
    assert derive_pattern("甲", "子") == "印格"


def test_jianlu_yuedong():
    """甲日寅月：寅本气甲（比肩，月與日同）→ 建祿月劫格。"""
    assert derive_pattern("甲", "寅") == "建祿月劫格"


def test_yangren_ge():
    """甲日卯月：卯本气乙（劫財）且卯为甲之阳刃 → 陽刃格。"""
    assert derive_pattern("甲", "卯") == "陽刃格"


def test_yuedong_feiren():
    """乙日寅月：寅本气甲（劫財），寅非乙之刃 → 建祿月劫格。"""
    assert derive_pattern("乙", "寅") == "建祿月劫格"


def test_hidden_stems_override():
    """L0 hidden_stems 优先于内置表。"""
    hidden = {"卯": ["甲"]}
    assert derive_pattern("甲", "卯", hidden=hidden) == "建祿月劫格"


# ---- 透干第二层（《论用神变化》第27页）----

def test_tougan_zhongqi_zuozhu():
    """己日申月，本气庚（傷官）不透，透中气壬 → 化財（原文例）。"""
    assert derive_pattern("己", "申", transparent_stems=["壬"]) == "財格"


def test_tougan_yuqi_huaguan():
    """辛日寅月，本气甲（財）不透，透丙 → 化財為官（原文例）。"""
    assert derive_pattern("辛", "寅", transparent_stems=["丙"]) == "正官格"


def test_benqi_tou_bushi_benge():
    """辛日寅月，本气甲透又透丙 → 仍正財格，官为兼格（原文例）。"""
    assert derive_pattern("辛", "寅", transparent_stems=["甲", "丙"]) == "財格"


def test_yuedong_tou_cai():
    """乙日寅月（月劫），透戊 → 化為財（原文例）。"""
    assert derive_pattern("乙", "寅", transparent_stems=["戊"]) == "財格"


def test_piancai_tou_sha():
    """丙日申月，本气庚（偏財）不透，透壬 → 化為煞（原文例）。"""
    assert derive_pattern("丙", "申", transparent_stems=["壬"]) == "七煞格"


def test_qisha_tou_yin():
    """壬日戌月，本气戊（七煞）不透，透辛 → 化煞為印（原文例）。"""
    assert derive_pattern("壬", "戌", transparent_stems=["辛"]) == "印格"


def test_benqi_butou_bu_bian():
    """丙日寅月，本气甲（印）不透干 → 仍為印綬（原文例）。"""
    assert derive_pattern("丙", "寅", transparent_stems=["庚"]) == "印格"


def test_duotou_order_uncertain():
    """丁日亥月，藏壬甲，透壬透甲（本气壬透）→ 本气定格（正官）。"""
    assert derive_pattern("丁", "亥", transparent_stems=["甲", "壬"]) == "正官格"


def test_facts_builder_injects_pattern():
    """FactsBuilder(engine=pzzq) 注入 pattern 字段。"""
    from engines.common.facts_builder import FactsBuilder
    fb = FactsBuilder(engine="pzzq")
    chart = {
        "canonical_input": {"ref": "t", "hash": "y" * 12},
        "pillars": {
            "year": {"stem": "甲", "branch": "子"},
            "month": {"stem": "丙", "branch": "酉"},
            "day": {"stem": "甲", "branch": "午"},
            "hour": {"stem": "戊", "branch": "午"},
        },
        "gender": "男",
        "xunkong": {"xun": "甲午旬"},
        "shishen": {"day_branch_hidden": ["丁"]},
        "changsheng": {}, "nayin": {}, "relations": {},
    }
    r = fb.build(chart)
    # pattern 规则（CAND-PZZQ-059 正官格→avoid 刑衝破害）应触发
    from engines.ziping_zhenquan.calculation.pattern import derive_pattern
    assert derive_pattern("甲", "酉") == "正官格"
    assert r.engine == "ZIPING_ZHENQUAN"
    assert len(r.facts.basic_structure_facts) >= 0
