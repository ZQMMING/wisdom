"""P1 Assertion Contract 测试 (DISPATCH_HERMES_ASSERTION_CONTRACT.md §12 验收)。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from tongshu.assertion.contract import (
    Assertion,
    AssertionInput,
    AssertionType,
    AuditFlag,
    Confidence,
    Direction,
    EvidenceRef,
    InputBoundaryError,
    StateKind,
    from_event_signal,
    insufficient_evidence,
)


# ---------- Rule 01/02: 输入边界 ----------

def test_input_boundary_accepts_legal_inputs():
    inp = AssertionInput(
        birth_datetime="1982-09-27T15:00",
        birth_location="香港",
        current_living_location="柏林",
    )
    assert inp.validate() == []


def test_input_boundary_requires_birth_datetime():
    assert "required" in AssertionInput(birth_datetime="").validate()[0]


def test_rule02_rejects_hidden_user_dependency():
    """禁止隐式用户依赖字段进入输入(from_user_dict 校验路径)。"""
    with pytest.raises(InputBoundaryError):
        AssertionInput.from_user_dict(
            {"birth_datetime": "1982-09-27", "occupation": "贸易"})
# ---------- Rule 04: Abstention ----------

def test_insufficient_evidence_factory():
    a = insufficient_evidence("健康", "单体系弱信号, 无流年引动")
    assert a.abstain is True
    assert a.confidence == Confidence.INSUFFICIENT_EVIDENCE
    assert a.assertion_type == AssertionType.INSUFFICIENT_EVIDENCE


def test_rule04_abstain_cannot_be_conditional_event():
    with pytest.raises(ValueError, match="Rule 04"):
        Assertion(
            subject="婚姻",
            assertion_type=AssertionType.CONDITIONAL_EVENT,
            abstain=True,
        )


# ---------- Rule 05: 人/事为隐变量 ----------

def test_rule05_conditions_only_on_conditional_types():
    with pytest.raises(ValueError, match="Rule 05"):
        Assertion(
            subject="事业",
            assertion_type=AssertionType.STRUCTURAL,
            conditions=("若从事贸易行业",),
        )


def test_conditional_event_allowed_with_conditions():
    a = Assertion(
        subject="财运",
        assertion_type=AssertionType.CONDITIONAL_EVENT,
        conditions=("若处于高流动资源整合型环境",),
        abstain=False,
        confidence=Confidence.LIKELY,
    )
    assert a.conditions


# ---------- 置信分级约束 ----------

def test_supported_requires_two_agreeing_systems():
    with pytest.raises(ValueError, match="SUPPORTED"):
        Assertion(
            subject="健康",
            assertion_type=AssertionType.STRUCTURAL,
            confidence=Confidence.SUPPORTED,
            evidence=(EvidenceRef(system="ziping", signal_ref="R1", agrees=True),),
        )
    a = Assertion(
        subject="健康",
        assertion_type=AssertionType.STRUCTURAL,
        confidence=Confidence.SUPPORTED,
        evidence=(
            EvidenceRef(system="ziping", signal_ref="R1", agrees=True),
            EvidenceRef(system="blind", signal_ref="B1", agrees=True),
        ),
    )
    assert a.confidence == Confidence.SUPPORTED


def test_audit_flag_carries_conflicting_engines():
    """V11: AuditFlag 记录反方向引擎, 用于驱动算法审计(替代废弃的CONFLICTED)."""
    flag = AuditFlag(
        topic="marriage",
        conflicting_engines=("ziwei: POSITIVE", "ziping: NEGATIVE"),
        hypothesis="多体系方向相反, 疑为算法错误",
    )
    assert flag.topic == "marriage"
    assert "ziwei: POSITIVE" in flag.conflicting_engines
    assert flag.action == "audit"
    d = flag.to_dict()
    assert d["conflicting_engines"] == ["ziwei: POSITIVE", "ziping: NEGATIVE"]


def test_assertion_accepts_audit_flags():
    """V11: Assertion 可携带审计信号(不进结论, 驱动审计)."""
    a = Assertion(
        subject="婚", assertion_type=AssertionType.ACTIVATION,
        confidence=Confidence.LIKELY,
        audit_flags=(
            AuditFlag(topic="婚", conflicting_engines=("ziwei: POSITIVE",)),
        ),
    )
    assert len(a.audit_flags) == 1
    assert a.audit_flags[0].topic == "婚"
    assert a.to_dict()["audit_flags"][0]["action"] == "audit"


# ---------- EVENT_SIGNAL 迁移映射 ----------

def test_from_event_signal_migration():
    es = {
        "system": "EVENT_TOPIC", "rule_id": "HLT-105", "theme": "健康",
        "direction": "DECREASE", "strength": 0.8,
        "time_scope": {"start_year": 2004, "end_year": 2004},
        "confidence": "LIKELY", "evidence": ["E-K2G-SHIPI-015"],
    }
    a = from_event_signal(es)
    assert a.subject == "健康"
    assert a.direction == Direction.NEGATIVE
    # strength 0.8 >=0.66 → LIKELY 提升为 SUPPORTED? 不 — 单体系不可 SUPPORTED
    # 迁移路径保守: 最高到 LIKELY
    assert a.confidence in (Confidence.LIKELY, Confidence.WEAK)


def test_to_dict_roundtrip_fields():
    a = Assertion(
        subject="环境",
        assertion_type=AssertionType.ENVIRONMENT_FIT,
        state=StateKind.ACTIVATION,
        direction=Direction.POSITIVE,
        mechanism="身强喜泄耗; 南方火场泄木气",
        time="常年",
        confidence=Confidence.WEAK,
        abstain=False,
    )
    d = a.to_dict()
    assert d["assertion_type"] == "ENVIRONMENT_FIT"
    assert d["state"] == "激活"
    assert d["abstain"] is False
