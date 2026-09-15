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
