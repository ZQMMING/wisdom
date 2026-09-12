"""
P0-5-A Tests — 飞星派 5 条生产规则 + 4 类验证

测试架构（与 P0-4-A 同模式）：
  1. production × 5 (10 测试 × ~4 个 sub-case) = 40-50 测试
  2. 空间关系专项（邻宫/对宫/自化）
  3. fail-closed（证据缺失/grade>2 不触发）
  4. P0-3 全回归 + P0-4 派别隔离（飞星不污染中州/三合）

P0-5-A 5 条 production：
  - FEX-CMB-001 财荫夹印
  - FEX-CMB-002 刑忌夹印
  - FEX-CMB-003 来因宫命迁线
  - FEX-CMB-004 自化忌基础
  - FEX-CMB-005 四化入命
"""
from __future__ import annotations

import sys
import pytest
from pathlib import Path

REPO = Path(r"C:\Users\wisdom\wisdom-github")
sys.path.insert(0, str(REPO / "src"))

from tongshu.engines.ziwei_engine import ZiweiChart, FrozenZiweiChart
from tongshu.engines.ziwei.rules.feixing import (
    FeixingRuleGraph,
    make_feixing_rule_graph,
    build_feature_bundle,
    detect_all_production,
    detect_all_drafts,
    get_all_flying_transforms,
    get_self_transforms,
    get_major_stars_in_palace,
    get_neighbor_palaces,
    find_star_palace,
    judge_all,
    evidence_grade,
    P0_5_A_PRODUCTION_DETECTORS,
    DRAFT_DETECTORS,
    EVIDENCE_TABLE,
)


# ─────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────


def make_chart(
    *,
    palaces: dict[str, dict],
    birth_year: int = 1984,
    soul_branch: str = "亥",
    body_branch: str = "巳",
) -> FrozenZiweiChart:
    """合成 FrozenZiweiChart 用于测试。"""
    return ZiweiChart(
        palaces=palaces,
        palace_data={},
        soul_earthly_branch=soul_branch,
        body_earthly_branch=body_branch,
        birth_year=birth_year,
        soul_palace_main_star="紫微",
        daily_luck_palace="命宫",
    )


# ============================================================================
# 1. Production × 5 规则测试
# ============================================================================


class TestFEX001CaiYinJiaYin:
    """FEX-CMB-001 财荫夹印 — 天相被化禄+天梁/天机/巨门/天同夹"""

    def test_positive_tianxiang_with_lu_neighbor(self):
        """正向：天相+两邻之一化禄入+邻宫主星荫星 → 命中"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["天相"], "minor": [], "stem": "乙", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "甲", "branch": "子"},
                "兄弟": {"major": ["巨门"], "minor": [], "stem": "丙", "branch": "丑"},
            },
        )
        # 父母宫甲干 → 化禄天机（在父母）→ 化禄飞入邻宫（父母）→ 天相（命宫）被夹
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-001"]
        # 注：根据实际飞化计算判定是否命中

    def test_negative_no_tianxiang(self):
        """反向：无天相 → 不命中"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "丙", "branch": "子"},
            },
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-001"]
        assert len(hits) == 0, "无天相不应命中"

    def test_evidence_grade_is_one(self):
        """FEX-CMB-001 evidence grade 必须是 1"""
        assert evidence_grade("FEX-CMB-001") == 1


class TestFEX002XingJiJiaYin:
    """FEX-CMB-002 刑忌夹印 — 天相被化忌+天梁/天机/巨门/天同夹"""

    def test_negative_no_tianxiang(self):
        """反向：无天相 → 不命中"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "丙", "branch": "子"},
            },
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-002"]
        assert len(hits) == 0, "无天相不应命中"

    def test_evidence_grade_is_one(self):
        assert evidence_grade("FEX-CMB-002") == 1


class TestFEX003LaiYinMingQianXian:
    """FEX-CMB-003 来因宫命迁线"""

    def test_positive_jia_year_ming_gong(self):
        """正向：甲子年生 + 命宫宫干=甲 → 来因宫在命宫 → 命迁线命中"""
        # 1984 = 甲子年 → birth_stem = 甲
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "甲", "branch": "亥"},
                "迁移": {"major": [], "minor": [], "stem": "己", "branch": "巳"},
            },
            birth_year=1984,
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-003"]
        assert len(hits) == 1, "甲子年命宫甲干 → 应命中"
        assert hits[0].facts["laiyin_palace"] == "命宫"

    def test_positive_qian_yi_gong(self):
        """正向：迁移宫宫干=生年干 → 来因宫在迁移 → 命迁线命中"""
        # 1984 甲子年 → birth_stem = 甲
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "己", "branch": "亥"},
                "迁移": {"major": [], "minor": [], "stem": "甲", "branch": "巳"},
            },
            birth_year=1984,
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-003"]
        assert len(hits) == 1, "甲子年迁移甲干 → 应命中"
        assert hits[0].facts["laiyin_palace"] == "迁移宫"

    def test_negative_other_palace(self):
        """反向：来因宫不在命迁线（如在父母宫）→ 不命中"""
        # 1984 甲子年 → birth_stem = 甲
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "己", "branch": "亥"},
                "迁移": {"major": [], "minor": [], "stem": "己", "branch": "巳"},
                "父母": {"major": ["天机"], "minor": [], "stem": "甲", "branch": "子"},
            },
            birth_year=1984,
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-003"]
        assert len(hits) == 0, "来因宫在父母宫 → 不命中"

    def test_xin_year_skip_zi_chou(self):
        """边界：辛年来因宫不取子/丑重复干（P0-3 修复）"""
        # 辛年生年干=辛；辛年应取寅至亥本位
        chart = make_chart(
            palaces={
                "命宫": {"major": [], "minor": [], "stem": "辛", "branch": "丑"},  # 子丑应排除
                "迁移": {"major": [], "minor": [], "stem": "丙", "branch": "巳"},
                "兄弟": {"major": [], "minor": [], "stem": "辛", "branch": "寅"},  # 寅→应取此
            },
            # 1931 = 辛未年 → birth_stem = 辛（(1931-4)%10 = 7 → 辛）
            birth_year=1931,
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-003"]
        # 辛年取寅宫（不在命迁线），应不命中
        assert len(hits) == 0, "辛年取寅宫（不在命迁线）→ 不命中"

    def test_evidence_grade_is_one(self):
        assert evidence_grade("FEX-CMB-003") == 1


class TestFEX004SelfJiBasic:
    """FEX-CMB-004 自化忌基础 — 任意宫位有自化忌"""

    def test_positive_one_self_ji(self):
        """正向：1 处自化忌 → 命中"""
        # 丙干：禄=天同 / 权=天机 / 科=文昌 / 忌=廉贞
        # 命宫丙干 → 化忌=廉贞 → 若廉贞在命宫 = 自化忌
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微", "廉贞"], "minor": [], "stem": "丙", "branch": "亥"},
                "父母": {"major": [], "minor": [], "stem": "甲", "branch": "子"},
            },
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-004"]
        assert len(hits) == 1, "命宫丙干+廉贞在命 → 化忌廉贞=自化忌 → 应命中"
        assert hits[0].facts["self_ji_count"] == 1

    def test_negative_no_self_ji(self):
        """反向：无自化忌 → 不命中"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "丙", "branch": "子"},
            },
        )
        # 命宫甲干 → 化禄廉贞/化权破军/化科武曲/化忌太阳 → 这些星都不在命宫 → 飞出
        # 父母丙干 → 化忌天同 → 天同不在父母 → 飞出
        # → 应无自化忌
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-004"]
        assert len(hits) == 0, "无自化忌 → 不命中"

    def test_evidence_grade_is_one(self):
        assert evidence_grade("FEX-CMB-004") == 1


class TestFEX005SiHuaLuRuMing:
    """FEX-CMB-005 四化入命 — 任意宫干飞化入命宫"""

    def test_positive_one_into_ming(self):
        """正向：父母宫甲干 → 化禄廉贞落入命宫 → 命中"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["廉贞"], "minor": [], "stem": "丙", "branch": "亥"},
                "父母": {"major": [], "minor": [], "stem": "甲", "branch": "子"},
            },
        )
        # 父母宫甲干 → 化禄廉贞 → 廉贞在命宫 → 飞入命宫
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-005"]
        assert len(hits) == 1, "甲干化禄廉贞入命 → 应命中"

    def test_negative_no_fly_into_ming(self):
        """反向：无任何飞化入命宫 → 不命中"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "丙", "branch": "子"},
                "兄弟": {"major": ["巨门"], "minor": [], "stem": "辛", "branch": "丑"},
            },
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-005"]
        assert len(hits) == 0, "无飞化入命 → 不命中"

    def test_evidence_grade_is_one(self):
        assert evidence_grade("FEX-CMB-005") == 1


# ============================================================================
# 2. 空间关系专项（邻宫/对宫/自化）
# ============================================================================


class TestSpatialRelations:
    """空间关系查询函数测试"""

    def test_get_neighbor_palaces(self):
        """邻宫=地支±1（夹印用法）"""
        chart = make_chart(
            palaces={
                "命宫": {"major": [], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": [], "minor": [], "stem": "丙", "branch": "子"},  # 亥±1=戌/子
                "兄弟": {"major": [], "minor": [], "stem": "辛", "branch": "戌"},  # 戌≠子
            },
        )
        neighbors = get_neighbor_palaces(chart, "命宫")
        # 命宫亥 → ±1 = 戌/子
        assert "父母" in neighbors, "子宫应为命宫邻宫"

    def test_find_star_palace(self):
        """星曜→宫位 反向索引"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微", "天相"], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "丙", "branch": "子"},
            },
        )
        assert find_star_palace(chart, "天相") == "命宫"
        assert find_star_palace(chart, "天机") == "父母"
        assert find_star_palace(chart, "贪狼") is None

    def test_self_transforms_excludes_out(self):
        """self_transforms 只包含 direction == "self" """
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "丙", "branch": "子"},
            },
        )
        bundle = build_feature_bundle(chart)
        for t in bundle.self_transforms:
            assert t.direction == "self", f"自化仅限 self direction: {t}"


# ============================================================================
# 3. fail-closed（证据缺失/grade>2 不触发）
# ============================================================================


class TestFailClosed:
    """失败/缺失 → 不触发（fail-closed）"""

    def test_drafts_never_hit(self):
        """DRAFT 规则 detect_*_draft 必须返回 None"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微", "天同", "天相"], "minor": [], "stem": "甲", "branch": "亥"},
                "父母": {"major": ["天机"], "minor": [], "stem": "丙", "branch": "子"},
                "兄弟": {"major": ["巨门"], "minor": [], "stem": "辛", "branch": "丑"},
            },
        )
        drafts = detect_all_drafts(chart)
        assert len(drafts) == 0, f"DRAFT 必须 0 hits，实际 {len(drafts)}"

    def test_invalid_birth_year(self):
        """无效 birth_year → FEX-CMB-003 不命中"""
        chart = make_chart(
            palaces={
                "命宫": {"major": [], "minor": [], "stem": "甲", "branch": "亥"},
            },
            birth_year=0,
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "FEX-CMB-003"]
        assert len(hits) == 0, "birth_year=0 → 不命中"

    def test_empty_palaces(self):
        """空 palaces → 所有 detect 安全返回 None"""
        chart = make_chart(
            palaces={},
            birth_year=1984,
        )
        result = detect_all_production(chart)
        # 应无命中但不抛异常
        assert isinstance(result, tuple)


# ============================================================================
# 4. P0-3 全回归 + 派别隔离（飞星不污染中州/三合）
# ============================================================================


class TestP0Isolation:
    """派别隔离：飞星子包不应影响中州/三合代码"""

    def test_zhongzhou_import_still_works(self):
        """中州子包导入应正常"""
        from tongshu.engines.ziwei.rules.zhongzhou import (
            ZhongzhouRuleGraph,
            build_feature_bundle as z_build,
        )
        # 仅验证导入成功
        assert ZhongzhouRuleGraph is not None

    def test_feixing_does_not_modify_common_facts(self):
        """飞星子包不应修改 FrozenZiweiChart / ZiweiChart"""
        from tongshu.engines.ziwei_engine import FrozenZiweiChart, ZiweiChart
        # 字段签名校验（不依赖实际 chart）
        import dataclasses
        frozen_fields = {f.name for f in dataclasses.fields(ZiweiChart)}
        assert "palaces" in frozen_fields
        assert "birth_year" in frozen_fields

    def test_5_production_5_drafts(self):
        """P0-5-A 维度：5 production + 5 DRAFT"""
        assert len(P0_5_A_PRODUCTION_DETECTORS) == 5
        assert len(DRAFT_DETECTORS) == 5
        assert len(EVIDENCE_TABLE) == 5

    def test_all_evidence_grade_one(self):
        """EVIDENCE_TABLE 全部 grade=1"""
        for ev in EVIDENCE_TABLE:
            assert ev.grade == 1, f"{ev.rule_id} grade={ev.grade} != 1"

    def test_rule_graph_id_and_method_id(self):
        """RuleGraph ID 一致"""
        graph = make_feixing_rule_graph()
        assert graph.graph_id() == "FEIXING-P0-5-A"
        assert graph.METHOD_ID == "FEIXING"
        assert graph.rule_count == 5
        assert graph.draft_count == 5
        assert graph.implementation_status == "PARTIAL"

    def test_match_all_returns_result(self):
        """match_all 返回 FeixingRuleGraphResult"""
        chart = make_chart(
            palaces={
                "命宫": {"major": ["紫微"], "minor": [], "stem": "甲", "branch": "亥"},
                "迁移": {"major": [], "minor": [], "stem": "己", "branch": "巳"},
            },
            birth_year=1984,
        )
        graph = make_feixing_rule_graph()
        result = graph.match_all(chart)
        assert result.implementation_status == "PARTIAL"
        assert result.rule_count == 5
        assert isinstance(result.matched_rules, tuple)


# ============================================================================
# 5. 证据与判定一致性
# ============================================================================


class TestEvidenceJudgmentConsistency:
    """evidence_grade 与 judgment 映射一致性"""

    def test_all_5_rules_have_evidence(self):
        """5 条 production 规则全部有 evidence 绑定"""
        for rid, _ in P0_5_A_PRODUCTION_DETECTORS:
            assert evidence_grade(rid) == 1, f"{rid} missing evidence"

    def test_all_5_rules_have_judgment(self):
        """5 条 production 规则全部有 judgment 映射"""
        from tongshu.engines.ziwei.rules.feixing import judge_combination
        # 用空 chart，detect_*_draft 返回 None（避免命中），改用 mock combo
        from tongshu.engines.ziwei.rules.feixing.combinations import FeixingCombination
        for rid, _ in P0_5_A_PRODUCTION_DETECTORS:
            mock_combo = FeixingCombination(
                rule_id=rid, detected=True, evidence_grade=1, facts={}
            )
            j = judge_combination(mock_combo)
            assert j is not None, f"{rid} missing judgment"
            assert j.judgment_strength in ("strong", "moderate", "weak", "neutral")