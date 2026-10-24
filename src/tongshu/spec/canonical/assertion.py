"""契约层子模块转发（单一来源 = ``heluo_engine.spec.canonical.assertion``）。

⚠ 2026-10-24 河洛回灌：见同目录 ``__init__.py`` 的说明 ——
   本文件原先独立定义 CanonicalAssertion / AssertionDirection / EvidenceRef，
   与 vendor 侧字节相同但**类身份不同** ⇒ 河洛产出的断言对象
   在主仓侧 isinstance 校验恒为 False（实测 2 条诊断断言因此失败）。
   现改为纯转发。
"""
from __future__ import annotations

from heluo_engine.spec.canonical.assertion import (
    AssertionDirection,
    CanonicalAssertion,
    EvidenceRef,
)

__all__ = ["CanonicalAssertion", "AssertionDirection", "EvidenceRef"]
