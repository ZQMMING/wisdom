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


def chart(pillars, relations=None, hidden_stems=None):
    c = dict(BASE)
    c["pillars"] = pillars
    c["relations"] = relations or {}
    if hidden_stems is not None:
        c["hidden_stems"] = hidden_stems
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


def test_dts_012_tian_quan_yiqi():
    """天全一氣 注入（《滴天髓·干支总论》DTS-010-004）。

    注：CAND-DTS-012 为 require 规则（RuleEngine 只消费 emit），facts 不产出；
    require 语义（莫之載為逆 警示）供上层 judgment 消费，V2.22 未定义消费机制，
    已记录待审批裁决。此处验证派生字段注入正确。
    """
    # 四天干全木（甲/乙 同木）：甲子 乙丑 甲寅 乙卯
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "乙", "branch": "丑"},
        "day": {"stem": "甲", "branch": "寅"},
        "hour": {"stem": "乙", "branch": "卯"},
    }))
    assert res.metadata["view"]["tian_status"] == "全一氣"
    assert "莫之載為逆" not in vals(res, "di_de")


def test_dts_013_di_quan_sanwu():
    """地全三物 注入（《滴天髓·干支总论》DTS-010-006/007 注：寅卯辰、亥卯未）。

    注：CAND-DTS-013 为 require 规则，facts 不产出；同上记录待审批。
    """
    # 地支含 寅卯辰（三会东方木）
    res = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "丙", "branch": "卯"},
        "day": {"stem": "甲", "branch": "辰"},
        "hour": {"stem": "庚", "branch": "午"},
    }))
    assert res.metadata["view"]["di_status"] == "全三物"
    assert "莫之容為逆" not in vals(res, "tian_dao")


def test_dts_014_015_stem_position():
    """陽乘陽位→陽者昌；陰乘陰位→陰氣盛（《滴天髓·干支总论》DTS-010-008/010）"""
    # 甲（阳）坐 午（阳）
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "午"},
        "hour": {"stem": "庚", "branch": "寅"},
    }))
    assert "陽者昌" in vals(res, "state")
    # 癸（阴）坐 丑（阴）
    res2 = build(chart({
        "year": {"stem": "壬", "branch": "申"},
        "month": {"stem": "癸", "branch": "亥"},
        "day": {"stem": "癸", "branch": "丑"},
        "hour": {"stem": "乙", "branch": "未"},
    }))
    assert "陰氣盛" in vals(res2, "state")


def test_dts_023_024_xing_state():
    """形全→損其有餘；形缺→補其不足（《滴天髓·形象论》DTS-011-008）。"""
    # 形全盘：四柱干支覆盖全五行（甲寅木 丙午火 庚申金 戊子水土）
    res = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "庚", "branch": "申"},
        "hour": {"stem": "戊", "branch": "子"},
    }))
    assert "損其有餘" in vals(res, "yi")
    # 形缺盘：缺土（甲寅木 丙午火 庚申金 壬子水）
    res2 = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "庚", "branch": "申"},
        "hour": {"stem": "壬", "branch": "子"},
    }))
    assert "補其不足" in vals(res2, "yi")


def test_dts_020_liangqi_chengxiang():
    """兩氣合而成象 → 象不可破（《滴天髓·形象论》DTS-011-001/002）。

    注：天干属一行（木）、地支属一行（火），木火相生，其象属一。
    """
    # 干全木（甲乙甲乙）+ 支全火（午巳午巳）→ 木生火 → 兩氣合而成象
    res = build(chart({
        "year": {"stem": "甲", "branch": "午"},
        "month": {"stem": "乙", "branch": "巳"},
        "day": {"stem": "甲", "branch": "午"},
        "hour": {"stem": "乙", "branch": "巳"},
    }))
    assert "象不可破" in vals(res, "xiang_state")
    # 反例：干木 + 支火 + 透金干（庚）→ 非全一行 → 不成象
    res2 = build(chart({
        "year": {"stem": "甲", "branch": "午"},
        "month": {"stem": "乙", "branch": "巳"},
        "day": {"stem": "甲", "branch": "午"},
        "hour": {"stem": "庚", "branch": "巳"},
    }))
    assert "象不可破" not in vals(res2, "xiang_state")


def test_dts_051_052_zhan():
    """天戰猶自可；地戰急如火（《滴天髓·战局》DTS-046-001/002 注）。"""
    # 天戰：干头甲乙（木）+ 庚辛（金）
    res = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "庚", "branch": "午"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "辛", "branch": "寅"},
    }))
    assert "猶自可" in vals(res, "xiong")
    # 地戰：地支寅申并存（干头无甲乙庚辛混战）
    res2 = build(chart({
        "year": {"stem": "丙", "branch": "寅"},
        "month": {"stem": "戊", "branch": "午"},
        "day": {"stem": "壬", "branch": "申"},
        "hour": {"stem": "庚", "branch": "子"},
    }))
    assert "急如火" in vals(res2, "xiong")


def test_dts_053_056_xiang():
    """君亢/臣過/母旺子孤/子衆母衰（《滴天髓》君象/臣象/母象/子象篇注）。"""
    # 君亢：甲乙日主满盘木（6），土（财）一二 → 損上以益下
    res = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "乙", "branch": "卯"},
        "day": {"stem": "甲", "branch": "辰"},
        "hour": {"stem": "乙", "branch": "未"},
    }))
    assert "損上以益下" in vals(res, "yi")
    # 臣過：甲乙日主满盘木（5），金（官）一二、无财土 → 損下以益上
    res2 = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "乙", "branch": "卯"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "辛", "branch": "巳"},
    }))
    assert "損下以益上" in vals(res2, "yi")
    # 母旺子孤：甲乙日主满盘木（6），火（食伤）一二、无财土 → 多方生子孫
    res3 = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "乙", "branch": "卯"},
        "day": {"stem": "甲", "branch": "午"},
        "hour": {"stem": "乙", "branch": "巳"},
    }))
    assert "多方生子孫" in vals(res3, "yi")
    # 子衆母衰：甲乙日主满盘木（5），水（印）多（3）→ 多方安母
    res4 = build(chart({
        "year": {"stem": "甲", "branch": "子"},
        "month": {"stem": "癸", "branch": "亥"},
        "day": {"stem": "甲", "branch": "寅"},
        "hour": {"stem": "乙", "branch": "卯"},
    }))
    assert "多方安母" in vals(res4, "yi")


def test_dts_021_022_duxang_quanxiang():
    """獨象喜行化地；全象喜行財地（《滴天髓·形象論》DTS-011-004/006 注）。
    [PENDING_VERIFY] 量化阈值（獨象≥6/全象恰三行且主≥3）为暂定口径，待多源验证。"""
    # 獨象：甲乙日主 8 字木 6（曲直炎上之類）
    res = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "乙", "branch": "卯"},
        "day": {"stem": "甲", "branch": "辰"},
        "hour": {"stem": "乙", "branch": "未"},
    }))
    assert "化地" in vals(res, "yun_favor")
    assert "要昌" in vals(res, "hua_shen")
    # 全象：主（木）3 + 食伤（火）2 + 财（土）3，恰三行
    res2 = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "辰"},
        "hour": {"stem": "己", "branch": "未"},
    }))
    assert "財地" in vals(res2, "yun_favor")


def test_dts_strength_min():
    """strength 最小可用版（Human 裁决 2026-09-16）：日主旺/衰/均衡 + 喜用方向。
    清浊（029/086/087）依赖 strength，本字段为清浊挂载最低门槛。
    [PENDING_VERIFY] 得令/得地（本气）/得势布尔组合近似；藏干权重与制化维度待迭代。"""
    # 身旺：甲日得令（月支寅木）∧得地（寅/卯藏干本气木）∧得势（年干甲比劫）→ WANG
    # 喜用＝财土/官杀金/食伤火
    res = build(chart({
        "year": {"stem": "甲", "branch": "寅"},
        "month": {"stem": "丙", "branch": "寅"},
        "day": {"stem": "甲", "branch": "寅"},
        "hour": {"stem": "丁", "branch": "卯"},
    }))
    assert res.metadata["view"]["day_strength_state"] == "WANG"
    assert res.metadata["view"]["yong_shen_ten_god"] == ["财", "官杀", "食伤"]
    assert "土" in res.metadata["view"]["yong_shen_el"]
    # 身弱：甲日失令（月支申金）∧无木根（藏干本气金）∧天干无帮扶 → SHUAI
    # 喜用＝比劫木/印水
    res2 = build(chart({
        "year": {"stem": "庚", "branch": "申"},
        "month": {"stem": "庚", "branch": "申"},
        "day": {"stem": "甲", "branch": "申"},
        "hour": {"stem": "庚", "branch": "申"},
    }))
    assert res2.metadata["view"]["day_strength_state"] == "SHUAI"
    assert res2.metadata["view"]["yong_shen_ten_god"] == ["印", "比劫"]
    assert "木" in res2.metadata["view"]["yong_shen_el"] and "水" in res2.metadata["view"]["yong_shen_el"]
    # 均衡：甲日失令（月支午火）但得地（日支寅藏干本气甲木）→ JUN_HENG（中和无定喜）
    res3 = build(chart({
        "year": {"stem": "丙", "branch": "午"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "寅"},
        "hour": {"stem": "丙", "branch": "午"},
    }, hidden_stems={"寅": ["甲", "丙", "戊"]}))
    assert res3.metadata["view"]["day_strength_state"] == "JUN_HENG"
    assert res3.metadata["view"]["yong_shen_el"] == []


def test_dts_047_050_cong_hua():
    """真从/假从/真化/假化（《滴天髓》從象/化象/假象/假化篇注）。
    [PENDING_VERIFY] 独象/全象阈值与假化缺龙口径为暂定，待多源验证。
    Human 裁决 2026-09-15：从格不量化——cai_guan_state/support_state 为状态枚举，
    规则 047/049 直接消费两枚举（结构事实→状态→从格规则）。"""
    # 真从：财官得令（申金）且透干（戊庚辛）→STRONG；干支+藏干无比劫印 →NONE
    res = build(chart({
        "year": {"stem": "戊", "branch": "戌"},
        "month": {"stem": "庚", "branch": "申"},
        "day": {"stem": "甲", "branch": "戌"},
        "hour": {"stem": "辛", "branch": "酉"},
    }))
    assert res.metadata["view"]["cai_guan_state"] == "STRONG"
    assert res.metadata["view"]["support_state"] == "NONE"
    assert "只論從神" in vals(res, "method")
    # 假从：财官 STRONG，时支寅木（比劫微根）→HAS_SUPPORT
    res2 = build(chart({
        "year": {"stem": "戊", "branch": "戌"},
        "month": {"stem": "庚", "branch": "申"},
        "day": {"stem": "甲", "branch": "戌"},
        "hour": {"stem": "辛", "branch": "寅"},
    }))
    assert res2.metadata["view"]["cai_guan_state"] == "STRONG"
    assert res2.metadata["view"]["support_state"] == "HAS_SUPPORT"
    assert "假從亦可發其身" in vals(res2, "method")
    # 不量化检查：派生 view 不得出现数字计数字段
    view = res.metadata["view"]
    assert not any(k in view for k in ("cai_guan_strength", "support_count", "zhu_wo"))
    # 真化：甲己合于时，单透己、不遇壬癸甲乙戊己、有辰、月支辰土（化神得令）
    res3 = build(chart({
        "year": {"stem": "丙", "branch": "辰"},
        "month": {"stem": "丙", "branch": "辰"},
        "day": {"stem": "甲", "branch": "子"},
        "hour": {"stem": "己", "branch": "巳"},
    }))
    assert "只論化神" in vals(res3, "method")
    # 假化：甲己合于时，单透己，但无辰（无龙）
    res4 = build(chart({
        "year": {"stem": "庚", "branch": "午"},
        "month": {"stem": "丙", "branch": "午"},
        "day": {"stem": "甲", "branch": "子"},
        "hour": {"stem": "己", "branch": "巳"},
    }))
    assert "假化亦多貴" in vals(res4, "method")
    # 乙庚真化（四合不检查「不遇」[DIRECT_TEXT]）：乙庚合于月、单透庚、有辰、月支申金（得令）
    # ——壬（印）在干亦不阻断（Human 裁决：乙庚等四合原文未列不遇集，不套用甲己例）
    res5 = build(chart({
        "year": {"stem": "壬", "branch": "辰"},
        "month": {"stem": "庚", "branch": "申"},
        "day": {"stem": "乙", "branch": "丑"},
        "hour": {"stem": "丁", "branch": "巳"},
    }))
    assert "只論化神" in vals(res5, "method")
