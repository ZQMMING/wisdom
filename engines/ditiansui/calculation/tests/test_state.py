"""DTS 基础态势派生测试（Phase 6 §65 ·《滴天髓》001-009/018-019）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from engines.common.facts_builder import FactsBuilder  # noqa: E402
from engines.ditiansui.calculation.state import derive_state  # noqa: E402


def build(chart):
    return FactsBuilder(engine="dts").build(chart)


def vals(res, field):
    return {f["value"] for f in res.facts.basic_structure_facts if f["field"] == field}


BASE = {
    "canonical_input": {"ref": "t", "hash": "x" * 12},
    "gender": "男", "xunkong": {"xun": "甲午旬"},
    "shishen": {}, "changsheng": {}, "nayin": {}, "hidden_stems": {},
    "relations": {},
}


def chart(pillars, relations=None):
    c = dict(BASE)
    c["pillars"] = pillars
    c["relations"] = relations or {}
    return c


def test_derive_state_stem():
    out = derive_state(day_stem="丙", month_branch="寅")
    assert out["stem"] == "丙" and out["stem_yinyang"] == "陽"
    out2 = derive_state(day_stem="癸", month_branch="卯")
    assert out2["stem_yinyang"] == "陰"
    assert derive_state(day_stem="甲", month_branch="寅")["branch_yinyang"] == "陽"


def test_dts_001_002_yinyang_extremity():
    """丙→陽之至；癸→陰之至（《滴天髓·天干》）"""
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "丙", "branch": "申"},
        "hour": {"stem": "庚", "branch": "寅"},
    }))
    assert "陽之至" in vals(res, "stem_yang_extremity")
    res2 = build(chart({
        "year": {"stem": "壬", "branch": "申"},
        "month": {"stem": "癸", "branch": "亥"},
        "day": {"stem": "癸", "branch": "卯"},
        "hour": {"stem": "乙", "branch": "未"},
    }))
    assert "陰之至" in vals(res2, "stem_yin_extremity")


def test_dts_003_004_stem_behavior():
    """阳干從氣不從勢；阴干從勢（《滴天髓·天干》）"""
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "庚", "branch": "寅"},
    }))
    assert "從氣不從勢" in vals(res, "stem_behavior")
    res2 = build(chart({
        "year": {"stem": "壬", "branch": "申"},
        "month": {"stem": "癸", "branch": "亥"},
        "day": {"stem": "乙", "branch": "卯"},
        "hour": {"stem": "辛", "branch": "未"},
    }))
    assert "從勢" in vals(res2, "stem_behavior")


def test_dts_005_006_branch_behavior():
    """阳支動強速達；阴支靜專否泰（《滴天髓·地支》；口径：月支）"""
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "庚", "branch": "寅"},
    }))
    assert "動強速達" in vals(res, "branch_behavior")
    res2 = build(chart({
        "year": {"stem": "壬", "branch": "申"},
        "month": {"stem": "癸", "branch": "卯"},
        "day": {"stem": "癸", "branch": "亥"},
        "hour": {"stem": "乙", "branch": "未"},
    }))
    assert "靜專否泰經年" in vals(res2, "branch_behavior")


def test_dts_007_shengsheng_ji_chong():
    """寅申巳亥生方 + 沖 → 生方忌沖動（《滴天髓·地支》）。

    注：CAND-DTS-007 为 suppress 规则（RuleEngine 只消费 emit），此处验证
    前置字段注入（relation=沖）正确 + suppress 规则被正确忽略（不产 fact）。
    """
    chart_ = chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "庚", "branch": "子"},
    }, relations={"liu_chong": ["寅申"]})
    res = build(chart_)
    assert res.metadata["view"]["relation"] == "沖"
    # suppress 不产 fact（预期行为；suppress 语义待审批裁决）
    assert "生方忌沖動" not in vals(res, "branch_phase")


def test_dts_008_ku_chong_kai():
    """辰戌丑未墓库 → 庫宜沖則開（《滴天髓·地支》）"""
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "丙", "branch": "辰"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "庚", "branch": "戌"},
    }))
    assert "庫宜沖則開" in vals(res, "branch_phase")


def test_dts_009_relation_weight():
    """沖 → 关系权重重"""
    res = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "庚", "branch": "子"},
    }, relations={"liu_chong": ["寅申"]}))
    assert "重" in vals(res, "relation_weight")


def test_dts_018_019_pillar_nature():
    """甲申/戊寅 殺印相生；癸丑/庚寅 坐兩神興旺（《滴天髓·干支总论》）"""
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "庚", "branch": "寅"},
    }))
    assert "殺印相生" in vals(res, "pillar_nature")
    res2 = build(chart({
        "year": {"stem": "壬", "branch": "申"},
        "month": {"stem": "癸", "branch": "亥"},
        "day": {"stem": "癸", "branch": "丑"},
        "hour": {"stem": "乙", "branch": "未"},
    }))
    assert "坐兩神興旺" in vals(res2, "pillar_nature")
