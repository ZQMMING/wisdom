# -*- coding: utf-8 -*-
"""断言系统小测试 — 用真实命例跑完整引擎, 评估各主题输出质量."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.assertion.contract import AssertionInput
from tongshu.assertion.engine import AssertionEngine
from tongshu.assertion.topics import (
    CareerAssertionProducer, WealthAssertionProducer,
    MarriageAssertionProducer, HealthAssertionProducer,
)
from tongshu.assertion.classical_validation import cross_validate_systems

# 测试命例
CASES = [
    {
        "name": "乾造·甲寅(事业型)",
        "birth": (1974, 4, 28, 16, "male"),
        "bazi": [("甲", "寅"), ("戊", "辰"), ("己", "亥"), ("壬", "申")],
        "gender": "male", "birth_hour": "申", "birth_year": 1974,
        "focus_years": [1996, 2006, 2016],
    },
    {
        "name": "坤造·乙卯(婚姻型)",
        "birth": (1980, 9, 15, 10, "female"),
        "bazi": [("庚", "申"), ("乙", "酉"), ("辛", "巳"), ("癸", "巳")],
        "gender": "female", "birth_hour": "巳", "birth_year": 1980,
        "focus_years": [2003, 2008, 2013],
    },
]


def run_engine(birth, bazi, gender, birth_hour, birth_year, focus_years):
    inp = AssertionInput(birth_datetime="2000-01-01T00:00:00+08:00")
    context = {
        "birth": birth, "bazi": bazi, "gender": gender,
        "birth_hour": birth_hour, "birth_year": birth_year,
        "focus_years": focus_years,
    }
    engine = AssertionEngine()
    engine.register(CareerAssertionProducer())
    engine.register(WealthAssertionProducer())
    engine.register(MarriageAssertionProducer())
    engine.register(HealthAssertionProducer())
    results = engine.run(inp, chart={}, context=context)
    return results


for case in CASES:
    print("=" * 70)
    print(f"【{case['name']}】 {case['bazi']}  {case['gender']}")
    print("=" * 70)
    results = run_engine(
        case["birth"], case["bazi"], case["gender"],
        case["birth_hour"], case["birth_year"], case["focus_years"],
    )
    for a in results:
        subject_cn = {"career": "事业", "wealth": "财运", "marriage": "婚姻", "health": "健康"}.get(a.subject, a.subject)
        if a.abstain:
            print(f"\n  [{subject_cn}] ⚠ 拒断: {a.mechanism[:80]}")
            continue
        print(f"\n  [{subject_cn}] 方向={a.direction.value} 置信={a.confidence.value}")
        print(f"    mechanism: {a.mechanism[:130]}")
        if a.advice:
            print(f"    advice: {a.advice[:150]}")
        if a.classical_refs:
            print(f"    古籍依据: {a.classical_refs}")
    # 古籍交叉验证
    cv = cross_validate_systems(results)
    print(f"\n  古籍交叉验证: 覆盖率{cv['ref_coverage']} 覆盖{cv['cited_classics'][:4]}")
    print()
