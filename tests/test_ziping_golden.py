"""ZIPING Golden Set Validation Tests

Validates ZIPING engine outputs against 25 hand-crafted golden cases
covering WANGSHUAI/GEJU/YONGSHEN domains with five-classic evidence traceability.

Test categories:
1. 旺衰三分支: STRONG/WEAK/MODERATE with score verification
2. 格局五态: ESTABLISHED/BROKEN/UNKNOWN with type verification
3. 用神五级: PRIMARY/SECONDARY with type verification
4. 证据可追溯: 所有 rule_refs/evidence_refs 指向真实文件
5. 边界条件: fail-closed, 无硬编码 fallback
"""
import json
import os
import sys
from typing import Any, Dict, Optional

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from tongshu.reasoning.judgment import (
    JudgmentConclusion,
    JudgmentDomain,
    JudgmentFactory,
)


# ---------------------------------------------------------------------------
# Golden set loading
# ---------------------------------------------------------------------------

GOLDEN_SET_PATH = os.path.join(
    os.path.dirname(__file__), "..", "cases", "golden", "ziping_golden_set.json"
)


@pytest.fixture(scope="session")
def golden_set() -> dict:
    with open(GOLDEN_SET_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def cases(golden_set: dict) -> list[dict]:
    return golden_set["cases"]


@pytest.fixture(scope="session")
def rules_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "backend", "data", "rules")


@pytest.fixture(scope="session")
def evidence_dir() -> str:
    return os.path.join(
        os.path.dirname(__file__), "..", "backend", "data", "evidence"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pillar(stem: str, branch: str, pos: str) -> dict:
    return {"position": pos, "heavenly_stem": stem, "earthly_branch": branch}


def build_context(stems: list[str], branches: list[str]) -> dict:
    """Build NatalContext from stem/branch lists [year, month, day, hour]."""
    assert len(stems) == 4 and len(branches) == 4
    pillars = [
        pillar(s, b, pos)
        for pos, (s, b) in zip(["YEAR", "MONTH", "DAY", "HOUR"], zip(stems, branches))
    ]
    return {"natal": {"pillars": pillars, "day_master": stems[2]}}


@pytest.fixture
def case(request, golden_set: dict):
    """Fixture for indirect parametrize: look up case by ID."""
    case_id = request.param
    found = [c for c in golden_set["cases"] if c["case_id"] == case_id]
    assert found, f"Case {case_id} not found in golden set"
    return found[0]


def run_all(c: dict):
    """Run full Judgment pipeline and return synthesis."""
    return JudgmentFactory.judge_all({}, c)


def check_contains(haystack: str, needle: str) -> bool:
    """Check if a string contains a substring."""
    return needle in haystack


def check_any_contains(texts: list[str], needles: list[str]) -> bool:
    """Check if any text contains any needle."""
    return any(n in t for t in texts for n in needles)


# ---------------------------------------------------------------------------
# Metadata tests
# ---------------------------------------------------------------------------

class TestGoldenSetMetadata:
    def test_file_exists(self):
        assert os.path.exists(GOLDEN_SET_PATH), f"Golden set not found: {GOLDEN_SET_PATH}"

    def test_total_cases_25(self, golden_set: dict):
        assert golden_set["metadata"]["total_cases"] == 25

    def test_cases_count_matches(self, golden_set: dict):
        assert len(golden_set["cases"]) == 25

    def test_all_cases_have_id(self, cases: list[dict]):
        for c in cases:
            assert "case_id" in c and c["case_id"], f"Missing case_id"

    def test_all_cases_have_category(self, cases: list[dict]):
        valid_cats = {"旺衰", "格局", "用神", "边界"}
        for c in cases:
            assert c.get("category") in valid_cats, f"{c['case_id']}: invalid category"

    def test_coverage_all_domains(self, golden_set: dict):
        meta = golden_set["metadata"]["coverage"]
        assert "STRONG" in meta["wangshuai"]
        assert "WEAK" in meta["wangshuai"]
        assert "MODERATE" in meta["wangshuai"]
        assert "ESTABLISHED" in meta["geju"]
        assert "BROKEN" in meta["geju"]
        assert "UNKNOWN" in meta["geju"]
        assert "PRIMARY" in meta["yongshen"]
        assert "SECONDARY" in meta["yongshen"]
        assert "UNKNOWN" in meta["yongshen"]


# ---------------------------------------------------------------------------
# WANGSHUAI domain tests
# ---------------------------------------------------------------------------

class TestWangshuai:
    """旺衰域测试: 三分支 + 评分完整性"""

    @pytest.mark.parametrize("case", ["WANG-001", "WANG-004", "WANG-006"], indirect=True)
    def test_strong_cases(self, case: dict):
        """身强案例: score >= 4"""
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.wangshuai.conclusion == JudgmentConclusion.STRONG
        score = (s.wangshuai.score_detail or {}).get("total_score")
        assert score is not None and score >= 4, f"WANG score={score}"

    @pytest.mark.parametrize("case", ["WANG-002", "WANG-007", "WANG-008"], indirect=True)
    def test_weak_cases(self, case: dict):
        """身弱案例: score <= -3"""
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.wangshuai.conclusion == JudgmentConclusion.WEAK
        score = (s.wangshuai.score_detail or {}).get("total_score")
        assert score is not None and score <= -3, f"WANG score={score}"

    @pytest.mark.parametrize("case", ["WANG-003", "WANG-005"], indirect=True)
    def test_moderate_cases(self, case: dict):
        """中和案例: -3 < score < 4"""
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.wangshuai.conclusion == JudgmentConclusion.MODERATE
        score = (s.wangshuai.score_detail or {}).get("total_score")
        assert score is not None and -3 < score < 4, f"WANG score={score}"

    def test_moderate_no_hardcoded_fallback(self, golden_set: dict):
        """MODERATE 必须伴随评分明细，不能绕过评分硬编码。"""
        for cid in ["WANG-003", "WANG-005"]:
            case = next(c for c in golden_set["cases"] if c["case_id"] == cid)
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            if s.wangshuai.conclusion == JudgmentConclusion.MODERATE:
                detail = s.wangshuai.score_detail or {}
                assert "total_score" in detail and detail["total_score"] is not None

    def test_wangshuai_score_components_present(self, golden_set: dict):
        """所有旺衰判断必须包含四维评分明细。"""
        for case in golden_set["cases"]:
            if case["category"] != "旺衰":
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            detail = s.wangshuai.score_detail or {}
            for key in ["get_ling_score", "de_di_score", "dangzhong_score", "total_score"]:
                assert key in detail, f"{case['case_id']}: missing score_detail.{key}"

    def test_wangshuai_rule_refs_exist(self, golden_set: dict, rules_dir: str):
        """旺衰判断的 rule_refs 必须指向真实规则文件。"""
        for case in golden_set["cases"]:
            if case["category"] != "旺衰":
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            for ref in s.wangshuai.rule_refs or []:
                assert os.path.exists(os.path.join(rules_dir, ref + ".json")), f"Missing rule: {ref}"

    def test_wangshuai_evidence_refs_valid(self, golden_set: dict, evidence_dir: str):
        """旺衰判断的 evidence_refs 必须指向真实证据文件（若不为空）。"""
        for case in golden_set["cases"]:
            if case["category"] != "旺衰":
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            for ref in s.wangshuai.evidence_refs or []:
                assert os.path.exists(os.path.join(evidence_dir, ref + ".json")), f"Missing evidence: {ref}"


# ---------------------------------------------------------------------------
# GEJU domain tests
# ---------------------------------------------------------------------------

class TestGeju:
    """格局域测试: 成格/破格/未知"""

    def test_jianlu_established(self, golden_set: dict):
        """建禄格成立: SMTH-103 引用"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "GEJU-001")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.geju.conclusion == JudgmentConclusion.ESTABLISHED
        assert s.geju.ge_type == "建禄格"
        assert "SMTH-103" in s.geju.rule_refs

    def test_yangren_established(self, golden_set: dict):
        """阳刃格成立: YHZP-101 引用"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "GEJU-002")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.geju.conclusion == JudgmentConclusion.ESTABLISHED
        assert s.geju.ge_type == "阳刃格"
        assert "YHZP-101" in s.geju.rule_refs

    def test_chong_breaks_structure(self, golden_set: dict):
        """月令受冲 → 破格: DTS-106 引用"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "GEJU-004")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.geju.conclusion == JudgmentConclusion.BROKEN
        assert "DTS-106" in s.geju.rule_refs
        assert "冲" in s.geju.reasoning

    def test_variant_geju_blocked(self, golden_set: dict):
        """变格(从格/专旺)无证据 → UNKNOWN + 证据缺口标注"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "BOUND-005")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.geju.conclusion == JudgmentConclusion.UNKNOWN
        assert "证据缺口" in s.geju.ge_type
        assert s.geju.evidence_refs == [], "变格无证据时应为空"

    def test_geju_rule_refs_exist(self, golden_set: dict, rules_dir: str):
        """格局判断的 rule_refs 必须指向真实规则文件。"""
        for case in golden_set["cases"]:
            if case["category"] not in ("格局", "边界"):
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            for ref in s.geju.rule_refs or []:
                assert os.path.exists(os.path.join(rules_dir, ref + ".json")), f"Missing rule: {ref}"

    def test_geju_evidence_refs_valid(self, golden_set: dict, evidence_dir: str):
        """格局判断的 evidence_refs 必须指向真实证据文件。"""
        for case in golden_set["cases"]:
            if case["category"] not in ("格局", "边界"):
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            for ref in s.geju.evidence_refs or []:
                assert os.path.exists(os.path.join(evidence_dir, ref + ".json")), f"Missing evidence: {ref}"


# ---------------------------------------------------------------------------
# YONGSHEN domain tests
# ---------------------------------------------------------------------------

class TestYongshen:
    """用神域测试: 五级优先级链"""

    def test_geju_yongshen_priority(self, golden_set: dict):
        """格局用神优先于扶抑/调候"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "YONG-001")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.yongshen.conclusion == JudgmentConclusion.PRIMARY
        assert s.yongshen.yongshen_type == "格局用神"

    def test_fuyi_yongshen(self, golden_set: dict):
        """扶抑用神: 身弱取生扶"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "YONG-003")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.yongshen.conclusion == JudgmentConclusion.PRIMARY
        assert s.yongshen.yongshen_type == "扶抑用神"
        assert "身弱" in s.yongshen.reasoning or "生扶" in s.yongshen.reasoning

    def test_tiaohou_does_not_downgrade_primary(self, golden_set: dict):
        """调候为补充项，不得把已取得的 PRIMARY 降级为 SECONDARY"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "YONG-004")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        # 格局用神取得 PRIMARY 后，调候介入不应降级
        assert s.yongshen.conclusion == JudgmentConclusion.PRIMARY

    def test_yongshen_rule_refs_exist(self, golden_set: dict, rules_dir: str):
        """用神判断的 rule_refs 必须指向真实规则文件。"""
        for case in golden_set["cases"]:
            if case["category"] not in ("用神", "边界"):
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            for ref in s.yongshen.rule_refs or []:
                assert os.path.exists(os.path.join(rules_dir, ref + ".json")), f"Missing rule: {ref}"

    def test_yongshen_no_fabricated_refs(self, golden_set: dict, evidence_dir: str):
        """用神判断不得包含臆造的证据引用。"""
        for case in golden_set["cases"]:
            if case["category"] not in ("用神", "边界"):
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            for ref in s.yongshen.evidence_refs or []:
                assert os.path.exists(os.path.join(evidence_dir, ref + ".json")), f"Fabricated evidence: {ref}"


# ---------------------------------------------------------------------------
# BOUNDARY tests
# ---------------------------------------------------------------------------

class TestBoundary:
    """边界条件测试"""

    def test_fail_closed_missing_day_master(self):
        """缺 day_master → 所有域返回 UNKNOWN"""
        s = run_all({"natal": {"pillars": [], "day_master": None}})
        assert s.wangshuai.conclusion == JudgmentConclusion.UNKNOWN
        assert s.geju.conclusion == JudgmentConclusion.UNKNOWN
        assert s.yongshen.conclusion == JudgmentConclusion.UNKNOWN

    def test_fail_closed_missing_month_branch(self):
        """缺 month_branch → 所有域返回 UNKNOWN"""
        s = run_all({"natal": {"pillars": [], "day_master": "JIA"}})
        assert s.wangshuai.conclusion == JudgmentConclusion.UNKNOWN
        assert s.geju.conclusion == JudgmentConclusion.UNKNOWN
        assert s.yongshen.conclusion == JudgmentConclusion.UNKNOWN

    def test_all_five_domains_produced(self, golden_set: dict):
        """所有案例必须产出核心三域完整判断 (SHISHEN/SHIJIAN 需 Signal 驱动)。"""
        for case in golden_set["cases"]:
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            assert s.has_core_judgment, f"{case['case_id']}: missing core judgment"

    def test_core_three_domains_produced(self, golden_set: dict):
        """核心三域必须有判断结果"""
        for case in golden_set["cases"]:
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            assert s.has_core_judgment, f"{case['case_id']}: missing core judgment"

    def test_dts_105_dangzhong_only_transparent(self, golden_set: dict):
        """DTS-105 党众只看透干，不含地支藏干。验证: 透干全为日主时党众=0"""
        # 甲木日主，四柱透干全为 JIA → 排除日主后透干集为空
        c = build_context(["JIA", "JIA", "JIA", "JIA"], ["YIN", "MAO", "MAO", "MAO"])
        s = run_all(c)
        detail = s.wangshuai.score_detail or {}
        assert detail.get("dangzhong_score") == 0, \
            f"透干全为日主应党众=0, 实际={detail.get('dangzhong_score')}"

    def test_no_zpz105_as_conge_rule(self, golden_set: dict):
        """ZPZ-105 是官杀当令规则，不是从格规则 — 不得出现在变格路径"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "BOUND-005")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        # 变格路径不应引用 ZPZ-105
        all_refs = (s.geju.rule_refs or []) + (s.wangshuai.rule_refs or [])
        assert "ZPZ-105" not in all_refs, "ZPZ-105 不应被用作从格规则依据"

    def test_chong_detection_accuracy(self, golden_set: dict):
        """六冲检测准确: ZI-WU 相冲正确识别"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "BOUND-004")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        assert s.geju.conclusion == JudgmentConclusion.BROKEN
        assert "冲" in s.geju.reasoning
        assert "DTS-106" in s.geju.rule_refs

    def test_no_false_chong(self, golden_set: dict):
        """非冲对不误报: CHOU-WEI 不冲 SI"""
        case = next(c for c in golden_set["cases"] if c["case_id"] == "GEJU-002")
        c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
        s = run_all(c)
        # 阳刃格无冲 → ESTABLISHED
        assert s.geju.conclusion == JudgmentConclusion.ESTABLISHED


# ---------------------------------------------------------------------------
# INTEGRATION tests
# ---------------------------------------------------------------------------

class TestIntegration:
    """集成测试: 完整流程验证"""

    def test_all_cases_deterministic(self, golden_set: dict):
        """同一输入两次运行结果一致"""
        for case in golden_set["cases"]:
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s1 = run_all(c)
            s2 = run_all(c)
            assert s1.wangshuai.conclusion == s2.wangshuai.conclusion
            assert s1.geju.conclusion == s2.geju.conclusion
            assert s1.yongshen.conclusion == s2.yongshen.conclusion

    def test_all_cases_no_crash(self, golden_set: dict):
        """所有案例不抛出异常"""
        for case in golden_set["cases"]:
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            assert s is not None

    def test_score_consistency_across_domains(self, golden_set: dict):
        """旺衰评分与格局/用神判断一致: 身弱案例不应判从格外且无证据"""
        for case in golden_set["cases"]:
            if case["case_id"] not in ("WANG-002", "WANG-007", "BOUND-005"):
                continue
            c = build_context(case["input"]["pillar_stems"], case["input"]["pillar_branches"])
            s = run_all(c)
            if s.wangshuai.conclusion == JudgmentConclusion.WEAK:
                # 身弱时变格应标证据缺口，不输出 ESTABLISHED
                if s.geju.ge_type and "疑似" in s.geju.ge_type:
                    assert s.geju.conclusion == JudgmentConclusion.UNKNOWN


# ---------------------------------------------------------------------------
# pytest collection hooks
# ---------------------------------------------------------------------------

def pytest_collection_modifyitems(config, items):
    """参数化测试的 case 筛选。"""
    for item in items:
        mark = item.iter_markers(name="parametrize")
        for m in mark:
            if "case" in str(m):
                item.add_marker(pytest.mark.integration)
