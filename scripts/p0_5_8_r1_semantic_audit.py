# -*- coding: utf-8 -*-
"""P0-5.8-R1: 生克制化原典语义审计

目标: 审计"制中有生、生中有制"的语义完整性

关键问题:
1. "须"是必要条件还是充分条件？
2. 是否需要"所有"制都有生、"所有"生都有制？
3. "太过/不及"是否必须实现？
"""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT, _branch_element


def extract_elements(chart) -> list:
    """提取四柱五行"""
    elements = []
    for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
        stem_elem = STEM_ELEMENT.get(pillar.heavenly_stem)
        branch_elem = _branch_element(pillar.earthly_branch)
        if stem_elem: elements.append(stem_elem)
        if branch_elem: elements.append(branch_elem)
    return elements


def find_gen_pairs(elements: list) -> list:
    """查找所有相生关系对"""
    unique = set(elements)
    GEN = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
    return [(s, d) for s, d in GEN.items() if s in unique and d in unique]


def find_keeps_pairs(elements: list) -> list:
    """查找所有相克关系对"""
    unique = set(elements)
    KEEPS = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}
    return [(s, d) for s, d in KEEPS.items() if s in unique and d in unique]


def audit_sheng_ke_hua_semantics(chart, description: str):
    """审计生克制化的语义完整性"""
    print(f"\n{'='*60}")
    print(f"命例: {description}")
    print(f"四柱: {chart.year_pillar} {chart.month_pillar} {chart.day_pillar} {chart.hour_pillar}")
    
    elements = extract_elements(chart)
    gen_pairs = find_gen_pairs(elements)
    keeps_pairs = find_keeps_pairs(elements)
    
    print(f"五行: {elements}")
    print(f"唯一五行: {list(set(elements))}")
    print(f"相生关系: {len(gen_pairs)} 条")
    for pair in gen_pairs:
        print(f"  - {pair[0]}→{pair[1]}")
    print(f"相克关系: {len(keeps_pairs)} 条")
    for pair in keeps_pairs:
        print(f"  - {pair[0]}→{pair[1]}")
    
    # 检查每条相生关系是否有制（生中有制）
    print(f"\n【语义审计】")
    print(f"1. 检查'生中有制'（每条相生关系是否有克制）:")
    for g_src, g_dst in gen_pairs:
        has_control = any(k_dst == g_src for k_src, k_dst in keeps_pairs)
        status = "✅ 有制" if has_control else "❌ 无制"
        print(f"   {g_src}→{g_dst}: {status}")
    
    # 检查每条相克关系是否有生（制中有生）
    print(f"\n2. 检查'制中有生'（每条相克关系是否有生化）:")
    for k_src, k_dst in keeps_pairs:
        has_support = any(g_dst == k_dst for g_src, g_dst in gen_pairs)
        status = "✅ 有生" if has_support else "❌ 无生"
        print(f"   {k_src}→{k_dst}: {status}")
    
    # 判断条件
    all_gen_has_keeps = all(any(k_dst == g_src for k_src, k_dst in keeps_pairs) for g_src, g_dst in gen_pairs)
    all_keeps_has_gen = all(any(g_dst == k_dst for g_src, g_dst in gen_pairs) for k_src, k_dst in keeps_pairs)
    
    print(f"\n3. 语义强度判断:")
    print(f"   - 所有相生都有制: {'✅ 是' if all_gen_has_keeps else '❌ 否'}")
    print(f"   - 所有相克都有生: {'✅ 是' if all_keeps_has_gen else '❌ 否'}")
    
    # 当前实现 vs 严格语义
    current_impl = len(gen_pairs) > 0 and len(keeps_pairs) > 0 and (
        any(any(g_dst == k_dst for g_src, g_dst in gen_pairs) for k_src, k_dst in keeps_pairs) or
        any(any(k_dst == g_src for k_src, k_dst in keeps_pairs) for g_src, g_dst in gen_pairs)
    )
    strict_semantic = all_gen_has_keeps and all_keeps_has_gen
    
    print(f"\n4. 判定结果:")
    print(f"   - 当前实现（存在即可）: {'✅ PASS' if current_impl else '❌ FAIL'}")
    print(f"   - 严格语义（全覆盖）: {'✅ PASS' if strict_semantic else '❌ FAIL'}")
    
    return {
        "description": description,
        "gen_pairs": gen_pairs,
        "keeps_pairs": keeps_pairs,
        "all_gen_has_keeps": all_gen_has_keeps,
        "all_keeps_has_gen": all_keeps_has_gen,
        "current_impl_pass": current_impl,
        "strict_semantic_pass": strict_semantic,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.8-R1: 生克制化原典语义审计")
    print("=" * 60)
    
    engine = BaziEngine()
    
    # 测试命例
    test_cases = [
        ((2018, 6, 1, 12), "甲日见戊年（四柱全五行）"),
        ((1990, 5, 15, 10), "庚日见庚年（只有金火土）"),
        ((1985, 12, 3, 8), "丙日见乙年（只有水火土木）"),
        ((1986, 3, 21, 6), "甲日见丙年（只有木火水金）"),
    ]
    
    results = []
    for solar_date, desc in test_cases:
        chart = engine.compute(solar_date, gender='male')
        result = audit_sheng_ke_hua_semantics(chart, desc)
        results.append(result)
    
    # 汇总
    print(f"\n{'='*60}")
    print("语义审计汇总")
    print("=" * 60)
    
    print(f"\n当前实现 vs 严格语义对比:")
    for r in results:
        print(f"\n{r['description']}:")
        print(f"  当前实现: {'✅ PASS' if r['current_impl_pass'] else '❌ FAIL'}")
        print(f"  严格语义: {'✅ PASS' if r['strict_semantic_pass'] else '❌ FAIL'}")
        if r['current_impl_pass'] != r['strict_semantic_pass']:
            print(f"  ⚠️ 不一致！")
    
    # 结论
    print(f"\n{'='*60}")
    print("审计结论")
    print("=" * 60)
    print(f"\n1. 当前实现（存在即可）:")
    print(f"   - 只要命局中同时存在相生和相克关系，且至少有一条关系链")
    print(f"   - 就判定'生克制化'成立")
    print(f"   - 这是 CURRENT IMPLEMENTATION，不是完整经典定义")
    
    print(f"\n2. 严格语义（全覆盖）:")
    print(f"   - 要求'所有'相生关系都有制，'所有'相克关系都有生")
    print(f"   - 这可能过于严格，原典未明确说明")
    print(f"   - 需要进一步语义考证")
    
    print(f"\n3. 建议:")
    print(f"   - 保持 CURRENT IMPLEMENTATION 标注")
    print(f"   - 不要将当前实现视为完整经典定义")
    print(f"   - '太过/不及'部分保持 UNRESOLVED")
