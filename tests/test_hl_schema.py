# -*- coding: utf-8 -*-
"""河洛 D 系列三补表结构测试(D-01/D-02/D-03)。

只读断言(information_schema / pg_constraint),不写数据;验证:
- 三表存在、关键列齐全
- status / conflict_type / link_type 的 CHECK 枚举正确
- hl_algorithm_evidence 对 hl_algorithms 的外键存在
- 索引存在(算法/证据/规则/案例反向可查所需)
"""
from __future__ import annotations

import pytest

from tongshu.db.kb_reader import with_kb_conn

EXPECTED_COLS = {
    "hl_algorithms": [
        "algorithm_id", "algorithm_code", "algorithm_name", "algorithm_domain",
        "algorithm_type", "hl_module", "input_spec", "output_spec",
        "source_scope", "rule_scope", "golden_scope", "status",
        "hl_calc_version", "description", "notes",
    ],
    "hl_ambiguities": [
        "ambiguity_id", "topic", "domain", "version_a", "version_b",
        "primary_source", "secondary_source", "conflict_type",
        "current_decision", "decision_reason", "status", "future_review",
        "evidence_refs",
    ],
    "hl_algorithm_evidence": [
        "link_id", "algorithm_id", "link_type", "passage_id", "evidence_id",
        "rule_id", "golden_case_id", "source_id",
    ],
}


def _columns(table: str):
    with with_kb_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name=%s",
            (table,),
        )
        return {r[0] for r in cur.fetchall()}


def _table_exists(table: str) -> bool:
    with with_kb_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema='public' AND table_name=%s",
            (table,),
        )
        return cur.fetchone()[0] == 1


def _check_enum(table: str, column: str) -> list[str]:
    """返回某列 CHECK 约束里用到的枚举字面量。"""
    with with_kb_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
            "WHERE conrelid = %s::regclass AND contype='c'",
            (table,),
        )
        out = []
        for (defn,) in cur.fetchall():
            if f"{column} " in defn or f"{column}=" in defn:
                out.append(defn)
        return out


@pytest.mark.parametrize("table,cols", EXPECTED_COLS.items())
def test_table_exists_with_expected_columns(table, cols):
    assert _table_exists(table), f"{table} 缺失(D 系列补表未落地?)"
    have = _columns(table)
    missing = set(cols) - have
    assert not missing, f"{table} 缺列: {sorted(missing)}"


def test_hl_algorithms_status_enum():
    defns = _check_enum("hl_algorithms", "status")
    assert defns, "hl_algorithms.status 无 CHECK"
    assert "OPEN" in defns[0] and "FROZEN" in defns[0] and "REJECTED" in defns[0]


def test_hl_algorithms_calc_version_enum():
    defns = _check_enum("hl_algorithms", "hl_calc_version")
    assert defns, "hl_algorithms.hl_calc_version 无 CHECK"
    for v in ("V0.1", "V0.9", "V1.0"):
        assert v in defns[0]


def test_hl_ambiguities_status_enum():
    defns = _check_enum("hl_ambiguities", "status")
    assert defns
    for v in ("OPEN", "UNDER_REVIEW", "RESOLVED", "FROZEN", "REJECTED"):
        assert v in defns[0]


def test_hl_ambiguities_conflict_type_enum():
    defns = _check_enum("hl_ambiguities", "conflict_type")
    assert defns
    for v in ("OCR_VARIANT", "EDITION_DIFFERENCE", "FORMULA_INTERPRETATION",
              "EXAMPLE_RULE_CONFLICT", "BOUNDARY_DEFINITION"):
        assert v in defns[0]


def test_hl_algorithm_evidence_link_type_enum():
    defns = _check_enum("hl_algorithm_evidence", "link_type")
    assert defns
    for v in ("ALGORITHM_PASSAGE", "ALGORITHM_EVIDENCE", "ALGORITHM_RULE",
              "ALGORITHM_GOLDEN"):
        assert v in defns[0]


def test_hl_algorithm_evidence_fk_to_algorithms():
    with with_kb_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT count(*) FROM pg_constraint "
            "WHERE conrelid='hl_algorithm_evidence'::regclass "
            "AND contype='f' AND confrelid='hl_algorithms'::regclass"
        )
        assert cur.fetchone()[0] == 1, "hl_algorithm_evidence 缺对 hl_algorithms 的外键"


def test_reverse_lookup_indexes_present():
    with with_kb_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT indexname FROM pg_indexes WHERE tablename='hl_algorithm_evidence'"
        )
        names = {r[0] for r in cur.fetchall()}
    for suffix in ("_ev_passage", "_ev_evidence", "_ev_rule", "_ev_golden"):
        assert any(suffix in n for n in names), f"缺索引 {suffix}"
