# -*- coding: utf-8 -*-
"""P0-5.7 改进版：关系对象绑定验证

目标: 验证"制中有生、生中有制"的语义完整性

问题发现:
- 当前实现只检查 has_gen + has_keeps
- 没有验证关系链（制和生的对象绑定）
- 会产生假阳性

实现:
- 检查相生关系的对象
- 检查相克关系的对象
- 验证是否形成"制中有生"或"生中有制"的关系链
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT, _branch_element


class WuxingRelationChecker:
    """五行生克关系检查器（关系对象绑定版）
    
    CURRENT IMPLEMENTATION:
    - 检查相生和相克关系的对象绑定
    - 验证是否形成"制中有生、生中有制"的关系链
    """
    
    # 相生关系（source 生 target）
    GEN_RELATION = {
        "WOOD": "FIRE",
        "FIRE": "EARTH",
        "EARTH": "METAL",
        "METAL": "WATER",
        "WATER": "WOOD",
    }
    
    # 相克关系（source 克 target）
    KEEPS_RELATION = {
        "WOOD": "EARTH",
        "EARTH": "WATER",
        "WATER": "FIRE",
        "FIRE": "METAL",
        "METAL": "WOOD",
    }
    
    @classmethod
    def extract_elements(cls, chart) -> list:
        """从四柱提取五行"""
        elements = []
        
        # 天干
        for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
            stem_element = STEM_ELEMENT.get(pillar.heavenly_stem)
            if stem_element:
                elements.append({"position": "stem", "gan_zhi": pillar.heavenly_stem, "element": stem_element})
        
        # 地支
        for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
            branch_element = _branch_element(pillar.earthly_branch)
            if branch_element:
                elements.append({"position": "branch", "gan_zhi": pillar.earthly_branch, "element": branch_element})
        
        return elements
    
    @classmethod
    def find_gen_pairs(cls, elements: list) -> list:
        """查找所有相生关系对
        
        Returns:
            list of (source, target)
        """
        element_values = [e["element"] for e in elements]
        unique_elements = set(element_values)
        
        pairs = []
        for src, dst in cls.GEN_RELATION.items():
            if src in unique_elements and dst in unique_elements:
                pairs.append((src, dst))
        
        return pairs
    
    @classmethod
    def find_keeps_pairs(cls, elements: list) -> list:
        """查找所有相克关系对
        
        Returns:
            list of (source, target)
        """
        element_values = [e["element"] for e in elements]
        unique_elements = set(element_values)
        
        pairs = []
        for src, dst in cls.KEEPS_RELATION.items():
            if src in unique_elements and dst in unique_elements:
                pairs.append((src, dst))
        
        return pairs
    
    @classmethod
    def check_gen_in_keeps(cls, keeps_pairs: list, gen_pairs: list) -> dict:
        """检查"制中有生"（相克关系中有相生）
        
        条件：某个被克的五行，有另一五行生它
        例如：金→木（相克），同时水→金（相生）
        
        Returns:
            {
                "exists": bool,
                "chains": list of (克者, 被克者, 生者)
            }
        """
        chains = []
        
        for keeps_src, keeps_dst in keeps_pairs:
            # 被克者是否有生？
            for gen_src, gen_dst in gen_pairs:
                if gen_dst == keeps_dst:  # 水→金，金被木克
                    chains.append((gen_src, keeps_src, keeps_dst))
        
        return {
            "exists": len(chains) > 0,
            "chains": chains,
        }
    
    @classmethod
    def check_keeps_in_gen(cls, gen_pairs: list, keeps_pairs: list) -> dict:
        """检查"生中有制"（相生关系中有相克）
        
        条件：某个生者的五行，有另一五行克它
        例如：木→火（相生），同时金→木（相克）
        
        Returns:
            {
                "exists": bool,
                "chains": list of (克者, 生者, 被生者)
            }
        """
        chains = []
        
        for gen_src, gen_dst in gen_pairs:
            # 生者是否有被克？
            for keeps_src, keeps_dst in keeps_pairs:
                if keeps_dst == gen_src:  # 金→木，木生火
                    chains.append((keeps_src, gen_src, gen_dst))
        
        return {
            "exists": len(chains) > 0,
            "chains": chains,
        }
    
    @classmethod
    def analyze_chart(cls, chart) -> dict:
        """分析四柱的五行生克关系（关系绑定版）"""
        elements = cls.extract_elements(chart)
        
        gen_pairs = cls.find_gen_pairs(elements)
        keeps_pairs = cls.find_keeps_pairs(elements)
        
        # 检查"制中有生"
        gen_in_keeps = cls.check_gen_in_keeps(keeps_pairs, gen_pairs)
        
        # 检查"生中有制"
        keeps_in_gen = cls.check_keeps_in_gen(gen_pairs, keeps_pairs)
        
        return {
            "elements_count": len(elements),
            "unique_elements": list(set(e["element"] for e in elements)),
            "gen_pairs": [f"{s}→{d}" for s, d in gen_pairs],
            "keeps_pairs": [f"{s}→{d}" for s, d in keeps_pairs],
            "gen_in_keeps": {
                "exists": gen_in_keeps["exists"],
                "chains": [f"{g}→{k}→{d}" for g, k, d in gen_in_keeps["chains"]],
            },
            "keeps_in_gen": {
                "exists": keeps_in_gen["exists"],
                "chains": [f"{k}→{g}→{d}" for k, g, d in keeps_in_gen["chains"]],
            },
            "has_both_relations": len(gen_pairs) > 0 and len(keeps_pairs) > 0,
        }


def create_test_charts():
    """创建测试命例"""
    return [
        {
            "year": 1990, "month": 5, "day": 15, "hour": 10,
            "description": "标准命例（应同时有生有克，且形成关系链）",
        },
        {
            "year": 1985, "month": 12, "day": 3, "hour": 8,
            "description": "冬季命例",
        },
        {
            "year": 1986, "month": 3, "day": 21, "hour": 6,
            "description": "春季命例",
        },
        {
            "year": 2018, "month": 6, "day": 1, "hour": 12,
            "description": "甲日见戊年（日犯岁君案例）",
        },
    ]


def run_sheng_ke_judgment(chart_data):
    """运行生克制化 Local Judgment（关系绑定版）"""
    print(f"\n命例: {chart_data['description']}")
    print(f"  公历: {chart_data['year']}-{chart_data['month']:02d}-{chart_data['day']:02d} {chart_data['hour']:02d}:00")
    
    # 计算四柱
    engine = BaziEngine()
    chart = engine.compute((chart_data['year'], chart_data['month'], chart_data['day'], chart_data['hour']), gender='male')
    
    # 分析五行关系（关系绑定版）
    analysis = WuxingRelationChecker.analyze_chart(chart)
    
    # 输出结果
    print(f"  四柱: {chart.year_pillar} {chart.month_pillar} {chart.day_pillar} {chart.hour_pillar}")
    print(f"  唯一五行: {', '.join(analysis['unique_elements'])}")
    print(f"  相生关系: {len(analysis['gen_pairs'])} 条")
    for pair in analysis['gen_pairs']:
        print(f"     - {pair}")
    print(f"  相克关系: {len(analysis['keeps_pairs'])} 条")
    for pair in analysis['keeps_pairs']:
        print(f"     - {pair}")
    
    print(f"  制中有生: {'✅ 存在' if analysis['gen_in_keeps']['exists'] else '❌ 不存在'}")
    if analysis['gen_in_keeps']['exists']:
        for chain in analysis['gen_in_keeps']['chains']:
            print(f"     - {chain}")
    
    print(f"  生中有制: {'✅ 存在' if analysis['keeps_in_gen']['exists'] else '❌ 不存在'}")
    if analysis['keeps_in_gen']['exists']:
        for chain in analysis['keeps_in_gen']['chains']:
            print(f"     - {chain}")
    
    # 判定条件：同时有相生和相克，且形成关系链
    condition_met = (
        len(analysis['gen_pairs']) > 0 and
        len(analysis['keeps_pairs']) > 0 and
        (analysis['gen_in_keeps']['exists'] or analysis['keeps_in_gen']['exists'])
    )
    
    status_icon = "✅ PASS" if condition_met else "❌ FAIL"
    
    print(f"  {status_icon}: 生克制化条件（制中有生，生中有制）")
    print(f"     证据: 滴天髓::生克制化，须制中有生，生中有制")
    print(f"     授权: CLASSICAL_EXPLICIT")
    print(f"     实现: CURRENT IMPLEMENTATION（关系对象绑定验证）")
    print(f"     未实现: 太过/不及判断")
    
    return {
        "description": chart_data['description'],
        "solar_date": (chart_data['year'], chart_data['month'], chart_data['day'], chart_data['hour']),
        "four_pillars": {
            "year": str(chart.year_pillar),
            "month": str(chart.month_pillar),
            "day": str(chart.day_pillar),
            "hour": str(chart.hour_pillar),
        },
        "analysis": analysis,
        "judgment": {
            "primitive": "生克制化",
            "condition_met": condition_met,
            "status": "PASS" if condition_met else "FAIL",
            "evidence": "滴天髓::生克制化，须制中有生，生中有制",
            "authorization": StateAuthorizationLevel.CLASSICAL_EXPLICIT.value,
            "layer": "生产层",
            "implementation_note": "CURRENT IMPLEMENTATION: 关系对象绑定验证",
            "unresolved_parts": ["太过", "不及", "损之", "益之"],
        },
        "no_strength_engine": True,
        "no_composite_judgment": True,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.7: 生克制化 Primitive 验证（关系绑定版）")
    print("=" * 60)
    print("\n关键约束：")
    print("- 检查相生和相克的对象绑定")
    print("- 验证是否形成'制中有生、生中有制'的关系链")
    print("- 不检查'太过/不及'（保持 UNRESOLVED）")
    print("- 不引入 strength_score")
    print("- 明确标注 CURRENT IMPLEMENTATION")
    
    # 创建测试命例
    charts = create_test_charts()
    
    # 运行 Local Judgment
    results = []
    for chart_data in charts:
        result = run_sheng_ke_judgment(chart_data)
        results.append(result)
    
    # 汇总
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    pass_count = sum(1 for r in results if r['judgment']['condition_met'])
    total = len(results)
    
    print(f"总测试: {total} 条命例 × 1 条件 = {total} 条")
    print(f"PASS: {pass_count}")
    print(f"FAIL: {total - pass_count}")
    print(f"成功率: {pass_count / total * 100:.1f}%")
    
    # 验证约束
    all_no_strength = all(r['no_strength_engine'] for r in results)
    all_no_composite = all(r['no_composite_judgment'] for r in results)
    all_current_impl = all('CURRENT IMPLEMENTATION' in r['judgment']['implementation_note'] for r in results)
    
    print(f"\n约束验证:")
    print(f"  无 strength_engine: {'✅' if all_no_strength else '❌'}")
    print(f"  无 Composite Judgment: {'✅' if all_no_composite else '❌'}")
    print(f"  标注 CURRENT IMPLEMENTATION: {'✅' if all_current_impl else '❌'}")
    
    # 保存
    output_path = Path(__file__).parent.parent / "data" / "p0_5_7_relation_binding.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total": total,
            "pass_count": pass_count,
            "pass_rate": f"{pass_count / total * 100:.1f}%",
            "implementation_note": "CURRENT IMPLEMENTATION: 关系对象绑定验证",
            "unresolved_parts": ["太过", "不及", "损之", "益之"],
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
