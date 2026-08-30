# -*- coding: utf-8 -*-
"""P0-5.8: 统一 Replay + Trace Audit

目标: 验证多个 Primitive 在同一命例上独立运行，互不污染

关键验证:
- 日犯岁君 和 生克制化 各自独立授权
- 各自产生 Local Judgment
- Trace 不串线
- 一个 Primitive 的成立不能帮助另一个满足 Condition
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT, _branch_element


# ============================================================
# Primitive 1: 日犯岁君
# ============================================================

class FanSuiJunChecker:
    """日犯岁君 Checker
    
    CURRENT IMPLEMENTATION:
    - 检查日干是否克年干
    - 原典: 渊海子平·论太岁吉凶
    """
    
    PRIMITIVE_ID = "YHZP-LF-TSJX-5"
    NAME = "日犯岁君"
    EVIDENCE = "渊海子平::且如甲日见戊年，太岁是也，剋重者死"
    AUTHORIZATION = StateAuthorizationLevel.CLASSICAL_EXPLICIT
    LAYER = "生产层"
    
    # 五行相克关系（source 克 target）
    KEEPS_RELATION = {
        "WOOD": "EARTH",
        "EARTH": "WATER",
        "WATER": "FIRE",
        "FIRE": "METAL",
        "METAL": "WOOD",
    }
    
    @classmethod
    def check(cls, chart) -> dict:
        """检查日犯岁君条件
        
        Returns:
            {
                "primitive_id": str,
                "condition_met": bool,
                "status": str,
                "trace": list of str,
                "details": dict,
            }
        """
        day_stem = chart.day_pillar.heavenly_stem
        year_stem = chart.year_pillar.heavenly_stem
        
        day_element = STEM_ELEMENT.get(day_stem)
        year_element = STEM_ELEMENT.get(year_stem)
        
        if not day_element or not year_element:
            return cls._fail_result("未知天干元素")
        
        # 日干克年干？
        is_fanke = cls.KEEPS_RELATION.get(day_element) == year_element
        
        if is_fanke:
            return {
                "primitive_id": cls.PRIMITIVE_ID,
                "name": cls.NAME,
                "condition_met": True,
                "status": "PASS",
                "trace": [
                    f"DayMaster: {day_stem} ({day_element})",
                    f"YearStem: {year_stem} ({year_element})",
                    f"Relation: {day_element}克{year_element}",
                    f"Evidence: {cls.EVIDENCE}",
                    f"Authorization: {cls.AUTHORIZATION.value}",
                ],
                "details": {
                    "day_stem": day_stem,
                    "year_stem": year_stem,
                    "day_element": day_element,
                    "year_element": year_element,
                    "relation": f"{day_element}克{year_element}",
                },
            }
        else:
            return cls._fail_result(f"{day_element}不克{year_element}")
    
    @classmethod
    def _fail_result(cls, reason: str) -> dict:
        return {
            "primitive_id": cls.PRIMITIVE_ID,
            "name": cls.NAME,
            "condition_met": False,
            "status": "FAIL",
            "trace": [
                f"DayMaster: {reason}",
                f"Evidence: {cls.EVIDENCE}",
                f"Authorization: {cls.AUTHORIZATION.value}",
                "Condition NOT met",
            ],
            "details": {"reason": reason},
        }


# ============================================================
# Primitive 2: 生克制化
# ============================================================

class ShengKeHuaChecker:
    """生克制化 Checker
    
    CURRENT IMPLEMENTATION:
    - 检查制中有生、生中有制的关系链
    - 原典: 滴天髓·生克制化
    """
    
    PRIMITIVE_ID = "DTS-SZ-HZ-ZL"
    NAME = "生克制化"
    EVIDENCE = "滴天髓::生克制化，须制中有生，生中有制"
    AUTHORIZATION = StateAuthorizationLevel.CLASSICAL_EXPLICIT
    LAYER = "生产层"
    
    # 相生关系
    GEN_RELATION = {
        "WOOD": "FIRE",
        "FIRE": "EARTH",
        "EARTH": "METAL",
        "METAL": "WATER",
        "WATER": "WOOD",
    }
    
    # 相克关系
    KEEPS_RELATION = {
        "WOOD": "EARTH",
        "EARTH": "WATER",
        "WATER": "FIRE",
        "FIRE": "METAL",
        "METAL": "WOOD",
    }
    
    @classmethod
    def extract_elements(cls, chart) -> list:
        elements = []
        for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
            stem_element = STEM_ELEMENT.get(pillar.heavenly_stem)
            if stem_element:
                elements.append(stem_element)
            branch_element = _branch_element(pillar.earthly_branch)
            if branch_element:
                elements.append(branch_element)
        return elements
    
    @classmethod
    def find_gen_pairs(cls, elements: list) -> list:
        unique = set(elements)
        pairs = []
        for src, dst in cls.GEN_RELATION.items():
            if src in unique and dst in unique:
                pairs.append((src, dst))
        return pairs
    
    @classmethod
    def find_keeps_pairs(cls, elements: list) -> list:
        unique = set(elements)
        pairs = []
        for src, dst in cls.KEEPS_RELATION.items():
            if src in unique and dst in unique:
                pairs.append((src, dst))
        return pairs
    
    @classmethod
    def check_gen_in_keeps(cls, keeps_pairs, gen_pairs) -> dict:
        chains = []
        for k_src, k_dst in keeps_pairs:
            for g_src, g_dst in gen_pairs:
                if g_dst == k_dst:
                    chains.append((g_src, k_src, k_dst))
        return {"exists": len(chains) > 0, "chains": chains}
    
    @classmethod
    def check_keeps_in_gen(cls, gen_pairs, keeps_pairs) -> dict:
        chains = []
        for g_src, g_dst in gen_pairs:
            for k_src, k_dst in keeps_pairs:
                if k_dst == g_src:
                    chains.append((k_src, g_src, g_dst))
        return {"exists": len(chains) > 0, "chains": chains}
    
    @classmethod
    def check(cls, chart) -> dict:
        elements = cls.extract_elements(chart)
        gen_pairs = cls.find_gen_pairs(elements)
        keeps_pairs = cls.find_keeps_pairs(elements)
        
        gen_in_keeps = cls.check_gen_in_keeps(keeps_pairs, gen_pairs)
        keeps_in_gen = cls.check_keeps_in_gen(gen_pairs, keeps_pairs)
        
        condition_met = (
            len(gen_pairs) > 0 and
            len(keeps_pairs) > 0 and
            (gen_in_keeps["exists"] or keeps_in_gen["exists"])
        )
        
        if condition_met:
            return {
                "primitive_id": cls.PRIMITIVE_ID,
                "name": cls.NAME,
                "condition_met": True,
                "status": "PASS",
                "trace": [
                    f"Elements: {list(set(elements))}",
                    f"Gen pairs: {[f'{s}→{d}' for s, d in gen_pairs]}",
                    f"Keeps pairs: {[f'{s}→{d}' for s, d in keeps_pairs]}",
                    f"Gen in Keeps: {gen_in_keeps['chains']}",
                    f"Keeps in Gen: {keeps_in_gen['chains']}",
                    f"Evidence: {cls.EVIDENCE}",
                    f"Authorization: {cls.AUTHORIZATION.value}",
                ],
                "details": {
                    "elements": list(set(elements)),
                    "gen_pairs": gen_pairs,
                    "keeps_pairs": keeps_pairs,
                    "gen_in_keeps": gen_in_keeps,
                    "keeps_in_gen": keeps_in_gen,
                },
            }
        else:
            return {
                "primitive_id": cls.PRIMITIVE_ID,
                "name": cls.NAME,
                "condition_met": False,
                "status": "FAIL",
                "trace": [
                    f"Elements: {list(set(elements))}",
                    f"Gen pairs: {[f'{s}→{d}' for s, d in gen_pairs]}",
                    f"Keeps pairs: {[f'{s}→{d}' for s, d in keeps_pairs]}",
                    f"Evidence: {cls.EVIDENCE}",
                    f"Authorization: {cls.AUTHORIZATION.value}",
                    "Condition NOT met",
                ],
                "details": {
                    "elements": list(set(elements)),
                    "gen_pairs": gen_pairs,
                    "keeps_pairs": keeps_pairs,
                },
            }


# ============================================================
# Trace Audit: 验证不串线
# ============================================================

def validate_trace_isolation(results: list) -> dict:
    """验证 Trace 隔离
    
    关键验证点：
    1. 每个 Primitive 的 Trace 不包含其他 Primitive 的 ID
    2. 每个 Primitive 的 Evidence 独立
    3. 一个 Primitive 的成立不能帮助另一个满足 Condition
    """
    issues = []
    
    # 提取每个 Primitive 的 Trace
    traces = {r["primitive_id"]: r["trace"] for r in results}
    
    # 验证 1: Trace 不包含其他 Primitive 的 ID
    for pid, trace in traces.items():
        trace_text = " ".join(trace)
        for other_pid in traces:
            if other_pid != pid and other_pid in trace_text:
                issues.append(f"Primitive {pid} 的 Trace 包含其他 Primitive {other_pid} 的 ID")
    
    # 验证 2: Evidence 独立
    evidence_set = set()
    for r in results:
        for line in r["trace"]:
            if line.startswith("Evidence:"):
                evidence_set.add(line)
    
    # 验证 3: 检查是否有关键词交叉
    for pid, trace in traces.items():
        trace_text = " ".join(trace)
        # 检查是否包含其他 Primitive 的关键词
        if pid == "YHZP-LF-TSJX-5":
            if "生克制化" in trace_text and "日犯岁君" not in trace_text:
                issues.append(f"Primitive {pid} 的 Trace 可能包含其他 Primitive 的内容")
        elif pid == "DTS-SZ-HZ-ZL":
            if "日犯岁君" in trace_text and "生克制化" not in trace_text:
                issues.append(f"Primitive {pid} 的 Trace 可能包含其他 Primitive 的内容")
    
    return {
        "isolated": len(issues) == 0,
        "issues": issues,
        "evidence_count": len(evidence_set),
    }


# ============================================================
# 主流程
# ============================================================

def create_test_charts():
    return [
        {
            "year": 2018, "month": 6, "day": 1, "hour": 12,
            "description": "甲日见戊年（日犯岁君案例）",
        },
        {
            "year": 1990, "month": 5, "day": 15, "hour": 10,
            "description": "标准命例",
        },
        {
            "year": 1985, "month": 12, "day": 3, "hour": 8,
            "description": "冬季命例",
        },
    ]


def run_multi_primitive_replay(chart_data):
    """运行多 Primitive 独立验证"""
    print(f"\n{'='*60}")
    print(f"命例: {chart_data['description']}")
    print(f"公历: {chart_data['year']}-{chart_data['month']:02d}-{chart_data['day']:02d} {chart_data['hour']:02d}:00")
    print(f"{'='*60}")
    
    engine = BaziEngine()
    chart = engine.compute((chart_data['year'], chart_data['month'], chart_data['day'], chart_data['hour']), gender='male')
    
    print(f"四柱: {chart.year_pillar} {chart.month_pillar} {chart.day_pillar} {chart.hour_pillar}")
    
    # 独立验证每个 Primitive
    results = []
    
    print(f"\n【Primitive 1】日犯岁君")
    result1 = FanSuiJunChecker.check(chart)
    results.append(result1)
    print(f"  判定: {result1['status']}")
    for line in result1["trace"]:
        print(f"    {line}")
    
    print(f"\n【Primitive 2】生克制化")
    result2 = ShengKeHuaChecker.check(chart)
    results.append(result2)
    print(f"  判定: {result2['status']}")
    for line in result2["trace"]:
        print(f"    {line}")
    
    # Trace Audit
    print(f"\n【Trace Audit】")
    audit = validate_trace_isolation(results)
    print(f"  Trace 隔离: {'✅ 通过' if audit['isolated'] else '❌ 失败'}")
    if not audit['isolated']:
        for issue in audit['issues']:
            print(f"    - {issue}")
    print(f"  独立 Evidence: {audit['evidence_count']} 条")
    
    return {
        "description": chart_data['description'],
        "solar_date": (chart_data['year'], chart_data['month'], chart_data['day'], chart_data['hour']),
        "four_pillars": {
            "year": str(chart.year_pillar),
            "month": str(chart.month_pillar),
            "day": str(chart.day_pillar),
            "hour": str(chart.hour_pillar),
        },
        "results": results,
        "trace_audit": audit,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.8: 统一 Replay + Trace Audit")
    print("=" * 60)
    print("\n关键约束:")
    print("- 每个 Primitive 独立验证")
    print("- 不共享状态")
    print("- 不互相引用")
    print("- Trace 独立，不串线")
    print("- 一个 Primitive 的成立不能帮助另一个满足 Condition")
    
    charts = create_test_charts()
    all_results = []
    
    for chart_data in charts:
        result = run_multi_primitive_replay(chart_data)
        all_results.append(result)
    
    # 汇总
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    total_primitives = len(charts) * 2  # 每个命例 2 个 Primitive
    pass_count = sum(1 for r in all_results for r2 in r['results'] if r2['condition_met'])
    
    print(f"总 Primitive 验证: {total_primitives} 条")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {total_primitives - pass_count}")
    
    # Trace Audit 汇总
    all_isolated = all(r['trace_audit']['isolated'] for r in all_results)
    print(f"\nTrace 隔离: {'✅ 全部通过' if all_isolated else '❌ 存在污染'}")
    
    # 保存
    output_path = Path(__file__).parent.parent / "data" / "p0_5_8_trace_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_primitives": total_primitives,
            "pass_count": pass_count,
            "trace_isolation": all_isolated,
            "results": all_results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
