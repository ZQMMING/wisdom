# -*- coding: utf-8 -*-
"""一格两面合并裁决层

A+B俱足→化气型(争合降MID) / A独足→专旺型 / B独足→CANDIDATE / 皆空→REJECT
"""
from typing import Tuple, Optional
from engines.axis_xiuqi import XiuqiResult
from engines.axis_fude import FudeResult

def merge(x: XiuqiResult, f: FudeResult, key: str) -> Tuple[Optional[str], str, str, int]:
    """
    返回 (pattern_claimed, pattern_type, confidence, score)
    """
    a_ok = f.a1_day and f.a2_ju and f.a3_po
    b_ok = (x.b1a or x.b1b) and x.b2

    if a_ok and b_ok:
        ge = f.pattern_root.split("·")[1] if f.pattern_root else x.pattern_root.split("·")[1]
        conf = "MID" if x.b1b else "CONFIRMED"
        total = x.score + f.score + (1 if x.b3 else 0)
        return (f"一行成象·{ge}", "化气型", conf, total)

    if a_ok:
        if f.score >= 3 and not f.cai_po:
            conf = "CONFIRMED"
        else:
            conf = "MID"
        return (f.pattern_root, "专旺型", conf, f.score)

    if b_ok:
        return (x.pattern_root, "化气型", "CANDIDATE", x.score)

    return (None, None, "REJECT", 0)
