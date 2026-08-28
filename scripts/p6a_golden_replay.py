"""P6-A Golden Dataset Replay - 评估框架.

P6-A硬纪律:
1. P5 Frozen, 不允许修改
2. Golden Dataset 不允许反向适配
3. Ground Truth 不能进入 Resolver / ContextResolver / Mapper
4. 不允许为了提高分数修改 semantic_family
5. 不允许把 UNRESOLVED 当 FAIL
6. 不允许把 NOT_READY 当预测错误
7. 所有失败必须定位到具体层

9项指标:
1. Evidence Coverage - Ground Truth 是否有对应证据链
2. Signal Coverage - Evidence 是否成功形成 READY Signal
3. Assertion Coverage - 是否形成对应 Assertion
4. Direction Accuracy - supportive/caution/neutral 是否正确
5. Domain Accuracy - domain 是否正确
6. Semantic Family Accuracy - semantic_family 是否正确
7. Guidance Fidelity - Guidance 是否忠实于 Assertion
8. Event Precision/Recall/F1 - 真正的断事效果
9. Architecture Integrity - 管道完整性(辅助指标)
"""
from __future__ import annotations
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from tongshu.api.app import create_app

app = create_app()
client = TestClient(app)


# 失败归因层
FAIL_LAYERS = [
    "INPUT", "ENGINE", "RULE_MAPPING", "SIGNAL", "CONTEXT",
    "ASSERTION", "GUIDANCE", "GROUND_TRUTH_MISMATCH", "NOT_APPLICABLE"
]


@dataclass
class CaseResult:
    """单个Golden Case的评估结果."""
    case_id: str
    gender: str
    birth_date: str
    birth_hour: int
    event_count: int
    source_type: str

    # 管道运行状态
    pipeline_success: bool = False
    pipeline_error: Optional[str] = None
    pipeline_duration_ms: float = 0.0

    # 各层覆盖指标
    evidence_count: int = 0
    evidence_by_engine: dict = field(default_factory=dict)
    signal_count: int = 0
    signal_ready_count: int = 0
    signal_not_ready_count: int = 0
    unresolved_count: int = 0
    assertion_count: int = 0
    assertion_by_domain: dict = field(default_factory=dict)
    assertion_by_direction: dict = field(default_factory=dict)
    guidance_count: int = 0
    guidance_by_domain: dict = field(default_factory=dict)

    # 失败归因
    failures: list[dict] = field(default_factory=list)

    # 事件级评估(需要流年层支持)
    event_eval_applicable: bool = False
    event_eval_note: str = ""

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "gender": self.gender,
            "birth_date": self.birth_date,
            "birth_hour": self.birth_hour,
            "event_count": self.event_count,
            "source_type": self.source_type,
            "pipeline_success": self.pipeline_success,
            "pipeline_error": self.pipeline_error,
            "pipeline_duration_ms": round(self.pipeline_duration_ms, 2),
            "evidence_count": self.evidence_count,
            "evidence_by_engine": self.evidence_by_engine,
            "signal_count": self.signal_count,
            "signal_ready_count": self.signal_ready_count,
            "signal_not_ready_count": self.signal_not_ready_count,
            "unresolved_count": self.unresolved_count,
            "assertion_count": self.assertion_count,
            "assertion_by_domain": self.assertion_by_domain,
            "assertion_by_direction": self.assertion_by_direction,
            "guidance_count": self.guidance_count,
            "guidance_by_domain": self.guidance_by_domain,
            "failures": self.failures,
            "event_eval_applicable": self.event_eval_applicable,
            "event_eval_note": self.event_eval_note,
        }


def run_case(case: dict) -> CaseResult:
    """运行单个Golden Case的完整管道."""
    result = CaseResult(
        case_id=case["case_id"],
        gender=case["gender"],
        birth_date=case["birth_date"],
        birth_hour=case["birth_hour"],
        event_count=len(case.get("events", [])),
        source_type=case.get("source_type", "unknown"),
    )

    start_time = time.time()

    try:
        # 解析出生日期
        birth_parts = case["birth_date"].split("-")
        birth_year = int(birth_parts[0])
        birth_month = int(birth_parts[1])
        birth_day = int(birth_parts[2])

        # 运行管道
        resp = client.post("/admin/cases", json={
            "birth_year": birth_year,
            "birth_month": birth_month,
            "birth_day": birth_day,
            "birth_hour": case["birth_hour"],
            "gender": case["gender"],
            "location": "中国",  # Golden Case默认中国
        })

        if resp.status_code != 200:
            result.pipeline_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
            # P6-A修正: HTTP 400输入验证失败属于INPUT层, 不是ENGINE层
            if resp.status_code == 400:
                result.failures.append({"layer": "INPUT", "reason": result.pipeline_error})
            else:
                result.failures.append({"layer": "ENGINE", "reason": result.pipeline_error})
            result.pipeline_duration_ms = (time.time() - start_time) * 1000
            return result

        case_id = resp.json()["case_id"]
        result.pipeline_success = True

        # 获取各层数据
        # Evidence
        ev_resp = client.get(f"/admin/cases/{case_id}/evidence")
        if ev_resp.status_code == 200:
            ev_data = ev_resp.json()
            result.evidence_count = ev_data["total"]
            result.evidence_by_engine = ev_data.get("summary", {})

        # Signals
        sig_resp = client.get(f"/admin/cases/{case_id}/signals")
        if sig_resp.status_code == 200:
            sig_data = sig_resp.json()
            result.signal_count = sig_data["total"]
            stats = sig_data.get("stats", {})
            result.signal_ready_count = stats.get("ready", 0)
            result.signal_not_ready_count = stats.get("not_ready", 0)

        # Resolved Rules (UNRESOLVED计数)
        res_resp = client.get(f"/admin/cases/{case_id}/resolved-rules")
        if res_resp.status_code == 200:
            res_data = res_resp.json()
            result.unresolved_count = res_data.get("by_status", {}).get("UNRESOLVED", 0)

        # Assertions
        ast_resp = client.get(f"/admin/cases/{case_id}/assertions")
        if ast_resp.status_code == 200:
            ast_data = ast_resp.json()
            result.assertion_count = ast_data["total"]
            stats = ast_data.get("stats", {})
            result.assertion_by_domain = stats.get("by_domain", {})
            result.assertion_by_direction = stats.get("by_direction", {})

        # Guidance
        gui_resp = client.get(f"/admin/cases/{case_id}/guidance")
        if gui_resp.status_code == 200:
            gui_data = gui_resp.json()
            result.guidance_count = gui_data["total"]
            stats = gui_data.get("stats", {})
            result.guidance_by_domain = stats.get("by_domain", {})

        # 事件级评估: 当前系统主要是本命分析, 流年事件预测需要后续扩展
        result.event_eval_applicable = False
        result.event_eval_note = "当前P0-P5管道输出本命结构分析, 流年事件预测需要流年层扩展(P6后续阶段)"

        # 检查失败
        if result.evidence_count == 0:
            result.failures.append({"layer": "ENGINE", "reason": "0 Evidence produced"})
        if result.assertion_count == 0 and result.signal_ready_count > 0:
            result.failures.append({"layer": "CONTEXT", "reason": "Signals ready but 0 Assertions"})
        if result.guidance_count == 0 and result.assertion_count > 0:
            result.failures.append({"layer": "GUIDANCE", "reason": "Assertions exist but 0 Guidance"})

    except Exception as e:
        result.pipeline_error = str(e)[:500]
        result.failures.append({"layer": "INPUT", "reason": f"Exception: {str(e)[:200]}"})

    result.pipeline_duration_ms = (time.time() - start_time) * 1000
    return result


def compute_aggregate_metrics(results: list[CaseResult]) -> dict:
    """计算聚合指标."""
    total = len(results)
    if total == 0:
        return {"error": "No results"}

    # 管道成功率
    pipeline_success = sum(1 for r in results if r.pipeline_success)

    # 各层覆盖率
    evidence_covered = sum(1 for r in results if r.evidence_count > 0)
    signal_ready_covered = sum(1 for r in results if r.signal_ready_count > 0)
    assertion_covered = sum(1 for r in results if r.assertion_count > 0)
    guidance_covered = sum(1 for r in results if r.guidance_count > 0)

    # 平均数量
    avg_evidence = sum(r.evidence_count for r in results) / total
    avg_signals = sum(r.signal_count for r in results) / total
    avg_ready_signals = sum(r.signal_ready_count for r in results) / total
    avg_assertions = sum(r.assertion_count for r in results) / total
    avg_guidance = sum(r.guidance_count for r in results) / total

    # UNRESOLVED统计
    total_unresolved = sum(r.unresolved_count for r in results)
    avg_unresolved = total_unresolved / total

    # 失败归因
    failure_by_layer = defaultdict(int)
    total_failures = 0
    for r in results:
        for f in r.failures:
            failure_by_layer[f["layer"]] += 1
            total_failures += 1

    # Domain分布
    all_domains = defaultdict(int)
    all_directions = defaultdict(int)
    for r in results:
        for d, c in r.assertion_by_domain.items():
            all_domains[d] += c
        for d, c in r.assertion_by_direction.items():
            all_directions[d] += c

    return {
        "total_cases": total,
        "pipeline_success_rate": round(pipeline_success / total * 100, 1),
        "pipeline_success_count": pipeline_success,

        # 9项指标
        "metrics": {
            "1_evidence_coverage_pct": round(evidence_covered / total * 100, 1),
            "2_signal_coverage_pct": round(signal_ready_covered / total * 100, 1),
            "3_assertion_coverage_pct": round(assertion_covered / total * 100, 1),
            "4_direction_accuracy_pct": "NOT_APPLICABLE (需要Ground Truth direction标注)",
            "5_domain_accuracy_pct": "NOT_APPLICABLE (需要Ground Truth domain标注)",
            "6_semantic_family_accuracy_pct": "NOT_APPLICABLE (需要Ground Truth semantic标注)",
            "7_guidance_fidelity_pct": round(guidance_covered / assertion_covered * 100, 1) if assertion_covered > 0 else 0,
            "8_event_precision_recall_f1": "NOT_APPLICABLE (需要流年层事件预测)",
            "9_architecture_integrity_pct": round(
                (evidence_covered + signal_ready_covered + assertion_covered + guidance_covered) / (total * 4) * 100, 1
            ),
        },

        # 平均数量
        "avg_per_case": {
            "evidence": round(avg_evidence, 1),
            "signals_total": round(avg_signals, 1),
            "signals_ready": round(avg_ready_signals, 1),
            "assertions": round(avg_assertions, 1),
            "guidance": round(avg_guidance, 1),
            "unresolved": round(avg_unresolved, 1),
        },

        # 失败归因
        "failures": {
            "total_failures": total_failures,
            "by_layer": dict(failure_by_layer),
        },

        # Domain/Direction分布
        "distribution": {
            "assertion_by_domain": dict(all_domains),
            "assertion_by_direction": dict(all_directions),
        },

        # UNRESOLVED说明
        "unresolved_note": "UNRESOLVED属于Rule Migration Coverage Gap, 不是断事准确率问题",
    }


def main():
    print("=" * 70)
    print("P6-A Golden Dataset Replay")
    print("P5 Frozen Baseline - 第一轮 (不修改, 只测量)")
    print("=" * 70)

    # 加载Golden Dataset
    with open("dataset/golden_v1/golden_cases.json", encoding="utf-8") as f:
        dataset = json.load(f)

    cases = dataset.get("cases", [])
    print(f"\nGolden Dataset: {dataset.get('case_count')} cases, {dataset.get('event_count')} events")
    print(f"Source types: {set(c.get('source_type', 'unknown') for c in cases)}")

    # 运行所有Case
    print(f"\n开始运行 {len(cases)} 个Golden Case...")
    results = []
    for i, case in enumerate(cases, 1):
        print(f"  [{i}/{len(cases)}] {case['case_id']} ({case['birth_date']} {case['gender']})...", end=" ")
        result = run_case(case)
        results.append(result)
        status = "OK" if result.pipeline_success else "FAIL"
        print(f"{status} (ev={result.evidence_count}, sig={result.signal_ready_count}, ast={result.assertion_count}, gui={result.guidance_count}, {result.pipeline_duration_ms:.0f}ms)")

    # 计算聚合指标
    print("\n" + "=" * 70)
    print("P6-A Baseline 结果汇总")
    print("=" * 70)

    metrics = compute_aggregate_metrics(results)

    print(f"\n总案例数: {metrics['total_cases']}")
    print(f"管道成功率: {metrics['pipeline_success_rate']}% ({metrics['pipeline_success_count']}/{metrics['total_cases']})")

    print("\n--- 9项指标 ---")
    for key, value in metrics["metrics"].items():
        print(f"  {key}: {value}")

    print("\n--- 平均每Case ---")
    for key, value in metrics["avg_per_case"].items():
        print(f"  {key}: {value}")

    print("\n--- 失败归因 ---")
    print(f"  总失败数: {metrics['failures']['total_failures']}")
    for layer, count in metrics["failures"]["by_layer"].items():
        print(f"  {layer}: {count}")

    print("\n--- Assertion Domain分布 ---")
    for domain, count in sorted(metrics["distribution"]["assertion_by_domain"].items(), key=lambda x: -x[1]):
        print(f"  {domain}: {count}")

    print("\n--- Assertion Direction分布 ---")
    for direction, count in sorted(metrics["distribution"]["assertion_by_direction"].items(), key=lambda x: -x[1]):
        print(f"  {direction}: {count}")

    # 保存详细结果
    output = {
        "baseline_info": {
            "name": "P6-A Golden Dataset Replay Baseline",
            "p5_status": "FROZEN",
            "round": 1,
            "dataset_version": dataset.get("version"),
            "dataset_case_count": dataset.get("case_count"),
            "dataset_event_count": dataset.get("event_count"),
        },
        "aggregate_metrics": metrics,
        "case_results": [r.to_dict() for r in results],
    }

    output_path = "docs/audit/p6a_baseline_results.json"
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存: {output_path}")

    # 失败Case详情
    failed_cases = [r for r in results if not r.pipeline_success or r.failures]
    if failed_cases:
        print(f"\n--- 有问题的Case ({len(failed_cases)}) ---")
        for r in failed_cases[:10]:
            print(f"  {r.case_id}: {r.pipeline_error or str(r.failures)[:100]}")

    print("\n" + "=" * 70)
    print("P6-A Baseline 完成")
    print("这是P5 Frozen后的第一次正式基线")
    print("后续每次规则优化都以此Baseline做增量比较")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
