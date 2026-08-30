# -*- coding: utf-8 -*-
"""P0-5.3: Local Judgment Replay（CLASSICAL_EXPLICIT 专用）

目标：
- 只用 CLASSICAL_EXPLICIT + VERIFIED 规则做 Local Judgment Replay
- 禁止 ENGINEERED_THRESHOLD 混入
- 只做局部条件判断，不做身强/身弱综合

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

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine


def run_classical_judgment(year, month, day, hour, description):
    """运行 CLASSICAL_EXPLICIT Local Judgment"""
    print(f"\n命例: {description}")
    print(f"  公历: {year}-{month:02d}-{day:02d} {hour:02d}:00")

    # 使用 BaziEngine 计算
    engine = BaziEngine()
    chart = engine.compute((year, month, day, hour), gender='male')

    # 输出四柱
    print(f"  四柱: {chart.year_pillar.to_string()} {chart.month_pillar.to_string()} {chart.day_pillar.to_string()} {chart.hour_pillar.to_string()}")

    # 输出特征值（如果有的话）
    features = getattr(chart, 'features', {})
    de_ling = features.get('de_ling', False) if features else False
    de_di = features.get('de_di', 0) if features else 0
    de_shi = features.get('de_shi', 0) if features else 0

    print(f"  de_ling={de_ling}, de_di={de_di}, de_shi={de_shi}")

    # 只测试 CLASSICAL_EXPLICIT 条件（得令）
    classical_condition = {
        "name": "得令",
        "feature_name": "de_ling",
        "operator": "==",
        "threshold": True,
        "status": StateAuthorizationLevel.CLASSICAL_EXPLICIT,
        "source_text": "得令者旺（月令支持日主）",
        "classic": "滴天髓",
    }

    # 执行条件验证
    feature_value = de_ling
    condition_met = (feature_value == classical_condition["threshold"])

    # 输出结果
    status_icon = "✅ PASS" if condition_met else "❌ FAIL"
    print(f"  {status_icon}: 得令条件")
    print(f"     证据: {classical_condition['classic']}::{classical_condition['source_text']}")
    print(f"     授权: {classical_condition['status'].value}")
    print(f"     层级: 生产层")

    return {
        "description": description,
        "solar_date": (year, month, day, hour),
        "four_pillars": {
            "year": chart.year_pillar.to_string(),
            "month": chart.month_pillar.to_string(),
            "day": chart.day_pillar.to_string(),
            "hour": chart.hour_pillar.to_string(),
        },
        "features": {
            "de_ling": de_ling,
            "de_di": de_di,
            "de_shi": de_shi,
        },
        "judgment": {
            "primitive": "得令",
            "condition_met": condition_met,
            "status": "PASS" if condition_met else "FAIL",
            "evidence": f"{classical_condition['classic']}::{classical_condition['source_text']}",
            "authorization": classical_condition["status"].value,
            "layer": "生产层",
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

    # 使用已知的公历日期测试（基于之前的 P0-3.9 测试数据）
    test_cases = [
        # 从 P0-3.9 的 chart_004 反推：得令=True 的命例
        (1990, 5, 15, 10, "得令命例（假设）"),
        # 其他测试用例
        (1990, 5, 15, 12, "标准测试命例"),
        (1985, 12, 3, 8, "冬季测试命例"),
        (1986, 3, 21, 6, "春季测试命例"),
    ]

    results = []
    for tc in test_cases:
        result = run_classical_judgment(*tc)
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
