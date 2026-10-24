"""契约层子模块转发（单一来源 = ``heluo_engine.spec.canonical.judgment``）。

⚠ 2026-10-24 河洛回灌：见同目录 ``__init__.py`` 的说明 ——
   本文件原先独立定义 EvidenceCoverage / Judgment，与 vendor 侧字节相同
   但类身份不同。现改为纯转发。
"""
from __future__ import annotations

from heluo_engine.spec.canonical.judgment import EvidenceCoverage, Judgment

__all__ = ["EvidenceCoverage", "Judgment"]
