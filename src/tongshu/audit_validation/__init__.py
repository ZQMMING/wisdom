"""audit_validation — 审计 + 校验集合包。

子包：
    gates/       V3.6 §22-23 · G1-G4 四道 Gate
    validators/  V3.6 §24 · Layer1/2/3 三层校验

原 audit/gates.py 与 validation/layer1.py · layer2.py · layer3.py 变为薄转发 shim
（保持公共接口可用）。

Version: 1.0.0  Created: 2026-08-20 (Phase 2 / Step 8)
"""

from . import gates, validators

__all__ = ["gates", "validators"]
