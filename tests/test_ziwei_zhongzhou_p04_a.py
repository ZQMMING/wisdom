"""
P0-4-A 中州派星系组合判法 — Pytest 套件

按 P0-4 裁决：
- 严格 10 条 production detect
- 每条规则：Positive case / Negative case / Boundary case
- 不修改 P0-3 任何 baseline（不动 ZiweiChart / FrozenZiweiChart 字段）
- 不混入 Sanhe / Feixing / Qintian（派别隔离）

工程纪律：
- 所有 chart 都用测试本地 ZiweiChart 构造，不依赖真实 iztro 输出
- evidence_grade 一律 = 1（王亭之原文）
- 失败一律 fail-closed（返回 None / 空集合）
"""
from __future__ import annotations

import pytest

from src.tongshu.engines.ziwei_engine import ZiweiChart
from src.tongshu.engines.ziwei_palace_resolution import ZiweiPalaceResolver
from src.tongshu.engines.ziwei_method_profile import MethodId
from src.tongshu.engines.ziwei.rules.zhongzhou import (
    EVIDENCE_TABLE,
    P0_4_A_PRODUCTION_DETECTORS,
    DRAFT_DETECTORS,
    ZhongzhouRuleGraph,
    build_feature_bundle,
    make_zhongzhou_rule_graph,
)
from src.tongshu.engines.ziwei.rules.zhongzhou.combinations import (
    detect_an_yao_sha_po_tan,
    detect_cai_yin_jia_yin_standard,
    detect_ji_yue_tong_liang_standard,
    detect_lu_cun_ya_tuo_jia,
    detect_lu_ma_jiao_chi,
    detect_ming_zhu_chu_hai_auspicious,
    detect_sha_xian_zhen_dui,
    detect_sha_po_lian_tan,
    detect_xing_ji_jia_yin_standard,
    detect_ziwei_gu_jun,
)


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────

def _empty_palaces() -> dict:
    """返回一份空 12 宫位骨架。"""
    names = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
             "迁移", "交友", "事业", "田宅", "福德", "父母"]
    branches = ["子", "丑", "寅", "卯", "辰", "巳",
                "午", "未", "申", "酉", "戌", "亥"]
    return {n: {"branch": b, "major": [], "minor": []}
            for n, b in zip(names, branches)}


def _make_chart(palaces: dict, birth_year: int = 2000,
                soul_main: list | None = None,
                soul_branch: str = "子") -> ZiweiChart:
    """构造测试用 ZiweiChart。"""
    return ZiweiChart(
        source="test",
        birth_year=birth_year,
        palaces=palaces,
        soul_palace_main_stars=soul_main or [],
        soul_earthly_branch=soul_branch,
    )


def _resolver(chart: ZiweiChart) -> ZiweiPalaceResolver:
    return ZiweiPalaceResolver(chart=chart, method_id=MethodId.ZHONGZHOU)


# ─────────────────────────────────────────────────────────────────────────
# [Group 1] stub / fail-closed
# ─────────────────────────────────────────────────────────────────────────

class TestStubChartFailClosed:
    """stub chart 不得触发任何规则。"""

    def test_stub_chart_zero_matches(self):
        stub = ZiweiChart(source="stub", birth_year=0)
        result = make_zhongzhou_rule_graph().match_all(stub, _resolver(stub))
        assert result.matched_rules == ()
        assert result.implementation_status == "PARTIAL"

    def test_stub_bundle_all_none_or_empty(self):
        stub = ZiweiChart(source="stub", birth_year=0)
        bundle = build_feature_bundle(stub, _resolver(stub))
        assert bundle.tianxiang_palace is None
        assert bundle.ziwei_palace is None
        assert bundle.ming_sanfang_stars == frozenset()
        assert bundle.lucun_palace is None
        assert bundle.tianma_palace is None
        assert bundle.qi_sha_palace is None
        assert bundle.wenqu_palace is None


# ─────────────────────────────────────────────────────────────────────────
# [Group 2] empty chart 不得触发
# ─────────────────────────────────────────────────────────────────────────

class TestEmptyChartNoFalsePositive:
    """空 12 宫位 (无任何星曜) 不得触发 production 规则。"""

    def test_all_10_production_detectors_return_none_on_empty(self):
        chart = _make_chart(_empty_palaces())
        bundle = build_feature_bundle(chart, _resolver(chart))
        hits = [d(bundle) for d in P0_4_A_PRODUCTION_DETECTORS]
        assert all(r is None for r in hits), \
            f"production 误触发: {[r.combo_id for r in hits if r]}"


# ─────────────────────────────────────────────────────────────────────────
# [Group 3] 10 条规则逐条：Positive / Negative / Boundary
# ─────────────────────────────────────────────────────────────────────────


class TestRule_001_JiYueTongLiang:
    """ZHZ-CMB-001 机月同梁格（标准）。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"],
                           "minor": ["天机", "天同", "天梁", "太阴", "文昌"]}
        chart = _make_chart(palaces)
        combo = detect_ji_yue_tong_liang_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-001"
        assert combo.evidence_grade == 1

    def test_negative_missing_one_star(self):
        palaces = _empty_palaces()
        # 缺太阴
        palaces["命宫"] = {"branch": "子", "major": ["紫微"],
                           "minor": ["天机", "天同", "天梁", "文昌"]}
        chart = _make_chart(palaces)
        combo = detect_ji_yue_tong_liang_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None

    def test_boundary_stars_in_sanfang_partial(self):
        """天机/天同/天梁在三方，但太阴不在三方 → 不命中（缺一颗）。"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"],
                           "minor": ["天同", "文昌"]}
        # 把天机放在迁移(午=三方)，天梁放在财帛(辰=三方)，太阴放在兄弟(丑=非三方)
        palaces["迁移"] = {"branch": "午", "major": ["天机"], "minor": []}
        palaces["财帛"] = {"branch": "辰", "major": ["天梁"], "minor": []}
        palaces["兄弟"] = {"branch": "丑", "major": ["太阴"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_ji_yue_tong_liang_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 太阴不在三方（兄弟不是三方）


class TestRule_003_ShaPoLianTan:
    """ZHZ-CMB-003 杀破廉贪格。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["七杀"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_sha_po_lian_tan(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-003"

    def test_negative_no_target_stars(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_sha_po_lian_tan(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None

    def test_boundary_po_jun_in_sanfang(self):
        """破军在迁移(午) = 命宫三方 → 命中。"""
        palaces = _empty_palaces()
        palaces["迁移"] = {"branch": "午", "major": ["破军"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_sha_po_lian_tan(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None  # 破军入命宫三方

    def test_boundary_po_jun_outside_sanfang(self):
        """破军在兄弟(丑) ≠ 命宫三方 → 不命中。"""
        palaces = _empty_palaces()
        palaces["兄弟"] = {"branch": "丑", "major": ["破军"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_sha_po_lian_tan(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 兄弟不是命宫三方


class TestRule_004_CaiYinJiaYin:
    """ZHZ-CMB-004 财荫夹印（标准）。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["兄弟"] = {"branch": "丑", "major": ["天相"], "minor": []}
        palaces["命宫"] = {"branch": "子", "major": ["巨门"], "minor": []}
        palaces["夫妻"] = {"branch": "寅", "major": ["天梁"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_cai_yin_jia_yin_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-004"

    def test_negative_no_tianxiang(self):
        palaces = _empty_palaces()
        chart = _make_chart(palaces)
        combo = detect_cai_yin_jia_yin_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None

    def test_boundary_wrong_neighbors(self):
        """巨门/天梁不在紧邻位置"""
        palaces = _empty_palaces()
        palaces["兄弟"] = {"branch": "丑", "major": ["天相"], "minor": []}
        palaces["财帛"] = {"branch": "辰", "major": ["巨门"], "minor": []}
        palaces["疾厄"] = {"branch": "巳", "major": ["天梁"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_cai_yin_jia_yin_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 巨门/天梁 跨位


class TestRule_006_XingJiJiaYin:
    """ZHZ-CMB-006 刑忌夹印（标准）。与财荫夹印同位置铁律。"""

    def test_positive_same_position_as_cai_yin(self):
        palaces = _empty_palaces()
        palaces["兄弟"] = {"branch": "丑", "major": ["天相"], "minor": []}
        palaces["命宫"] = {"branch": "子", "major": ["巨门"], "minor": []}
        palaces["夫妻"] = {"branch": "寅", "major": ["天梁"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_xing_ji_jia_yin_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-006"

    def test_negative_no_tianxiang(self):
        palaces = _empty_palaces()
        chart = _make_chart(palaces)
        combo = detect_xing_ji_jia_yin_standard(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None


class TestRule_008_ZiweiGuJun:
    """ZHZ-CMB-008 紫微孤君。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"], "minor": []}
        chart = _make_chart(palaces, soul_main=["紫微"])
        combo = detect_ziwei_gu_jun(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-008"

    def test_negative_with_fu_bi(self):
        """左辅/右弼在紫微的"三方" (命宫+迁移+财帛+事业) 则非孤君。"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"], "minor": []}
        # 左辅放在迁移(午)= 三方；这样不算孤君
        palaces["迁移"] = {"branch": "午", "major": [], "minor": ["左辅"]}
        chart = _make_chart(palaces, soul_main=["紫微"])
        combo = detect_ziwei_gu_jun(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 三方有左辅则非孤君

    def test_negative_fu_bi_outside_sanfang_still_gu_jun(self):
        """左辅在兄弟宫（不在三方）→ 仍然孤君（紫微三方不含兄弟）。"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"], "minor": []}
        palaces["兄弟"] = {"branch": "丑", "major": [], "minor": ["左辅"]}
        chart = _make_chart(palaces, soul_main=["紫微"])
        combo = detect_ziwei_gu_jun(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None  # 兄弟不在三方 → 仍孤君

    def test_boundary_ziwei_not_in_ming(self):
        palaces = _empty_palaces()
        palaces["兄弟"] = {"branch": "丑", "major": ["紫微"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_ziwei_gu_jun(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 紫微不在命宫


class TestRule_010_MingZhuChuHai:
    """ZHZ-CMB-010 明珠出海（吉）。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"],
                           "minor": ["太阴", "文昌"]}
        chart = _make_chart(palaces)
        combo = detect_ming_zhu_chu_hai_auspicious(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-010"

    def test_negative_no_chang_qu(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"], "minor": ["太阴"]}
        chart = _make_chart(palaces)
        combo = detect_ming_zhu_chu_hai_auspicious(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None

    def test_boundary_jie_kong_unsafe(self):
        """截空值日=丑/未/寅/申 - 命宫在这些地支时不安"""
        for branch in ["丑", "未", "寅", "申"]:
            palaces = _empty_palaces()
            palaces["命宫"] = {"branch": branch, "major": ["紫微"],
                               "minor": ["太阴", "文昌"]}
            chart = _make_chart(palaces)
            combo = detect_ming_zhu_chu_hai_auspicious(
                build_feature_bundle(chart, _resolver(chart)))
            assert combo is None, f"截空值日={branch} 应不触发"


class TestRule_012_AnYaoShaPoTan:
    """ZHZ-CMB-012 暗曜凶格（文曲 + 杀破贪同宫）。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["七杀"], "minor": ["文曲"]}
        chart = _make_chart(palaces)
        combo = detect_an_yao_sha_po_tan(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-012"

    def test_negative_no_wenqu(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["七杀"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_an_yao_sha_po_tan(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None


class TestRule_016_ShaXianZhenDui:
    """ZHZ-CMB-016 杀陷震兑。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["子女"] = {"branch": "卯", "major": ["七杀", "武曲"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_sha_xian_zhen_dui(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-016"

    def test_negative_qisha_in_zi(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["七杀", "武曲"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_sha_xian_zhen_dui(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 七杀在子不在震兑

    def test_boundary_no_wuqu(self):
        palaces = _empty_palaces()
        palaces["子女"] = {"branch": "卯", "major": ["七杀"], "minor": []}
        chart = _make_chart(palaces)
        combo = detect_sha_xian_zhen_dui(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 武曲未同度


class TestRule_017_LuCunYaTuoJia:
    """ZHZ-CMB-017 禄存必为羊陀夹。"""

    def test_positive(self):
        """禄存在命宫(子)，左邻父母(亥)= 陀罗，右邻兄弟(丑)= 擎羊 → 命中。"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["禄存"], "minor": []}
        palaces["父母"] = {"branch": "亥", "major": [], "minor": ["陀罗"]}
        palaces["兄弟"] = {"branch": "丑", "major": [], "minor": ["擎羊"]}
        chart = _make_chart(palaces)
        combo = detect_lu_cun_ya_tuo_jia(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-017"

    def test_negative_only_ya_present(self):
        """只有擎羊没有陀罗 → 不命中。"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["禄存"], "minor": []}
        palaces["兄弟"] = {"branch": "丑", "major": [], "minor": ["擎羊"]}
        chart = _make_chart(palaces)
        combo = detect_lu_cun_ya_tuo_jia(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None

    def test_negative_no_ya_or_tuo(self):
        """禄存邻宫既无擎羊也无陀罗 → 不命中。"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["禄存"], "minor": []}
        palaces["兄弟"] = {"branch": "丑", "major": [], "minor": ["左辅"]}
        chart = _make_chart(palaces)
        combo = detect_lu_cun_ya_tuo_jia(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None  # 邻宫无羊陀


class TestRule_018_LuMaJiaoChi:
    """ZHZ-CMB-018 禄马交驰。"""

    def test_positive(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["禄存"], "minor": ["天马"]}
        chart = _make_chart(palaces)
        combo = detect_lu_ma_jiao_chi(build_feature_bundle(chart, _resolver(chart)))
        assert combo is not None
        assert combo.combo_id == "ZHZ-CMB-018"

    def test_negative_different_palaces(self):
        """禄存和马在不同宫"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["禄存"], "minor": []}
        palaces["兄弟"] = {"branch": "丑", "major": [], "minor": ["天马"]}
        chart = _make_chart(palaces)
        combo = detect_lu_ma_jiao_chi(build_feature_bundle(chart, _resolver(chart)))
        assert combo is None


# ─────────────────────────────────────────────────────────────────────────
# [Group 4] DRAFT detector 必须强制返回 None（fail-closed 关键）
# ─────────────────────────────────────────────────────────────────────────

class TestDraftDetectorsFailClosed:
    """10 条 DRAFT detect 在任何 chart 下必须返回 None（不进入生产）。"""

    def test_all_draft_detectors_return_none_on_stub(self):
        stub = ZiweiChart(source="stub", birth_year=0)
        bundle = build_feature_bundle(stub, _resolver(stub))
        for det in DRAFT_DETECTORS:
            assert det(bundle) is None, f"{det.__name__} 不应在 stub 触发"

    def test_all_draft_detectors_return_none_on_empty(self):
        chart = _make_chart(_empty_palaces())
        bundle = build_feature_bundle(chart, _resolver(chart))
        for det in DRAFT_DETECTORS:
            assert det(bundle) is None, f"{det.__name__} 不应在 empty 触发"

    def test_all_draft_detectors_return_none_on_combined(self):
        """即便组合 chart 也不触发 DRAFT（防止误判上生产）"""
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"],
                           "minor": ["天机", "天同", "天梁", "太阴", "文昌"]}
        palaces["子女"] = {"branch": "卯", "major": ["七杀", "武曲"], "minor": []}
        chart = _make_chart(palaces)
        bundle = build_feature_bundle(chart, _resolver(chart))
        for det in DRAFT_DETECTORS:
            assert det(bundle) is None, f"{det.__name__} 不应在 combined 触发"


# ─────────────────────────────────────────────────────────────────────────
# [Group 5] 端到端 RuleGraph
# ─────────────────────────────────────────────────────────────────────────

class TestRuleGraphEndToEnd:
    """rule_graph.match_all 完整链路。"""

    def test_stub_returns_zero_matches(self):
        stub = ZiweiChart(source="stub", birth_year=0)
        result = make_zhongzhou_rule_graph().match_all(stub, _resolver(stub))
        assert result.matched_rules == ()
        assert result.implementation_status == "PARTIAL"
        assert result.rule_count == 10
        assert result.draft_count == 10

    def test_combined_chart_triggers_multiple(self):
        palaces = _empty_palaces()
        palaces["命宫"] = {"branch": "子", "major": ["紫微"],
                           "minor": ["天机", "天同", "天梁", "太阴", "文昌"]}
        palaces["子女"] = {"branch": "卯", "major": ["七杀", "武曲"], "minor": []}
        chart = _make_chart(palaces)
        result = make_zhongzhou_rule_graph().match_all(chart, _resolver(chart))
        assert len(result.matched_rules) >= 2
        for m in result.matched_rules:
            assert m.combo.evidence_grade == 1
            assert m.evidence.evidence_grade == 1
            assert m.judgment.combo_id == m.combo.combo_id

    def test_all_matches_have_evidence_grade_1(self):
        """所有触发的 combo 必须绑定证据等级 1 (王亭之原文)"""
        # 遍历多种 chart 验证 evidence_grade 一致性
        test_charts = []
        # chart 1: 机月同梁
        p1 = _empty_palaces()
        p1["命宫"] = {"branch": "子", "major": ["紫微"],
                      "minor": ["天机", "天同", "天梁", "太阴", "文昌"]}
        test_charts.append(_make_chart(p1))
        # chart 2: 杀破廉贪
        p2 = _empty_palaces()
        p2["命宫"] = {"branch": "子", "major": ["七杀"], "minor": []}
        test_charts.append(_make_chart(p2))
        # chart 3: 杀陷震兑
        p3 = _empty_palaces()
        p3["子女"] = {"branch": "卯", "major": ["七杀", "武曲"], "minor": []}
        test_charts.append(_make_chart(p3))

        for chart in test_charts:
            result = make_zhongzhou_rule_graph().match_all(chart, _resolver(chart))
            for m in result.matched_rules:
                assert m.evidence.evidence_grade == 1, \
                    f"{m.combo.combo_id} evidence_grade={m.evidence.evidence_grade} ≠ 1"
                assert m.evidence.source in {"d48733", "谈星1107", "谈星1108",
                                              "谈星1109", "谈星1113",
                                              "谈星1117", "谈星1126"}


# ─────────────────────────────────────────────────────────────────────────
# [Group 6] 派别隔离（不能污染 Sanhe / Feixing / Qintian）
# ─────────────────────────────────────────────────────────────────────────

class TestMethodIsolation:
    """ZhongzhouRuleGraph 只处理中州规则，不得影响其他 Method。"""

    def test_does_not_modify_chart(self):
        stub = ZiweiChart(source="stub", birth_year=0)
        before_palaces = dict(stub.palaces)
        make_zhongzhou_rule_graph().match_all(stub, _resolver(stub))
        # ZiweiChart 是 frozen=True dataclass，理论上不能修改
        # 这里再次确认 chart 内容一致
        assert stub.palaces == before_palaces

    def test_evidence_table_only_has_zhongzhou_sources(self):
        """EVIDENCE_TABLE 不得混入其他派别资料。"""
        forbidden_sources = {"sanhe", "feixing", "qintian", "三合", "飞星", "钦天"}
        for ev in EVIDENCE_TABLE.values():
            src_lower = ev.source.lower()
            for fs in forbidden_sources:
                assert fs not in src_lower, f"{ev.combo_id} source={ev.source} 含禁止源"


# ─────────────────────────────────────────────────────────────────────────
# [Group 7] evidence_grade 严格 = 1
# ─────────────────────────────────────────────────────────────────────────

class TestEvidenceGradeStrictlyOne:
    """P0-4-A 严格只允许 evidence_grade=1（王亭之原文）进生产。"""

    def test_all_production_combos_have_grade_1(self):
        for combo_id, ev in EVIDENCE_TABLE.items():
            assert ev.evidence_grade == 1, f"{combo_id} evidence_grade={ev.evidence_grade}"

    def test_evidence_table_size_matches_production_detectors(self):
        assert len(EVIDENCE_TABLE) == len(P0_4_A_PRODUCTION_DETECTORS) == 10
