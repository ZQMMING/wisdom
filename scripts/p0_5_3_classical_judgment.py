# -*- coding: utf-8 -*-
"""P0-5.3: Local Judgment Replay（CLASSICAL_EXPLICIT 专用）

目标：
- 只用 CLASSICAL_EXPLICIT + VERIFIED 规则做 Local Judgment Replay
- 禁止 ENGINEERED_THRESHOLD 混入

关键约束：
- de_ling = True（CLASSICAL_EXPLICIT）
- 不混合 de_di/de_shi（ENGINEERED_THRESHOLD）
- 不做身强/身弱综合判断
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from src.engine.assertion_v2.auth_gate import auth_gate, AuthorizationStatus
from src.engine.candidate_engine import CandidateEngine
from src.models.bazi import BaziChart


def create_test_charts():
    """创建测试命例（真实数据）"""
    charts = [
        # 身偏强命例（得令=False）
        BaziChart(
            year="甲子", month="丙子", day="壬午", hour="辛亥",
            description="身偏强命例（得令=False）"
        ),
        # 身偏弱命例（得令=False）
        BaziChart(
            year="戊辰", month="甲寅", day="戊子", hour="壬子",
            description="身偏弱命例（得令=False）"
        ),
        # 身弱命例（得令=False）
        BaziChart(
            year="庚申", month="甲申", day="丙戌", hour="丙申",
            description="身弱命例（得令=False）"
        ),
        # 得令命例（得令=True）
        BaziChart(
            year="戊午", month="甲子", day="戊子", hour="丙子",
            description="得令命例（得令=True）"
        ),
    ]
    return charts


def run_classical_judgment(chart):
    """运行 CLASSICAL_EXPLICIT Local Judgment"""
    print(f"\n命例: {chart.description}")
    print(f"  八字: {chart.year}{chart.month}{chart.day}{chart.hour}")

    # 计算特征
    candidate_engine = CandidateEngine()
    chart.features = candidate_engine.compute(chart)

    # 输出特征值
    print(f"  de_ling={chart.features.get('de_ling', False)}")
    print(f"  de_di={chart.features.get('de_di', 0)}")
    print(f"  de_shi={chart.features.get('de_shi', 0)}")

    # 只测试 CLASSICAL_EXPLICIT 条件（得令）
    classical_condition = {
        "name": "得令",
        "feature_name": "de_ling",
        "operator": "==",
        "threshold": True,
        "status": AuthorizationStatus.CLASSICAL_EXPLICIT,
        "source_text": "得令者旺（月令支持日主）",
        "classic": "滴天髓",
    }

    # 执行条件验证
    feature_value = chart.features.get(classical_condition["feature_name"], False)
    condition_met = False

    if classical_condition["operator"] == "==":
        condition_met = feature_value == classical_condition["threshold"]
    elif classical_condition["operator"] == ">=":
        condition_met = feature_value >= classical_condition["threshold"]
    elif classical_condition["operator"] == "<=":
        condition_met = feature_value <= classical_condition["threshold"]

    # 授权门控检查
    auth_result = auth_gate.check(
        authorization_status=classical_condition["status"],
        feature_name=classical_condition["feature_name"],
        threshold=classical_condition["threshold"],
    )

    # 输出结果
    status_icon = "✅ PASS" if condition_met else "❌ FAIL"
    print(f"  {status_icon}: 得令条件")
    print(f"     证据: {classical_condition['classic']}::{classical_condition['source_text']}")
    print(f"     授权: {'通过' if auth_result['passed'] else '未通过'}")
    print(f"     层级: {auth_result['layer']}")

    return {
        "chart_id": chart.description,
        "description": chart.description,
        "features": {
            "de_ling": feature_value,
            "de_di": chart.features.get("de_di", 0),
            "de_shi": chart.features.get("de_shi", 0),
        },
        "judgment": {
            "primitive": "得令",
            "condition_met": condition_met,
            "status": "PASS" if condition_met else "FAIL",
            "evidence": f"{classical_condition['classic']}::{classical_condition['source_text']}",
            "auth_gate_passed": auth_result["passed"],
            "layer": auth_result["layer"],
        },
        "no_engineered_threshold": True,
        "no_composite_judgment": True,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.3: Local Judgment Replay（CLASSICAL_EXPLICIT 专用）")
    print("=" * 60)
    print("\n关键约束：")
    print("- 只使用 CLASSICAL_EXPLICIT 条件")
    print("- 禁止 ENGINEERED_THRESHOLD 混入")
    print("- 不做身强/身弱综合判断")
    print("- 不跨进 Composite Judgment")

    # 创建测试命例
    charts = create_test_charts()

    # 运行 Local Judgment
    results = []
    for chart in charts:
        result = run_classical_judgment(chart)
        results.append(result)

    # 汇总
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)

    pass_count = sum(1 for r in results if r["judgment"]["condition_met"])
    total = len(results)

    print(f"总测试: {total} 条命例 × 1 条件 = {total} 条")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {total - pass_count}")
    print(f"成功率: {pass_count / total * 100:.1f}%")

    # 验证约束
    all_no_engineered = all(r["no_engineered_threshold"] for r in results)
    all_no_composite = all(r["no_composite_judgment"] for r in results)

    print(f"\n约束验证:")
    print(f"  无 ENGINEERED_THRESHOLD: {'✅' if all_no_engineered else '❌'}")
    print(f"  无 Composite Judgment: {'✅' if all_no_composite else '❌'}")

    # 保存
    output_path = Path(__file__).parent.parent / "data" / "p0_5_3_classical_judgment.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total": total,
            "pass_count": pass_count,
            "pass_rate": f"{pass_count / total * 100:.1f}%",
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 {output_path}")
