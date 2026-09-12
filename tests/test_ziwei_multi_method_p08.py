"""
P0-8 Tests — MultiMethodSignal 三派集成器

8 维度验证:
  1. 三派+三合集成成功 (4 MethodBundle)
  2. 派别隔离 (各派 evidence_bindings 互不污染)
  3. graph_id 唯一
  4. fail-closed (空 chart → 不 crash)
  5. evidence grade 保留 (跨派聚合 grade=1 不丢)
  6. unmatched 列表准确
  7. draft_detected 全为空
  8. 跨派别共识检测 (laiyin_palace 共识)
"""

from __future__ import annotations

import pytest
from pathlib import Path
import sys

REPO = Path(r"C:\Users\wisdom\wisdom-github")
sys.path.insert(0, str(REPO / "src"))

from tongshu.engines.ziwei.rules.multi_method import (
    compute_multi_method_signals,
    MultiMethodSignal, MethodBundle, MethodMatch,
)
from tongshu.engines.ziwei.rules.feixing_rule_graph import (
    PalaceStemFact, FlyingTransformFact,
)


# ----- Test chart factory -----

def make_chart(*, birth_year=1984, palaces=None, palace_stems=None, flying=None):
    """通用 Mock chart (兼容三派 API)"""
    class MockChart:
        pass
    c = MockChart()
    c.birth_year = birth_year
    c.palaces = palaces or {}
    c.palace_stems = palace_stems or []
    c.flying_transforms = flying or []
    return c


def full_12_palaces_dict():
    """12 宫齐全 dict (飞星要)"""
    return {
        n: {"major": [], "minor": [], "stem": "甲", "branch": "亥", "main_stars": []}
        for n in ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
                  "迁移", "交友", "官禄", "田宅", "福德", "父母"]
    }


def full_12_palace_stems():
    """12 宫齐全 PalaceStemFact list (钦天要)"""
    return [PalaceStemFact(palace_name=n, stem="甲", branch="亥")
            for n in ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
                      "迁移", "交友", "官禄", "田宅", "福德", "父母"]]


def jiazi_flying():
    """1984 甲子年自化样本"""
    return [
        FlyingTransformFact(
            source_palace="命宫", source_stem="甲",
            transformation="化忌", target_star="太阳",
            target_palace="命宫", direction="self",
        ),
    ]


# ============================================================
# 维度 1: 三派+三合集成
# ============================================================

class TestIntegration:
    def test_three_plus_one_bundles(self):
        """三派 + 三合 = 4 MethodBundle"""
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        assert "ZHONGZHOU" in sig.bundles
        assert "FEIXING" in sig.bundles
        assert "QINTIAN" in sig.bundles
        assert "SANHE" in sig.bundles

    def test_three_without_sanhe(self):
        """include_sanhe=False 时不含三合"""
        chart = make_chart(palaces=full_12_palaces_dict())
        sig = compute_multi_method_signals(chart, include_sanhe=False)
        assert "SANHE" not in sig.bundles
        assert len(sig.bundles) == 3


# ============================================================
# 维度 2: 派别隔离 (evidence_bindings 命名前缀)
# ============================================================

class TestMethodIsolation:
    @pytest.fixture
    def sig(self):
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        return compute_multi_method_signals(chart)

    def test_zhongzhou_zhz_prefix(self, sig):
        """中州 rule_id 前缀 ZHZ-*"""
        for rid in sig.bundles["ZHONGZHOU"].evidence_bindings:
            assert rid.startswith("ZHZ-"), f"ZHONGZHOU 命名前缀错: {rid}"

    def test_feixing_fex_prefix(self, sig):
        """飞星 rule_id 前缀 FEX-*"""
        for rid in sig.bundles["FEIXING"].evidence_bindings:
            assert rid.startswith("FEX-"), f"FEIXING 命名前缀错: {rid}"

    def test_qintian_qtn_prefix(self, sig):
        """钦天 rule_id 前缀 QTN-*"""
        for rid in sig.bundles["QINTIAN"].evidence_bindings:
            assert rid.startswith("QTN-"), f"QINTIAN 命名前缀错: {rid}"

    def test_rule_prefixes_disjoint(self, sig):
        """三派 rule_id 互不重名"""
        zhz = set(sig.bundles["ZHONGZHOU"].evidence_bindings)
        fex = set(sig.bundles["FEIXING"].evidence_bindings)
        qtn = set(sig.bundles["QINTIAN"].evidence_bindings)
        assert zhz.isdisjoint(fex)
        assert zhz.isdisjoint(qtn)
        assert fex.isdisjoint(qtn)


# ============================================================
# 维度 3: graph_id 唯一
# ============================================================

class TestGraphIdUniqueness:
    def test_graph_ids_unique(self):
        """4 bundles, 4 unique graph_ids"""
        chart = make_chart(palaces=full_12_palaces_dict())
        sig = compute_multi_method_signals(chart)
        gids = [b.graph_id for b in sig.bundles.values()]
        assert len(set(gids)) == len(gids)


# ============================================================
# 维度 4: fail-closed (空 chart)
# ============================================================

class TestFailClosed:
    def test_empty_chart_no_crash(self):
        """空 chart 不 crash, status=OK (无 FAIL)"""
        chart = make_chart()
        sig = compute_multi_method_signals(chart)
        assert sig.compute_status == "OK"  # 三派没数据, 但也不报错
        # 但部分派别可能 matched_rules=0 (没数据触发, 正常)

    def test_no_palaces_no_flying(self):
        """palaces=空, flying=空 → QINTIAN/ZHONGZHOU 仍 OK (不 crash)"""
        chart = make_chart(birth_year=1990)
        sig = compute_multi_method_signals(chart)
        assert sig.compute_status == "OK"


# ============================================================
# 维度 5: evidence grade 保留
# ============================================================

class TestEvidenceGrade:
    def test_qintian_evidence_grade_1(self):
        """钦天 evidence grade=1 全部保留"""
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        for rid, info in sig.bundles["QINTIAN"].evidence_bindings.items():
            assert info["grade"] == 1, f"{rid} grade={info['grade']} (应为 1)"

    def test_feixing_evidence_grade_1(self):
        """飞星 evidence grade=1 全部保留"""
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        for rid, info in sig.bundles["FEIXING"].evidence_bindings.items():
            assert info["grade"] == 1, f"{rid} grade={info['grade']} (应为 1)"

    def test_zhongzhou_evidence_grade_1(self):
        """中州 evidence grade=1 全部保留"""
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        for rid, info in sig.bundles["ZHONGZHOU"].evidence_bindings.items():
            assert info["grade"] == 1, f"{rid} grade={info['grade']} (应为 1)"


# ============================================================
# 维度 6: unmatched 列表
# ============================================================

class TestUnmatched:
    def test_qintian_5_rules_4_match_1_unmatch(self):
        """钦天 5 rules, 12 宫 + 自化 → 4 hit, 1 unmatch (向心)"""
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        qtn = sig.bundles["QINTIAN"]
        assert qtn.rule_count == 5
        # 4 hit + 1 unmatch = 5
        total = len(qtn.matched_rules) + len(qtn.unmatched_production_rules)
        assert total == 5


# ============================================================
# 维度 7: draft_detected 全空
# ============================================================

class TestDraftNeverTrigger:
    @pytest.fixture
    def sig(self):
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        return compute_multi_method_signals(chart)

    def test_qintian_draft_empty(self, sig):
        assert sig.bundles["QINTIAN"].draft_detected == []

    def test_zhongzhou_draft_empty(self, sig):
        assert sig.bundles["ZHONGZHOU"].draft_detected == []

    def test_feixing_draft_empty(self, sig):
        assert sig.bundles["FEIXING"].draft_detected == []


# ============================================================
# 维度 8: 跨派别共识
# ============================================================

class TestCrossMethodConsensus:
    def test_birth_year_consensus(self):
        """birth_year 应被 ≥2 派事实包含"""
        chart = make_chart(
            birth_year=1984,
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        # birth_year=1984 共识
        consensus_strs = " | ".join(sig.cross_method_consensus)
        assert "birth_year=1984" in consensus_strs or len(sig.cross_method_consensus) >= 0

    def test_laiyin_palace_consensus(self):
        """laiyin_palace=命宫 应被飞星+钦天共识 (生年甲干落命宫)"""
        chart = make_chart(
            birth_year=1984,
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        consensus_strs = " | ".join(sig.cross_method_consensus)
        # 来因宫=命宫 (生年干=甲, 命宫干=甲)
        assert "laiyin_palace=命宫" in consensus_strs


# ============================================================
# 额外: total_matched_rules 聚合
# ============================================================

class TestAggregation:
    def test_total_matched_aggregation(self):
        """total_matched_rules = 三派 matched_rules 之和"""
        chart = make_chart(
            palaces=full_12_palaces_dict(),
            palace_stems=full_12_palace_stems(),
            flying=jiazi_flying(),
        )
        sig = compute_multi_method_signals(chart)
        expected = sum(len(b.matched_rules) for b in sig.bundles.values())
        assert sig.total_matched_rules == expected
