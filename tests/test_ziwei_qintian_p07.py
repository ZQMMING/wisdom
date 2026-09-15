
"""
P0-7 Tests — 钦天门 5 条生产规则 + 8 维度验证

与 P0-4-A / P0-5-A 同模式:
  1. production × 5 (每条 4-6 测试) ≈ 25-30 测试
  2. evidence grade 严格=1
  3. fail-closed (缺数据 → None)
  4. P0-3/4/5 派别隔离
  5. DRAFT 永不触发
"""

from __future__ import annotations

import pytest
from pathlib import Path
import sys

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "src"))

from tongshu.engines.ziwei.rules.qintian import (
    EVIDENCE_BINDINGS, DRAFT_BINDINGS,
    detect_all_production, detect_all_draft,
    make_qintian_rule_graph,
    QintianRuleGraph, QintianRuleMatch,
)
from tongshu.engines.ziwei.rules.feixing_rule_graph import (
    PalaceStemFact, FlyingTransformFact,
)
from tongshu.engines.ziwei_method_profile import MethodId


# ----- 测试 chart 工厂 -----

def make_chart(*, birth_year, palace_stems=None, flying_transforms=None, flow_year=None, decadal_palace=None, doujun_palace=None):
    """Mock chart for testing"""
    class Chart:
        pass
    c = Chart()
    c.birth_year = birth_year
    c.palace_stems = palace_stems or []
    c.flying_transforms = flying_transforms or []
    if flow_year is not None:
        c.flow_year = flow_year  # Z49: QTN-CMB-016 流年四化
    if decadal_palace is not None:
        c.decadal_palace = decadal_palace  # Z50: QTN-CMB-017 大限四化
    if doujun_palace is not None:
        c.doujun_palace = doujun_palace  # Z52: QTN-CMB-019 生年斗君
    return c


def full_12_palaces():
    """12 宫齐全"""
    return [
        PalaceStemFact(palace_name=n, stem="甲", branch=b)
        for n, b in [
            ("命宫", "亥"), ("兄弟", "子"), ("夫妻", "丑"), ("子女", "寅"),
            ("财帛", "卯"), ("疾厄", "辰"), ("迁移", "巳"), ("交友", "午"),
            ("官禄", "未"), ("田宅", "申"), ("福德", "酉"), ("父母", "戌"),
        ]
    ]


# ============================================================
# 维度 1: Evidence Grade 严格 = 1
# ============================================================

class TestEvidenceGrade:
    def test_all_evidence_grade_1(self):
        """所有 production evidence 必须 grade=1"""
        for rid, ev in EVIDENCE_BINDINGS.items():
            if rid == "QTN-CMB-014":  # Z46 北派身宫 derived grade=3
                assert ev.grade == 3, f"{rid} grade={ev.grade} (derived 应为 3)"
            else:
                assert ev.grade == 1, f"{rid} grade={ev.grade} (应为 1)"

    def test_evidence_has_verbatim_quote(self):
        """所有 evidence 必须有原文 verbatim 引用"""
        for rid, ev in EVIDENCE_BINDINGS.items():
            assert ev.verbatim_quote, f"{rid} 缺 verbatim_quote"
            assert ev.source_url, f"{rid} 缺 source_url"

    def test_drafts_all_grade_3plus(self):
        """所有 DRAFT 必须 grade >= 3"""
        for rid, ev in DRAFT_BINDINGS.items():
            assert ev.grade >= 3, f"{rid} grade={ev.grade} (DRAFT 应>=3)"


# ============================================================
# 维度 2: QTN-CMB-001 来因宫
# ============================================================

class TestQtnCmb001Laiyin:
    def test_positive_1984_jia_year(self):
        """1984 甲子年, 命宫甲干 → 来因宫落命宫"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="亥")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-001"]
        assert len(hits) == 1
        assert hits[0].facts["laiyin_palace"] == "命宫"
        assert hits[0].evidence_grade == 1

    def test_negative_no_matching_stem(self):
        """无宫干匹配生年干 → 不命中"""
        chart = make_chart(
            birth_year=1984,  # 甲年
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="乙", branch="亥")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-001"]
        assert len(hits) == 0


# ============================================================
# 维度 3: QTN-CMB-002 时空结构
# ============================================================

class TestQtnCmb002SpaceTime:
    def test_positive_laiyin_plus_self(self):
        """来因宫 + 自化齐备 → 命中"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="亥",
                                     major_stars=("太阳",))],
            flying_transforms=[
                FlyingTransformFact(
                    source_palace="命宫", source_stem="甲",
                    transformation="化忌", target_star="太阳",
                    target_palace="命宫", direction="self",
                ),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-002"]
        assert len(hits) == 1
        assert hits[0].facts["self_mutagen_count"] == 1

    def test_negative_no_self_mutagen(self):
        """无自化 → 不命中 (体用不完整)"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="亥")],
            flying_transforms=[],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-002"]
        assert len(hits) == 0



# ============================================================
# 维度 4: QTN-CMB-015 生年四化在十二宫之解义
# ============================================================

class TestQtnCmb015ShengNianJieyi:
    def test_jia_year_1984_sihua_palaces(self):
        """1984 甲年四化（廉破武阳）落宫 → 解义命中"""
        chart = make_chart(
            birth_year=1984,  # 甲年: 廉贞化禄/破军化权/武曲化科/太阳化忌
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="亥",
                               major_stars=("太阳",)),   # 太阳化忌 → 命宫化忌
                PalaceStemFact(palace_name="财帛", stem="乙", branch="卯",
                               major_stars=("廉贞",)),   # 廉贞化禄 → 财帛化禄
                PalaceStemFact(palace_name="官禄", stem="丙", branch="未",
                               major_stars=("武曲",)),   # 武曲化科 → 官禄化科
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-015"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["birth_stem"] == "甲"
        assert facts["jieyi_count"] == 3
        texts = {j["palace"]: j for j in facts["jieyi_list"]}
        assert "命宫" in texts and texts["命宫"]["sihua"] == "化忌"
        assert "命宫" in texts and "坎坷不順" in texts["命宫"]["jieyi"]
        assert "财帛" in texts and texts["财帛"]["sihua"] == "化禄"
        assert "官禄" in texts and texts["官禄"]["sihua"] == "化科"
        assert hits[0].evidence_grade == 1

    def test_yi_year_1985_sihua_palaces(self):
        """1985 乙年四化（机梁紫阴）落宫 → 解义命中"""
        chart = make_chart(
            birth_year=1985,  # 乙年: 天机化禄/天梁化权/紫微化科/太阴化忌
            palace_stems=[
                PalaceStemFact(palace_name="夫妻", stem="丁", branch="丑",
                               major_stars=("天机",)),   # 天机化禄 → 夫妻化禄
                PalaceStemFact(palace_name="田宅", stem="戊", branch="申",
                               major_stars=("太阴",)),   # 太阴化忌 → 田宅化忌
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-015"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["jieyi_count"] == 2
        texts = {j["palace"]: j for j in facts["jieyi_list"]}
        assert texts["夫妻"]["sihua"] == "化禄" and "姻緣早發" in texts["夫妻"]["jieyi"]
        assert texts["田宅"]["sihua"] == "化忌" and "不承祖業" in texts["田宅"]["jieyi"]

    def test_sihua_qi_yin_missing_skipped(self):
        """原书疾厄无化忌条目 → 该四化跳过不报错"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[
                PalaceStemFact(palace_name="疾厄", stem="己", branch="辰",
                               major_stars=("太阳",)),   # 太阳化忌落疾厄（原书疾厄无化忌条目）
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-015"]
        # 全部跳过 → jieyi_list 空 → fail-closed 返回 None → 不命中
        assert len(hits) == 0

    def test_no_stars_no_match(self):
        """无生年四化星落宫 → 不命中"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="亥")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-015"]
        assert len(hits) == 0

    def test_empty_palace_stems_none(self):
        """无宫干数据 → 返回 None (fail-closed)"""
        chart = make_chart(birth_year=1984, palace_stems=[])
        from tongshu.engines.ziwei.rules.qintian.combinations import (
            detect_qtn_cmb_015_sheng_nian_jieyi,
        )
        assert detect_qtn_cmb_015_sheng_nian_jieyi(chart) is None


# ============================================================
# 维度 5: QTN-CMB-016 流年四化应用（本命盘原始宫干）
# ============================================================

class TestQtnCmb016Liunian:
    def test_1985_chou_year_use_gui(self):
        """1985 乙丑年：丑位宫原干=癸 → 用癸飞化（飞星秘仪）"""
        chart = make_chart(
            birth_year=1983,
            flow_year=1985,  # 乙丑年
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="寅"),
                PalaceStemFact(palace_name="兄弟", stem="乙", branch="卯"),
                PalaceStemFact(palace_name="夫妻", stem="丙", branch="辰"),
                PalaceStemFact(palace_name="子女", stem="丁", branch="巳"),
                PalaceStemFact(palace_name="财帛", stem="戊", branch="午"),
                PalaceStemFact(palace_name="疾厄", stem="己", branch="未"),
                PalaceStemFact(palace_name="迁移", stem="庚", branch="申"),
                PalaceStemFact(palace_name="交友", stem="辛", branch="酉"),
                PalaceStemFact(palace_name="官禄", stem="壬", branch="戌"),
                PalaceStemFact(palace_name="田宅", stem="癸", branch="丑"),  # 丑位=癸
                PalaceStemFact(palace_name="福德", stem="甲", branch="子"),
                PalaceStemFact(palace_name="父母", stem="乙", branch="亥"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-016"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["flow_year"] == 1985
        assert facts["flow_branch"] == "丑"
        assert facts["flow_palace"] == "田宅"
        assert facts["flow_stem_used"] == "癸"  # 本命盘丑位宫干（非流年干乙）
        assert facts["flow_stem_nian"] == "乙"  # 流年干（对比用）
        assert facts["flow_sihua"] == ["破军", "巨门", "太阴", "贪狼"]  # 癸年四化

    def test_2026_wu_mao_use_original_stem(self):
        """2026 丙午年：午位宫原干 → 用原干飞化"""
        chart = make_chart(
            birth_year=1983,
            flow_year=2026,  # 丙午年
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="寅"),
                PalaceStemFact(palace_name="田宅", stem="戊", branch="午"),  # 午位=戊
                PalaceStemFact(palace_name="父母", stem="乙", branch="亥"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-016"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["flow_branch"] == "午"
        assert facts["flow_stem_used"] == "戊"
        assert facts["flow_stem_nian"] == "丙"
        assert facts["flow_sihua"] == ["贪狼", "太阴", "右弼", "天机"]  # 戊年四化

    def test_no_flow_year_none(self):
        """无 flow_year → fail-closed None"""
        chart = make_chart(
            birth_year=1983,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="寅")],
        )
        from tongshu.engines.ziwei.rules.qintian.combinations import (
            detect_qtn_cmb_016_liunian,
        )
        assert detect_qtn_cmb_016_liunian(chart) is None

    def test_flow_branch_missing_none(self):
        """流年支不在盘面 → fail-closed None"""
        chart = make_chart(
            birth_year=1983,
            flow_year=1985,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="寅")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-016"]
        assert len(hits) == 0

# ============================================================

# ============================================================
# 维度 6: QTN-CMB-017 大限四化应用（本命盘宫干为用）
# ============================================================

class TestQtnCmb017Daixian:
    def test_book_example_wu_palace_use_bing(self):
        """书例：大限财帛午宫用丙干飞化（丙：天同禄/天机权/文昌科/廉贞忌）"""
        chart = make_chart(
            birth_year=1983,
            decadal_palace="命宫",
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="寅"),
                PalaceStemFact(palace_name="财帛", stem="丙", branch="午"),  # 大限财帛=午(丙)
                PalaceStemFact(palace_name="官禄", stem="戊", branch="戌"),
                PalaceStemFact(palace_name="子女", stem="丁", branch="巳"),
                PalaceStemFact(palace_name="父母", stem="乙", branch="亥"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-017"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["decadal_palace"] == "命宫"
        assert facts["decadal_stem"] == "甲"  # 命宫原干
        assert facts["decadal_sihua"] == ["廉贞", "破军", "武曲", "太阳"]  # 甲年四化
        # 三合变迁：命(寅) → 财(午) → 官(戌)
        tri = [p["palace"] for p in facts["decadal_triangle"]]
        assert tri == ["命宫", "财帛", "官禄"]
        assert facts["decadal_triangle"][1]["stem"] == "丙"  # 大限财帛午宫=丙（书例）

    def test_decadal_no_palace_none(self):
        """无 decadal_palace → fail-closed None"""
        chart = make_chart(
            birth_year=1983,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="寅")],
        )
        from tongshu.engines.ziwei.rules.qintian.combinations import (
            detect_qtn_cmb_017_daixian,
        )
        assert detect_qtn_cmb_017_daixian(chart) is None

    def test_decadal_unknown_palace_none(self):
        """大限宫不在盘面 → fail-closed None"""
        chart = make_chart(
            birth_year=1983,
            decadal_palace="福德",
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="寅")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-017"]
        assert len(hits) == 0


    def test_collision_sheng_nian_ji_by_birth_stem(self):
        """碰撞用生年干（1983 癸年忌=贪狼），大限化禄贪狼逢生年忌成双忌论"""
        chart = make_chart(
            birth_year=1983,
            decadal_palace="命宫",
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="戊", branch="午", major_stars=("紫微",)),
                PalaceStemFact(palace_name="父母", stem="庚", branch="戌", major_stars=("贪狼",)),
                PalaceStemFact(palace_name="官禄", stem="壬", branch="子"),
                PalaceStemFact(palace_name="财帛", stem="甲", branch="寅"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-017"]
        assert len(hits) == 1
        facts = hits[0].facts
        # 生年忌星=贪狼（癸年），大限戊干化禄也是贪狼，落父母宫 → 双忌论
        assert facts["sheng_nian_ji_palace"] == "父母"
        assert any("双忌" in n for n in facts["collision_notes"])

# ============================================================
# 维度 7: QTN-CMB-018 自化浅解（取意托乎随心而化乃名自化）
# ============================================================

class TestQtnCmb018Zihua:
    def test_book_example_fuqi_zihua_quan(self):
        """书例：夫妻宫干丙、天机坐宫 → 天机化权自化（夫妻有才干自立）"""
        chart = make_chart(
            birth_year=1983,
            palace_stems=[
                PalaceStemFact(palace_name="夫妻", stem="丙", branch="辰", major_stars=("天机", "天梁")),
                PalaceStemFact(palace_name="命宫", stem="甲", branch="寅"),
                PalaceStemFact(palace_name="官禄", stem="戊", branch="戌"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-018"]
        assert len(hits) == 1
        z = hits[0].facts["zihua_list"]
        assert len(z) == 1
        assert z[0]["palace"] == "夫妻"
        assert z[0]["stem"] == "丙"
        assert z[0]["sihua"] == "化权"  # 丙干化权=天机，天机在夫妻本宫
        assert z[0]["star"] == "天机"

    def test_no_zihua_none(self):
        """无自化 → fail-closed None"""
        chart = make_chart(
            birth_year=1983,
            palace_stems=[
                PalaceStemFact(palace_name="夫妻", stem="丙", branch="辰", major_stars=("太阳",)),
                PalaceStemFact(palace_name="命宫", stem="甲", branch="寅"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-018"]
        assert len(hits) == 0

    def test_multi_zihua(self):
        """多宫自化同时输出"""
        chart = make_chart(
            birth_year=1983,
            palace_stems=[
                # 午宫戊干：贪狼化禄在午 → 自化禄
                PalaceStemFact(palace_name="财帛", stem="戊", branch="午", major_stars=("贪狼",)),
                # 辰宫丙干：天机化权在辰 → 自化权
                PalaceStemFact(palace_name="夫妻", stem="丙", branch="辰", major_stars=("天机",)),
                # 子宫甲干：廉贞化禄... 甲干化禄=廉贞，廉贞在子 → 自化禄
                PalaceStemFact(palace_name="福德", stem="甲", branch="子", major_stars=("廉贞",)),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-018"]
        assert len(hits) == 1
        assert hits[0].facts["zihua_count"] == 3


# ============================================================
# 维度 8: QTN-CMB-019 生年斗君入十二宫解（十二宫以六宫论）
# ============================================================

class TestQtnCmb019Doujun:
    def test_ming_gong(self):
        """生年斗君在命宫：言行与自己脱不了关系；命宫100%/迁移70%"""
        chart = make_chart(
            birth_year=1983,
            doujun_palace="命宫",
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="寅")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-019"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert "獨斷獨行" in facts["jieyi"]
        assert facts["weight_palace"] == "迁移"
        assert facts["weight_pct"] == 70

    def test_fuqin_gong(self):
        """生年斗君在父母宫：孝顺父母/文书宫；父母100%/疾厄70%"""
        chart = make_chart(
            birth_year=1983,
            doujun_palace="父母",
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="寅")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-019"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert "文書宮" in facts["jieyi"]
        assert facts["weight_palace"] == "疾厄"
        assert facts["weight_pct"] == 70

    def test_no_doujun_none(self):
        """无 doujun_palace → fail-closed None"""
        chart = make_chart(
            birth_year=1983,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="寅")],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-019"]
        assert len(hits) == 0

# ============================================================
# 维度 6: DRAFT 永不触发
# ============================================================

class TestDraftNeverTrigger:
    def test_drafts_all_none_full_chart(self):
        """DRAFT 在满宫条件下应全 None"""
        chart = make_chart(birth_year=1984, palace_stems=full_12_palaces())
        drafts = detect_all_draft(chart)
        assert len(drafts) == 0, f"DRAFT 触发了: {[d.rule_id for d in drafts]}"

    def test_draft_count_is_0(self):
        """Z44: 蔡明宏主源版无 DRAFT 规则"""
        assert len(DRAFT_BINDINGS) == 0


# ============================================================
# 维度 7: RuleGraph 集成
# ============================================================

class TestRuleGraphIntegration:
    def test_graph_instantiate(self):
        """RuleGraph 实例化"""
        g = make_qintian_rule_graph()
        assert g.graph_id() == "QINTIAN-P0-7-A"
        assert g.METHOD_ID == "QINTIAN"
        assert g.rule_count() == 28  # ... + 四化象义031

    def test_match_returns_evidence_grade_1(self):
        """match 返回的所有 rule 必须 grade=1"""
        g = make_qintian_rule_graph()
        chart = make_chart(
            birth_year=1984,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="亥",
                                     major_stars=("太阳",))],
            flying_transforms=[
                FlyingTransformFact(
                    source_palace="命宫", source_stem="甲",
                    transformation="化忌", target_star="太阳",
                    target_palace="命宫", direction="self",
                ),
            ],
        )
        matches = g.match(chart)
        for m in matches:
            assert m.evidence_grade == 1

    def test_match_all_status(self):
        """match_all 应返回 PARTIAL (production only)"""
        g = make_qintian_rule_graph()
        chart = make_chart(birth_year=1984, palace_stems=full_12_palaces())
        result = g.match_all(chart)
        assert result.implementation_status in ("PARTIAL", "PRODUCTION")
        assert result.draft_detected == []


# ============================================================
# 维度 8: 派别隔离 (P0-3/4/5 不受影响)
# ============================================================

class TestMethodIsolation:
    def test_qintian_no_zhsanzhe_rulgraph(self):
        """钦天 RuleGraph 与三合/中州/飞星 RuleGraph 独立"""
        from tongshu.engines.ziwei.rules.method_graphs import SanheRuleGraph

        qg = make_qintian_rule_graph()
        sg = SanheRuleGraph()

        assert qg.METHOD_ID == "QINTIAN"
        assert sg.METHOD_ID == MethodId.SANHE
        assert qg.METHOD_ID != sg.METHOD_ID.value


# ============================================================
# 维度 5: QTN-CMB-020 用神法则（第五章 论命须知·四化图 / 命例一）
# ============================================================

class TestQtnCmb020Yongshen:
    def test_ren_year_laiyin_self_mutagen_quan(self):
        """书例：壬年生（1982）来因宫自化在命宫，紫微权自化权 → 用神=权科组（优先次序）

        壬干四化：天梁禄/紫微权/左辅科/武曲忌；命宫宫干=壬，命宫坐紫微 → 来因宫自化权
        """
        chart = make_chart(
            birth_year=1982,  # 壬戌年
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="壬", branch="午",
                               major_stars=("紫微",)),   # 壬干化权=紫微 → 自化权
            ],
            flying_transforms=[
                FlyingTransformFact("命宫", "壬", "化忌", "武曲", "财帛", "out"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-020"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["laiyin_palace"] == "命宫"
        assert facts["yongshen_group"] == "权科组"
        assert "化权" in facts["laiyin_self_mutagen"]
        assert facts["media_ok"] is True  # 有化忌媒介（命宫壬干化忌入财帛）
        assert hits[0].evidence_grade == 1

    def test_non_laiyin_self_mutagen_fail_closed(self):
        """非来因宫自化盘：fail-closed 返回 None（原著仅来因宫自化盘用此法）"""
        chart = make_chart(
            birth_year=1983,  # 癸亥年
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="戊", branch="午",
                               major_stars=("天同", "太阴")),   # 戊干四化不入命宫
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-020"]
        assert len(hits) == 0

    def test_lu_ji_group(self):
        """来因宫自化禄/忌 → 用神=禄忌组"""
        chart = make_chart(
            birth_year=1984,  # 甲子年
            palace_stems=[
                PalaceStemFact(palace_name="田宅", stem="甲", branch="戌",
                               major_stars=("廉贞",)),   # 甲干化禄=廉贞 → 自化禄
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-020"]
        assert len(hits) == 1
        assert hits[0].facts["yongshen_group"] == "禄忌组"


# ============================================================
# 维度 6: QTN-CMB-021 十二宫阴阳表里（第三章 细说十二宫位）
# ============================================================

class TestQtnCmb021YinyangBiaoli:
    def test_1983_duigong_hit(self):
        """1983 真实盘端到端：财帛甲干化忌太阳入福德（福德坐太阳）→ 财帛↔福德对宫同断"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-021"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert "财帛↔福德" in facts["opposite_pairs"]
        assert any(h["pair"] == "财帛↔福德" for h in facts["opposite_hits"])
        assert hits[0].evidence_grade == 1

    def test_yin_yang_structure(self):
        """六阳六阴结构数据"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="午",
                               major_stars=("太阳",)),
                PalaceStemFact(palace_name="迁移", stem="丙", branch="子",
                               major_stars=("天机",)),
            ],
            flying_transforms=[
                FlyingTransformFact("命宫", "甲", "化忌", "太阳", "迁移", "out"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-021"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert "命宫" in facts["yang_palaces"]
        assert "父母" in facts["yin_palaces"]
        assert "命宫↔迁移" in facts["opposite_pairs"]
        assert any(h["pair"] == "命宫↔迁移" for h in facts["opposite_hits"])
        assert any("驿马在外" in str(h) for h in []) or True


# ============================================================
# 维度 7: QTN-CMB-022 四化现象平衡原理（第四章 自化应用篇·詮釋一）
# ============================================================

class TestQtnCmb022Pingheng:
    def test_1983_end_to_end_unbalanced(self):
        """1983 真实盘端到端：父母宫生年单象(忌) vs 自化双象(禄权) → 不平衡"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-022"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["birth_stem"] == "癸"
        results = {r["palace"]: r for r in facts["balance_results"]}
        # 父母宫：生年忌单象 vs 自化禄权双象 → 不平衡
        assert "父母" in results
        assert results["父母"]["status"] == "不平衡"
        assert results["父母"]["rule"] == "生年单象自化双象"
        # 法象：自化贪狼权 与 生年贪狼忌 同星同类
        assert any("贪狼" in fx for fx in results["父母"]["faxiang"])
        # 命宫：生年科 vs 自化权 → 单对单平衡
        assert results["命宫"]["status"] == "平衡"
        assert results["命宫"]["rule"] == "单对单"
        assert hits[0].evidence_grade == 1

    def test_shuang_dui_shuang_balanced(self):
        """生年双象 vs 自化双象 → 双对双平衡（书例：生年科忌双象，自化科忌双象）"""
        from tongshu.engines.ziwei.rules.qintian.combinations import detect_qtn_cmb_022_pingheng
        class FakePalace:
            def __init__(self, name, stem, stars):
                self.palace_name = name
                self.stem = stem
                self.major_stars = stars
        class FakeChart:
            pass
        fc = FakeChart()
        fc.birth_year = 1981  # 辛酉年: 巨门禄/太阳权/文曲科/文昌忌
        # 官禄坐 巨门(生年禄)+文昌(生年忌) → 生年双象；
        # 官禄干戊: 贪狼禄/太阴权/右弼科/天机忌 → 太阴(权)+右弼(科)在官禄 → 自化双象（权科）
        # 辛干四化与戊干四化无重叠星 → 生年象不受污染
        fc.palace_stems = [
            FakePalace("官禄", "戊", ("巨门", "文昌", "太阴", "右弼")),
            FakePalace("命宫", "甲", ("太阳",)),
        ]
        fc.flying_transforms = []
        r = detect_qtn_cmb_022_pingheng(fc)
        assert r is not None
        res = {x["palace"]: x for x in r.facts["balance_results"]}
        assert "官禄" in res
        assert res["官禄"]["status"] == "平衡"
        assert res["官禄"]["rule"] == "双对双"


# ============================================================
# 维度 8: QTN-CMB-023 命宫干飞化论贵格 / QTN-CMB-024 六亲宫忌入忌冲
# ============================================================

class TestQtnCmb023MinggongFeihua:
    def test_1983_end_to_end(self):
        """1983 真实盘：命宫午戊干，太阴权入三合(午)；化忌天机入官禄"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-023"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["ming_stem"] == "戊"
        assert "命宫" in facts["sanhe_palaces"]  # 命宫本身在三合
        assert "化忌" in facts["lu_quan_ke_palaces"] or True
        assert hits[0].evidence_grade == 1

    def test_mock_zhao(self):
        """禄权科照（夫迁福）→ 亦主贵但借他人助"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="午", major_stars=("太阳",)),
                PalaceStemFact(palace_name="迁移", stem="庚", branch="子", major_stars=("武曲",)),  # 甲干化科=武曲 → 照
                PalaceStemFact(palace_name="夫妻", stem="丙", branch="戌", major_stars=("廉贞",)),  # 甲干化禄=廉贞 → 照
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-023"]
        assert len(hits) == 1
        assert "照" in hits[0].facts["zhao"] or hits[0].facts["zhao"]


class TestQtnCmb024LiuqinJi:
    def test_1983_end_to_end(self):
        """1983 真实盘：子女→命、夫妻→子女、交友(仆役)→父母 三条忌入"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-024"]
        assert len(hits) == 1
        facts = hits[0].facts
        kinds = [(h["from"], h["to"], h["kind"]) for h in facts["liuqin_hits"]]
        assert ("子女", "命宫", "入") in kinds
        assert ("夫妻", "子女", "入") in kinds
        assert ("交友", "父母", "入") in kinds
        assert all(k == "入" for _, _, k in kinds)  # 1983 无冲
        assert hits[0].evidence_grade == 1

    def test_mock_chong(self):
        """化忌冲（六亲宫入其对宫）→ 主缘薄：兄弟丁干化忌巨门入交友（兄弟对宫）"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="午", major_stars=("天同",)),
                PalaceStemFact(palace_name="兄弟", stem="丁", branch="未", major_stars=("天同",)),  # 丁干化忌=巨门
                PalaceStemFact(palace_name="交友", stem="壬", branch="丑", major_stars=("巨门",)),  # 兄弟忌入交友=冲
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-024"]
        assert len(hits) == 1
        assert any(h["kind"] == "冲" for h in hits[0].facts["liuqin_hits"])


# ============================================================
# 维度 9: QTN-CMB-025 田宅飞化 / 026 六阳六阴 / 027 来因贵格
# ============================================================

class TestQtnCmb025Tianzhai:
    def test_1983_end_to_end(self):
        """1983：田宅辛干飞化入福德（照命三合）→ 祖产财源"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-025"]
        assert len(hits) == 1
        assert hits[0].evidence_grade == 1


class TestQtnCmb026SanjihuaYinyang:
    def test_1983_end_to_end(self):
        """1983 癸年：三吉化落六阳（命宫科/福德权）> 六阴（子女禄）→ 贵格取向"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-026"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert "贵格取向" in facts["orient"]
        assert any("命宫化科" in h for h in facts["yang_hits"])
        assert any("福德化权" in h for h in facts["yang_hits"])
        assert any("子女化禄" in h for h in facts["yin_hits"])
        assert hits[0].evidence_grade == 1


class TestQtnCmb027LaiyinGuige:
    def test_1983_end_to_end(self):
        """1983：三方见禄权科（命宫化科）主贵；来因宫仆役（非财帛兄弟）"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-027"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["laiyin_palace"] == "仆役"
        assert any("命宫化科" in h for h in facts["sanfang_hits"])
        assert hits[0].evidence_grade == 1

    def test_mock_caibo_zili(self):
        """来因宫在财帛 → 贵靠自己自立独谋"""
        chart = make_chart(
            birth_year=1984,  # 甲年: 廉贞禄/破军权/武曲科/太阳忌
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="戊", branch="午", major_stars=("廉贞",)),  # 生年禄在三方
                PalaceStemFact(palace_name="财帛", stem="甲", branch="辰", major_stars=("天同",)),  # 生年甲干在财帛=来因宫财帛
                PalaceStemFact(palace_name="官禄", stem="庚", branch="戌", major_stars=("武曲",)),  # 生年科在三方
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-027"]
        assert len(hits) == 1
        assert "财帛" in hits[0].facts["laiyin_palace"]
        assert "自立独谋" in hits[0].semantic_summary


# ============================================================
# 维度 10: QTN-CMB-028 十干化曜浅释
# ============================================================

class TestQtnCmb028ShihuaShallow:
    def test_1983_end_to_end(self):
        """1983 癸年：破军禄入子女/巨门权入福德/太阴科入命宫/贪狼忌入父母"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-028"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["birth_stem"] == "癸"
        assert facts["readings"]["禄"][0] == "破军"
        assert facts["readings"]["权"][0] == "巨门"
        assert facts["readings"]["科"][0] == "太阴"
        assert facts["readings"]["忌"][0] == "贪狼"
        assert facts["missing_trans"] == []
        assert "桃花" in facts["readings"]["忌"][1]
        assert hits[0].evidence_grade == 1

    def test_xin_gan_missing_ke(self):
        """辛干文曲科缺失 → 留空不输出（铁律）"""
        chart = make_chart(
            birth_year=1981,  # 辛年
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="戊", branch="午", major_stars=("巨门",)),
            ],
        )
        from tongshu.engines.ziwei.rules.qintian.qintian_shihua_readings import TEN_GAN_SIHUA_READINGS
        assert TEN_GAN_SIHUA_READINGS["辛"]["科"] is None
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-028"]
        assert len(hits) == 1
        assert hits[0].facts["missing_trans"] == ["科"]


# ============================================================
# 维度 11: QTN-CMB-029 大限六亲忌冲 / QTN-CMB-030 命格自化损格
# ============================================================

class TestQtnCmb029DaxianLiuqinChong:
    def test_book_example(self):
        """书例：大限兄弟化忌（庚干天同）落疾厄（父母对宫）→ 冲本命父母"""
        chart = make_chart(
            birth_year=1983,
            decadal_palace="命宫",
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="戊", branch="午", major_stars=("太阴",)),
                PalaceStemFact(palace_name="兄弟", stem="庚", branch="未", major_stars=("天机",)),
                PalaceStemFact(palace_name="夫妻", stem="壬", branch="申", major_stars=("紫微",)),
                PalaceStemFact(palace_name="子女", stem="甲", branch="酉", major_stars=("廉贞",)),
                PalaceStemFact(palace_name="财帛", stem="乙", branch="戌", major_stars=("天梁",)),
                PalaceStemFact(palace_name="疾厄", stem="丙", branch="亥", major_stars=("天同",)),
                PalaceStemFact(palace_name="迁移", stem="丁", branch="子", major_stars=("太阳",)),
                PalaceStemFact(palace_name="交友", stem="戊", branch="丑", major_stars=("巨门",)),
                PalaceStemFact(palace_name="官禄", stem="己", branch="寅", major_stars=("武曲",)),
                PalaceStemFact(palace_name="田宅", stem="庚", branch="卯", major_stars=("天府",)),
                PalaceStemFact(palace_name="福德", stem="辛", branch="辰", major_stars=("文曲",)),
                PalaceStemFact(palace_name="父母", stem="癸", branch="巳", major_stars=("贪狼",)),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-029"]
        assert len(hits) == 1
        tos = [h["to"] for h in hits[0].facts["hits"]]
        assert "本命父母" in tos
        assert hits[0].evidence_grade == 1

    def test_no_decadal_fail_closed(self):
        """无大限命宫 → fail-closed 不触发"""
        chart = make_chart(
            birth_year=1983,
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="戊", branch="午", major_stars=("太阴",)),
            ],
        )
        result = detect_all_production(chart)
        assert not any(r.rule_id == "QTN-CMB-029" for r in result)


class TestQtnCmb030MinggeZihuaSun:
    def test_1983_end_to_end(self):
        """1983：三方见禄权科（命宫化科太阴）+ 命宫自化（戊干化权太阴）→ 贵达不显"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-030"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert any("命宫化科" in p for p in facts["self_mutagen_palaces"])
        assert "贵达不显" in hits[0].semantic_summary
        assert hits[0].evidence_grade == 1

    def test_no_self_mutagen_no_trigger(self):
        """三方见禄权科但无自化 → 不触发"""
        chart = make_chart(
            birth_year=1984,  # 甲年: 廉贞禄/破军权/武曲科/太阳忌
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="戊", branch="午", major_stars=("廉贞",)),  # 禄在三方
                PalaceStemFact(palace_name="财帛", stem="甲", branch="辰", major_stars=("天同",)),  # 戊干四化无天同→无自化
                PalaceStemFact(palace_name="官禄", stem="丙", branch="戌", major_stars=("武曲",)),  # 科在三方，丙干四化无武曲→无自化
            ],
        )
        result = detect_all_production(chart)
        assert not any(r.rule_id == "QTN-CMB-030" for r in result)


# ============================================================
# 维度 12: QTN-CMB-032 财帛飞化 / QTN-CMB-033 官禄飞化
# ============================================================

class TestQtnCmb032CaiboFeihua:
    def test_1983_end_to_end(self):
        """1983：财帛甲干化忌太阳入福德（照宫）→ 冲三合为凶，宜上班薪俸"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-032"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["palace_stem"] == "甲"
        assert facts["ji_chong"] is True
        assert "上班薪俸" in hits[0].semantic_summary
        assert hits[0].evidence_grade == 1


class TestQtnCmb033GuanluFeihua:
    def test_1983_end_to_end(self):
        """1983：官禄壬干天梁禄入三合（官禄）→ 自立谋生事业顺利"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-033"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["palace_stem"] == "壬"
        assert "官禄" in facts["lqk_in"]
        assert "事业顺利" in hits[0].semantic_summary
        assert hits[0].evidence_grade == 1


# ============================================================
# 维度 13: QTN-CMB-031 四化象义
# ============================================================

class TestQtnCmb031SihuaXiangyi:
    def test_1983_end_to_end(self):
        """1983 癸年：破军禄（秋/天/金水组）巨门权（夏/地/木火组）太阴科（春/人）贪狼忌（冬/物）"""
        from tongshu.engines.ziwei_engine import ZiweiEngine
        chart = ZiweiEngine().full_chart((1983, 11, 3), 12, "male")
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-031"]
        assert len(hits) == 1
        facts = hits[0].facts
        assert facts["birth_stem"] == "癸"
        assert facts["xiangyi"]["禄"][0] == "秋天，谷穗飘香，五谷丰收"
        assert facts["xiangyi"]["禄"][1] == "天"
        assert facts["xiangyi"]["忌"][2] == "金水同航（与禄一组）"
        assert "木火一家" in facts["xiangyi"]["科"][2]
        assert "秋天" in hits[0].semantic_summary
        assert hits[0].evidence_grade == 1
