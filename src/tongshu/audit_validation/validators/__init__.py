"""audit_validation.validators — 渲染输出 3 层校验。

对齐 V3.6 §24 § “输出校验”：
    layer1_claim.py       — 表述覆盖（claim coverage）
    layer2_similarity.py  — 文本相似度（similarity）
    layer3_entailment.py  — 蕴含（entailment by judge model）
    result.py             — Layer1Result / Layer2Result / Layer3Result 数据类

原 validation/layer1.py · layer2.py · layer3.py 变为薄转发 shim。

调用方接口未变：
    from tongshu.validation.layer1 import validate_layer1   # 仍可用
    from tongshu.audit_validation.validators import validate_layer1  # 新路径

Version: 1.0.0  Created: 2026-08-20 (Phase 2 / Step 8)
"""

from .layer1_claim import validate_layer1
from .layer2_similarity import validate_layer2
from .layer3_entailment import validate_layer3
from .result import Layer1Result, Layer2Result, Layer3Result


__all__ = [
    "Layer1Result",
    "Layer2Result",
    "Layer3Result",
    "validate_layer1",
    "validate_layer2",
    "validate_layer3",
]
