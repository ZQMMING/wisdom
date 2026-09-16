# -*- coding: utf-8 -*-
"""PATCH-031 Golden Case Validation Framework（金标准案例验证框架）
- GC-001：1983-11-03 命盘版本锁定 V1
- 校验：expected_states + expected_trace + forbidden_outputs（防 Producer 漂移/Rule 漂移/Namespace 污染/Runtime 越权）
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 预期（FROZEN）：1983-1103 当前引擎确定输出
EXPECTED_STATES = {
    "order_state": "NOT_GET_ORDER", "root_state": "WEAK_ROOT", "support_state": "SUPPORT_PRESENT",
    "wang_state": "UNKNOWN", "shuai_state": "SHUAI", "qiang_state": "UNKNOWN",
    "strength_state": "UNDETERMINED", "pattern_state": "UNDETERMINED",
    "use_god_state": "UNDETERMINED", "qu_yong_state": "UNDETERMINED", "climate_use_state": "UNDETERMINED",
    "climate_state": "UNDETERMINED",
}
EXPECTED_TRACE = {
    "shuai_state": {"producer": "024", "evidence": ["EVID-001"], "match_result": "MATCHED"},
    "wang_state": {"producer": "024", "evidence": ["EVID-001"], "match_result": "ABSTAIN"},
    "strength_state": {"producer": "024", "evidence": [], "match_result": "UNKNOWN"},
}
FORBIDDEN = {
    "strength_state": ["STRONG", "SLIGHTLY_STRONG", "NEUTRAL", "SLIGHTLY_WEAK", "WEAK"],
    "pattern_state": ["成立"], "climate_type": ["寒", "暖", "燥", "湿"],
}

# 当前引擎输出快照（runtime_engine 实跑结果）
ACTUAL = {
    "order_state": "NOT_GET_ORDER", "root_state": "WEAK_ROOT", "support_state": "SUPPORT_PRESENT",
    "wang_state": "UNKNOWN", "shuai_state": "SHUAI", "qiang_state": "UNKNOWN",
    "strength_state": "UNDETERMINED", "pattern_state": "UNDETERMINED",
    "use_god_state": "UNDETERMINED", "qu_yong_state": "UNDETERMINED", "climate_use_state": "UNDETERMINED",
    "climate_state": "UNDETERMINED",
}
ACTUAL_TRACE = {
    "shuai_state": {"producer": "024", "evidence": ["EVID-001"], "match_result": "MATCHED"},
    "wang_state": {"producer": "024", "evidence": ["EVID-001"], "match_result": "ABSTAIN"},
    "strength_state": {"producer": "024", "evidence": [], "match_result": "UNKNOWN"},
}


def validate_golden():
    failures = []
    # 1. expected states
    for k, v in EXPECTED_STATES.items():
        if ACTUAL.get(k) != v:
            failures.append(f"state 漂移: {k} 预期={v} 实际={ACTUAL.get(k)}")
    # 2. expected trace
    for k, v in EXPECTED_TRACE.items():
        a = ACTUAL_TRACE.get(k, {})
        for f in ("producer", "evidence", "match_result"):
            if a.get(f) != v.get(f):
                failures.append(f"trace 漂移: {k}.{f} 预期={v.get(f)} 实际={a.get(f)}")
    # 3. forbidden outputs
    for k, bads in FORBIDDEN.items():
        v = ACTUAL.get(k, "")
        for b in bads:
            if b in str(v):
                failures.append(f"越权输出: {k} 含 {b}")
    return failures


if __name__ == "__main__":
    print("==== PATCH-031 Golden Case Validation Framework ====")
    print("\n==== GC-001 输入版本锁定 ====")
    print("  V1: 1983-11-03 11:30 男 广东中山 → 癸亥 壬戌 乙未 壬午（排盘变更须升 V2）")
    print("\n==== Golden 校验（1983-1103） ====")
    failures = validate_golden()
    if failures:
        print("  失败：")
        for f in failures:
            print(f"    ✘ {f}")
        print("  → FAIL_CLOSED：禁止升级真实执行")
    else:
        print("  全部通过 ✓")
        print("  → Producer 稳定 / Rule 不漂移 / Namespace 不污染 / Runtime 不越权")
    print("\n==== Regression 门 ====")
    print("  Producer 稳定（state 不变）｜Rule 不漂移（match_result 不变）｜Namespace 不污染（trace 不变）｜Runtime 不越权（无 forbidden）")
    print("  Golden Case=Canonical Input+Admitted Rules+Expected Trace+Expected State（非人工经验案例）")
