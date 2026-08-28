# -*- coding: utf-8 -*-
"""V11-P4: 断言层审计流程 — 反方向=算法错误, 定位可疑引擎, 驱动修复.

架构依据(V11): 互补不比较, 反方向=算法错误.
当主题层检测到多引擎方向相反(AuditFlag)时, 不输出"冲突"结论,
而是进入审计: 收集所有反方向信号, 按引擎冲突频率定位最可能出错的引擎.

用法:
    from tongshu.assertion.audit_report import build_audit_report
    report = build_audit_report([assertion1, assertion2, ...])
    # report: {
    #   "total_conflicts": int,
    #   "topics": {topic: [{engines, hypothesis, action}]},
    #   "engine_conflict_count": {engine: count},   # 越高的引擎越可疑
    #   "most_suspect_engine": str,                 # 最可能算法出错
    # }
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List


def build_audit_report(assertions) -> dict:
    """收集所有断言的 audit_flags, 输出结构化审计报告.

    - topics: 每个主题的反方向详情
    - engine_conflict_count: 各引擎在反方向中的出现频次(冲突越多越可疑)
    - most_suspect_engine: 冲突频次最高的引擎 = 最可能算法出错(需优先审计)
    """
    topics: Dict[str, List[dict]] = {}
    engine_counter: Counter = Counter()

    for a in assertions:
        flags = getattr(a, "audit_flags", None) or ()
        for flag in flags:
            topic = flag.topic
            topics.setdefault(topic, []).append({
                "conflicting_engines": list(flag.conflicting_engines),
                "hypothesis": flag.hypothesis,
                "action": flag.action,
            })
            for entry in flag.conflicting_engines:
                engine = entry.split(":")[0].strip()
                engine_counter[engine] += 1

    if not engine_counter:
        return {
            "total_conflicts": 0,
            "topics": {},
            "engine_conflict_count": {},
            "most_suspect_engine": None,
        }

    most_suspect = engine_counter.most_common(1)[0][0]
    return {
        "total_conflicts": sum(engine_counter.values()),
        "topics": topics,
        "engine_conflict_count": dict(engine_counter),
        "most_suspect_engine": most_suspect,
    }
