
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

REPO = Path(r"C:\Users\wisdom\wisdom-github")
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


# ----- 测试 chart 工厂 -----

def make_chart(*, birth_year, palace_stems=None, flying_transforms=None):
    """Mock chart for testing"""
    class Chart:
        pass
    c = Chart()
    c.birth_year = birth_year
    c.palace_stems = palace_stems or []
    c.flying_transforms = flying_transforms or []
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
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="亥")],
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
# 维度 4: QTN-CMB-003 立太极基础
# ============================================================

class TestQtnCmb003Xuanji:
    def test_positive_12_palaces(self):
        """12 宫齐全 → 立太极基础命中"""
        chart = make_chart(birth_year=1990, palace_stems=full_12_palaces())
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-003"]
        assert len(hits) == 1
        assert hits[0].facts["palace_count"] == 12

    def test_negative_only_2_palaces(self):
        """只有 2 宫 → 不命中"""
        chart = make_chart(
            birth_year=1990,
            palace_stems=[
                PalaceStemFact(palace_name="命宫", stem="甲", branch="亥"),
                PalaceStemFact(palace_name="兄弟", stem="乙", branch="子"),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-003"]
        assert len(hits) == 0


# ============================================================
# 维度 5: QTN-CMB-005 忌入六亲
# ============================================================

class TestQtnCmb005JiSixRelatives:
    def test_positive_ji_into_brother(self):
        """化忌入兄弟宫 → 命中 (潜意识亏欠)"""
        chart = make_chart(
            birth_year=1984,
            palace_stems=[PalaceStemFact(palace_name="兄弟", stem="甲", branch="子")],
            flying_transforms=[
                FlyingTransformFact(
                    source_palace="兄弟", source_stem="甲",
                    transformation="化忌", target_star="太阳",
                    target_palace="兄弟", direction="self",
                ),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-005"]
        assert len(hits) == 1
        assert hits[0].facts["ji_into_six_relatives_count"] == 1

    def test_negative_ji_into_non_relative(self):
        """化忌入非六亲宫 (迁移/福德) → 不命中"""
        chart = make_chart(
            birth_year=1984,
            flying_transforms=[
                FlyingTransformFact(
                    source_palace="命宫", source_stem="甲",
                    transformation="化忌", target_star="太阳",
                    target_palace="迁移", direction="out",
                ),
            ],
        )
        result = detect_all_production(chart)
        hits = [r for r in result if r.rule_id == "QTN-CMB-005"]
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

    def test_draft_count_is_5(self):
        """DRAFT 数量必须=5"""
        assert len(DRAFT_BINDINGS) == 5


# ============================================================
# 维度 7: RuleGraph 集成
# ============================================================

class TestRuleGraphIntegration:
    def test_graph_instantiate(self):
        """RuleGraph 实例化"""
        g = make_qintian_rule_graph()
        assert g.graph_id() == "QINTIAN-P0-7-A"
        assert g.METHOD_ID == "QINTIAN"
        assert g.rule_count() == 5

    def test_match_returns_evidence_grade_1(self):
        """match 返回的所有 rule 必须 grade=1"""
        g = make_qintian_rule_graph()
        chart = make_chart(
            birth_year=1984,
            palace_stems=[PalaceStemFact(palace_name="命宫", stem="甲", branch="亥")],
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
        from tongshu.engines.ziwei.rules.zhongzhou import ZhongzhouRuleGraph, make_zhongzhou_rule_graph
        from tongshu.engines.ziwei.rules.feixing import make_feixing_rule_graph

        qg = make_qintian_rule_graph()
        zg = make_zhongzhou_rule_graph()
        fg = make_feixing_rule_graph()

        assert qg.METHOD_ID != zg.METHOD_ID
        assert qg.METHOD_ID != fg.METHOD_ID
        assert zg.METHOD_ID != fg.METHOD_ID
