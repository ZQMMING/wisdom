"""
P1.2-A Contract Layer — Canonical Data Structures（**单一来源转发**）

V13 统一合约层：EngineEvidence → SemanticAtom → CanonicalAssertion → EvidenceCoverage → Judgment

⚠ 2026-10-24 河洛回灌：契约层改为**单一来源**。
   本仓曾同时存在两份**字节完全相同**的契约定义：
     · 本目录 ``tongshu/spec/canonical/``（主仓侧）
     · ``heluo_engine/spec/canonical/``（河洛独立包 vendor 副本）
   字节相同 ≠ 类身份相同 —— Python 中两份源码各自定义同名 dataclass，
   得到的��**两个互不相等、互相不可 isinstance 的类**。
   ⇒ 河洛引擎产出的 ``EngineEvidence`` 传进主仓契约层时，
     ``isinstance(x, EngineEvidence)`` 为 **False**，
     平台侧的 ``assert isinstance(..., CanonicalAssertion)`` 一类校验必然变红。
   （实测：tests/heluo/test_h12_diagnosis.py 的
     test_assertions_have_required_fields / test_judgment_authorized
     两条断言即因此失败。）

   现本目录**只做转发**，实体定义一律取自 ``heluo_engine.spec.canonical``：
   · 类身份唯一 ⇒ isinstance 跨包成立；
   · 物理文件不再重复 ⇒ 不存在「改一边忘另一边」的漂移。

   保持**子模块路径**（``tongshu.spec.canonical.assertion`` 等）可用，
   以免破坏既有直接子模块 import（见 tests/spec/test_vertical_slice*.py）。

Contract（定义见 heluo_engine/spec/canonical/）：
  - 所有 dataclass 使用 frozen=True（不可变）
  - 所有枚举继承 str, enum.Enum（方便 JSON 序列化）
  - evidence_id 与 rule_id 分离（V2 修正）
  - direction 仅在 Assertion 层由授权规则产生
  - judgment 需经授权规则，禁止聚合即判断
"""
from __future__ import annotations

from heluo_engine.spec.canonical import (
    AssertionDirection,
    CanonicalAssertion,
    EngineEvidence,
    EngineName,
    EvidenceCoverage,
    EvidenceRef,
    Judgment,
    SemanticAtom,
    TemporalScope,
)

__all__ = [
    "EngineEvidence",
    "EngineName",
    "TemporalScope",
    "SemanticAtom",
    "CanonicalAssertion",
    "AssertionDirection",
    "EvidenceRef",
    "EvidenceCoverage",
    "Judgment",
]
