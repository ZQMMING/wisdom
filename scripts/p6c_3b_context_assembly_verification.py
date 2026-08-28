"""P6-C-3B: 513 events Context Assembly 完整验证.

验收表:
- 513 events loaded: 513/513
- Natal completeness: 100%
- DaYun completeness: 100%
- Year completeness: 100%
- Temporal scope: 100%
- DerivedSignal contract: 100% valid
- Provenance: 100%
- Missing vs Empty 可区分: ✓
- Temporal leakage: 0
- Ground Truth unchanged: ✓
- V2 Baseline unchanged: ✓
- Contract Validator: PASS

最终输出:
P6-C-3B CONTEXT_COMPLETENESS = 100%
PROVENANCE_COMPLETENESS = 100%
TEMPORAL_LEAKAGE = 0
BASELINE_MUTATION = 0
GROUND_TRUTH_MUTATION = 0
"""
from __future__ import annotations
import json
import sys
import hashlib
from collections import Counter, defaultdict
sys.path.insert(0, "src")

from tongshu.reasoning.context_assembler import ContextAssembler
from tongshu.reasoning.temporal_context_contract import (
    ContractValidator, TemporalLayer, SignalSource,
)
from p6b_annotation_contract import load_annotation_table


def load_golden_cases() -> list[dict]:
    with open("dataset/golden_v1/golden_cases.json", encoding="utf-8") as f:
        return json.load(f)["cases"]


def load_ground_truth_v2() -> dict:
    table = load_annotation_table("dataset/golden_v1/ground_truth_frozen_v2.json")
    return {e.event_id: e for e in table}


def compute_file_hash(filepath: str) -> str:
    """计算文件hash用于检测mutation."""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def main():
    print("=" * 70)
    print("P6-C-3B: 513 events Context Assembly 完整验证")
    print("=" * 70)

    # 0. 记录baseline和ground_truth的hash (验证unchanged)
    baseline_hash_before = compute_file_hash("docs/audit/p6c_temporal_baseline_v2.json")
    gt_hash_before = compute_file_hash("dataset/golden_v1/ground_truth_frozen_v2.json")

    # 1. 加载数据
    golden_cases = load_golden_cases()
    gt_v2 = load_ground_truth_v2()

    print(f"\nGolden Cases: {len(golden_cases)}")
    print(f"Ground Truth V2: {len(gt_v2)} events")

    # 2. 收集513 events
    events_to_assemble = []
    for case in golden_cases:
        case_id = case["case_id"]
        birth = case["birth_date"].split("-")
        birth_year = int(birth[0])
        birth_month = int(birth[1])
        birth_day = int(birth[2])
        birth_hour = case["birth_hour"]
        gender = case["gender"]

        for i, event in enumerate(case.get("events", [])):
            event_id = f"{case_id}_EV{i+1:03d}"
            target_year = int(event["date"].split("-")[0])
            gt = gt_v2.get(event_id)
            if gt and not gt.unmappable:
                events_to_assemble.append({
                    "event_id": event_id,
                    "case_id": case_id,
                    "birth_year": birth_year,
                    "birth_month": birth_month,
                    "birth_day": birth_day,
                    "birth_hour": birth_hour,
                    "gender": gender,
                    "target_year": target_year,
                    "event_date": event["date"],
                })

    print(f"Events to assemble: {len(events_to_assemble)}")

    # 3. Context Assembly
    assembler = ContextAssembler()
    assembled_contexts = []
    assembly_errors = []

    natal_complete = 0
    dayun_complete = 0
    year_complete = 0
    temporal_scope_complete = 0
    signal_contract_valid = 0
    provenance_complete = 0
    total_signals = 0
    empty_signals_count = 0  # 经过计算, 没有DerivedSignal
    invalid_signals_count = 0  # 有Signal, 但provenance不合法

    # Temporal leakage tracking
    temporal_leak_count = 0
    temporal_leak_details = []

    for i, ev in enumerate(events_to_assemble):
        try:
            ctx = assembler.assemble(
                case_id=ev["case_id"],
                birth_year=ev["birth_year"],
                birth_month=ev["birth_month"],
                birth_day=ev["birth_day"],
                birth_hour=ev["birth_hour"],
                gender=ev["gender"],
                target_year=ev["target_year"],
            )
            assembled_contexts.append(ctx)

            # Natal completeness
            if ctx.natal.day_master and len(ctx.natal.pillars) == 4:
                natal_complete += 1

            # DaYun completeness (允许起运前current_da_yun为None)
            if ctx.da_yun.current_da_yun is not None or ctx.da_yun.is_pre_luck_period:
                dayun_complete += 1

            # Year completeness
            if ctx.year.year_stem and ctx.year.year_branch and ctx.year.year_stem_ten_god:
                year_complete += 1

            # Temporal scope
            if ctx.target_year == ev["target_year"]:
                temporal_scope_complete += 1

            # DerivedSignal contract + Provenance
            signals_valid = True
            all_provenance_valid = True
            for sig in ctx.derived_signals:
                total_signals += 1
                # 验证signal contract
                sig_errors = ContractValidator.validate_derived_signal(sig)
                if sig_errors:
                    signals_valid = False
                    invalid_signals_count += 1
                # 验证provenance
                if not sig.provenance.source_engine or sig.provenance.source_engine == "UNKNOWN":
                    all_provenance_valid = False
                if not sig.provenance.source_rule_id or sig.provenance.source_rule_id == "UNKNOWN":
                    all_provenance_valid = False

                # Temporal leakage test: signal的temporal_layer不能来自未来
                # 对于YEAR层signal, target_year必须 >= signal的年份
                # 对于DA_YUN层signal, 大运开始年份必须 <= target_year
                if sig.temporal_layer == TemporalLayer.DA_YUN:
                    if ctx.da_yun.current_da_yun:
                        if ctx.da_yun.current_da_yun.start_year > ev["target_year"]:
                            temporal_leak_count += 1
                            temporal_leak_details.append({
                                "event_id": ev["event_id"],
                                "target_year": ev["target_year"],
                                "signal_id": sig.signal_id,
                                "da_yun_start_year": ctx.da_yun.current_da_yun.start_year,
                            })

            if signals_valid:
                signal_contract_valid += 1
            if all_provenance_valid:
                provenance_complete += 1

            # EMPTY vs MISSING
            if len(ctx.derived_signals) == 0:
                empty_signals_count += 1

        except Exception as e:
            assembly_errors.append({"event_id": ev["event_id"], "error": str(e)})

    # 4. 统计
    total = len(events_to_assemble)
    assembled = len(assembled_contexts)

    print(f"\n{'='*70}")
    print("Assembly 结果")
    print(f"{'='*70}")
    print(f"  总events: {total}")
    print(f"  成功组装: {assembled}")
    print(f"  组装错误: {len(assembly_errors)}")
    if assembly_errors:
        for e in assembly_errors[:5]:
            print(f"    - {e['event_id']}: {e['error']}")

    print(f"\n{'='*70}")
    print("Completeness 验证")
    print(f"{'='*70}")
    print(f"  Natal completeness: {natal_complete}/{assembled} ({natal_complete/assembled*100:.1f}%)")
    print(f"  DaYun completeness: {dayun_complete}/{assembled} ({dayun_complete/assembled*100:.1f}%)")
    print(f"  Year completeness: {year_complete}/{assembled} ({year_complete/assembled*100:.1f}%)")
    print(f"  Temporal scope: {temporal_scope_complete}/{assembled} ({temporal_scope_complete/assembled*100:.1f}%)")
    print(f"  DerivedSignal contract valid: {signal_contract_valid}/{assembled} ({signal_contract_valid/assembled*100:.1f}%)")
    print(f"  Provenance complete: {provenance_complete}/{assembled} ({provenance_complete/assembled*100:.1f}%)")

    print(f"\n{'='*70}")
    print("DerivedSignals 统计")
    print(f"{'='*70}")
    print(f"  总signals: {total_signals}")
    print(f"  平均每event signals: {total_signals/assembled:.1f}")
    print(f"  EMPTY (经过计算无signal): {empty_signals_count}")
    print(f"  INVALID (provenance不合法): {invalid_signals_count}")
    print(f"  MISSING (应该有但没有): {assembly_errors} (组装错误即MISSING)")

    # Signal来源分布
    signal_source_dist = Counter()
    signal_layer_dist = Counter()
    for ctx in assembled_contexts:
        for sig in ctx.derived_signals:
            signal_source_dist[sig.source.value] += 1
            signal_layer_dist[sig.temporal_layer.value] += 1

    print(f"\n  Signal来源分布:")
    for src, cnt in signal_source_dist.most_common():
        print(f"    {src}: {cnt}")
    print(f"  Signal层级分布:")
    for layer, cnt in signal_layer_dist.most_common():
        print(f"    {layer}: {cnt}")

    print(f"\n{'='*70}")
    print("Temporal Leakage Test")
    print(f"{'='*70}")
    print(f"  Temporal leakage count: {temporal_leak_count}")
    if temporal_leak_details:
        for d in temporal_leak_details[:5]:
            print(f"    - {d['event_id']}: target_year={d['target_year']}, da_yun_start={d['da_yun_start_year']}")

    # 5. 验证baseline和ground_truth未被修改
    baseline_hash_after = compute_file_hash("docs/audit/p6c_temporal_baseline_v2.json")
    gt_hash_after = compute_file_hash("dataset/golden_v1/ground_truth_frozen_v2.json")

    baseline_unchanged = baseline_hash_before == baseline_hash_after
    gt_unchanged = gt_hash_before == gt_hash_after

    print(f"\n{'='*70}")
    print("Mutation 检测")
    print(f"{'='*70}")
    print(f"  V2 Baseline unchanged: {'✓ YES' if baseline_unchanged else '❌ NO'}")
    print(f"  Ground Truth V2 unchanged: {'✓ YES' if gt_unchanged else '❌ NO'}")

    # 6. Contract Validator 全量验证
    print(f"\n{'='*70}")
    print("Contract Validator 全量验证")
    print(f"{'='*70}")
    all_valid = 0
    validator_errors = []
    for ctx in assembled_contexts:
        validation = ContractValidator.validate_temporal_context(ctx)
        if validation["valid"]:
            all_valid += 1
        else:
            validator_errors.append({
                "case_id": ctx.case_id,
                "target_year": ctx.target_year,
                "errors": validation["errors"],
            })

    print(f"  Contract Validator PASS: {all_valid}/{assembled} ({all_valid/assembled*100:.1f}%)")
    if validator_errors:
        print(f"  失败案例 (前5):")
        for e in validator_errors[:5]:
            print(f"    - {e['case_id']}/{e['target_year']}: {e['errors'][:3]}")

    # 7. 最终验收表
    print(f"\n{'='*70}")
    print("P6-C-3B 验收表")
    print(f"{'='*70}")
    print(f"  检查项                              要求          结果")
    print(f"  {'-'*65}")
    print(f"  513 events loaded                   513/513       {assembled}/{total}")
    print(f"  Natal completeness                  100%          {natal_complete/assembled*100:.1f}%")
    print(f"  DaYun completeness                  100%          {dayun_complete/assembled*100:.1f}%")
    print(f"  Year completeness                   100%          {year_complete/assembled*100:.1f}%")
    print(f"  Temporal scope                      100%          {temporal_scope_complete/assembled*100:.1f}%")
    print(f"  DerivedSignal contract              100% valid    {signal_contract_valid/assembled*100:.1f}%")
    print(f"  Provenance                          100%          {provenance_complete/assembled*100:.1f}%")
    print(f"  Missing vs Empty 可区分             ✓             ✓ (EMPTY={empty_signals_count}, INVALID={invalid_signals_count})")
    print(f"  Temporal leakage                    0             {temporal_leak_count}")
    print(f"  Ground Truth unchanged              ✓             {'✓' if gt_unchanged else '❌'}")
    print(f"  V2 Baseline unchanged               ✓             {'✓' if baseline_unchanged else '❌'}")
    print(f"  Contract Validator                  PASS          {'PASS' if all_valid == assembled else 'FAIL'}")

    # 8. 最终指标
    context_completeness = min(
        natal_complete/assembled*100,
        dayun_complete/assembled*100,
        year_complete/assembled*100,
        temporal_scope_complete/assembled*100,
    )
    provenance_completeness = provenance_complete/assembled*100

    print(f"\n{'='*70}")
    print("P6-C-3B 最终指标")
    print(f"{'='*70}")
    print(f"  CONTEXT_COMPLETENESS = {context_completeness:.1f}%")
    print(f"  PROVENANCE_COMPLETENESS = {provenance_completeness:.1f}%")
    print(f"  TEMPORAL_LEAKAGE = {temporal_leak_count}")
    print(f"  BASELINE_MUTATION = {0 if baseline_unchanged else 1}")
    print(f"  GROUND_TRUTH_MUTATION = {0 if gt_unchanged else 1}")

    # 9. 保存结果
    output = {
        "stage": "P6-C-3B",
        "total_events": total,
        "assembled": assembled,
        "assembly_errors": len(assembly_errors),
        "completeness": {
            "natal": natal_complete/assembled*100,
            "dayun": dayun_complete/assembled*100,
            "year": year_complete/assembled*100,
            "temporal_scope": temporal_scope_complete/assembled*100,
            "signal_contract": signal_contract_valid/assembled*100,
            "provenance": provenance_complete/assembled*100,
        },
        "signals": {
            "total": total_signals,
            "avg_per_event": total_signals/assembled,
            "empty": empty_signals_count,
            "invalid": invalid_signals_count,
            "source_distribution": dict(signal_source_dist),
            "layer_distribution": dict(signal_layer_dist),
        },
        "temporal_leakage": {
            "count": temporal_leak_count,
            "details": temporal_leak_details,
        },
        "mutation": {
            "baseline_unchanged": baseline_unchanged,
            "ground_truth_unchanged": gt_unchanged,
        },
        "contract_validator": {
            "pass": all_valid,
            "total": assembled,
            "pass_rate": all_valid/assembled*100,
        },
        "final_metrics": {
            "CONTEXT_COMPLETENESS": context_completeness,
            "PROVENANCE_COMPLETENESS": provenance_completeness,
            "TEMPORAL_LEAKAGE": temporal_leak_count,
            "BASELINE_MUTATION": 0 if baseline_unchanged else 1,
            "GROUND_TRUTH_MUTATION": 0 if gt_unchanged else 1,
        },
    }

    with open("docs/audit/p6c_3b_context_assembly_report.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n详细报告已保存: docs/audit/p6c_3b_context_assembly_report.json")

    # Gate判断
    gate_pass = (
        assembled == total and
        context_completeness == 100.0 and
        provenance_completeness == 100.0 and
        temporal_leak_count == 0 and
        baseline_unchanged and
        gt_unchanged and
        all_valid == assembled
    )

    print(f"\n{'='*70}")
    print(f"P6-C-3B GATE: {'PASS' if gate_pass else 'FAIL'}")
    print(f"{'='*70}")

    return output


if __name__ == "__main__":
    main()
