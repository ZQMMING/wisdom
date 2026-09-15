"""五部 Phase 7-10 管线冒烟（judgment/golden/provenance/regression/production）。"""
from pathlib import Path

ROOT = Path(r"D:\shuntian-ziping-p0")

ENGINES = [
    ("ziping_zhenquan", "pzzq", "ZIPING_ZHENQUAN"),
    ("ditiansui", "dts", "DITIANSUI"),
    ("qiongtong_baojian", "qtbj", "QIONGTONG_BAOJIAN"),
    ("sanming_tonghui", "smth", "SANMING_TONGHUI"),
    ("shenfeng_tongkao", "sftk", "SHENFENG_TONGKAO"),
]

TEMPLATE = '''"""Phase 7-10 管线测试 · {dirname}。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from engines.common.facts_builder import FactsBuilder  # noqa: E402

REG = "{reg}"
ENGINE_ID = "{eid}"

CHART = {{
    "canonical_input": {{"ref": "p7t", "hash": "z" * 12}},
    "pillars": {{
        "year": {{"stem": "甲", "branch": "子"}},
        "month": {{"stem": "丙", "branch": "酉"}},
        "day": {{"stem": "甲", "branch": "午"}},
        "hour": {{"stem": "戊", "branch": "午"}},
    }},
    "gender": "男",
    "xunkong": {{"xun": "甲午旬"}},
    "shishen": {{"day_branch_hidden": ["丁"]}},
    "changsheng": {{}}, "nayin": {{}}, "relations": {{}},
}}


def test_judgment_assertions():
    from engines.{dirname}.judgment.judgment_builder import build_assertions
    r = FactsBuilder(engine=REG).build(CHART)
    asts = build_assertions(r)
    assert all(a["assertion_id"].startswith("AST-") for a in asts)
    for a in asts:
        assert a["fact_id"] and a["evidence_ids"]


def test_golden_runner_blocked():
    from engines.{dirname}.golden.golden_runner import GoldenRunner
    gr = GoldenRunner()
    assert gr.approved_technical_goldens() == []  # TG 未审批 → 阻塞（§67 不代行）


def test_provenance_record():
    from engines.{dirname}.provenance.provenance import ProvenanceRecorder
    rec = ProvenanceRecorder(engine=REG)
    p = rec.record({{}}, "ref", ["R1"], ["S1"], ["E1"])
    assert p["engine"] == ENGINE_ID
    assert p["rule_version"] and p["source_version"]


def test_regression_harness():
    from engines.{dirname}.regression.regression_harness import DEMO_CHART, compare, snapshot_all
    r1 = FactsBuilder(engine=REG).build(DEMO_CHART)
    r2 = FactsBuilder(engine=REG).build(DEMO_CHART)
    assert compare(snapshot_all(r1), snapshot_all(r2))["pass"]


def test_production_admission_blocks_on_golden():
    from engines.{dirname}.production.admission import ProductionAdmission
    res = ProductionAdmission(engine=REG).check()
    assert res["golden"]["status"] == "BLOCKED"      # TG 未审批
    assert res["admission"] == "NOT_ADMITTED"        # 不代行审批（§67）
    assert res["cross_domain"]["status"] == "PASS"
    for gate in ("contract", "schema", "rule", "evidence", "regression", "boundary", "provenance"):
        assert res[gate] is True, f"{{gate}} gate 失败: {{res[gate]}}"
'''

for dirname, reg, eid in ENGINES:
    p = ROOT / "engines" / dirname / "tests" / "test_phase_7_10.py"
    p.write_text(TEMPLATE.format(dirname=dirname, reg=reg, eid=eid), encoding="utf-8")
    print("OK", dirname)
print("done")
