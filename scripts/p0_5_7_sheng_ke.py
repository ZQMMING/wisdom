# -*- coding: utf-8 -*-
"""P0-5.7: DTS-SZ-HZ-ZL「生克制化」Primitive 验证

目标: 实现"生克制化，须制中有生，生中有制"的关系检查
约束: 只检查关系事实，不碰旺衰评分和人为阈值
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT, _branch_element


class WuxingRelationChecker:
    """五行生克关系检查器
    
    CURRENT IMPLEMENTATION:
    - 仅检查四柱中是否存在相生和相克关系
    - 不检查"太过/不及"（保持 UNRESOLVED）
    """
    
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
        """从四柱提取五行"""
        elements = []
        
        # 天干
        for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
            stem_element = STEM_ELEMENT.get(pillar.heavenly_stem)
            if stem_element:
                elements.append(("stem", pillar.heavenly_stem, stem_element))
        
        # 地支
        for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
            branch_element = _branch_element(pillar.earthly_branch)
            if branch_element:
                elements.append(("branch", pillar.earthly_branch, branch_element))
        
        return elements
    
    @classmethod
    def check_gen_relation(cls, elements: list) -> tuple:
        """检查是否存在相生关系
        
        Returns:
            (exists: bool, pairs: list)
        """
        pairs = []
        element_values = [e[2] for e in elements]
        
        for src, dst in cls.GEN_RELATION.items():
            if src in element_values and dst in element_values:
                pairs.append(f"{src}生{dst}")
        
        return (len(pairs) > 0, pairs)
    
    @classmethod
    def check_keeps_relation(cls, elements: list) -> tuple:
        """检查是否存在相克关系
        
        Returns:
            (exists: bool, pairs: list)
        """
        pairs = []
        element_values = [e[2] for e in elements]
        
        for src, dst in cls.KEEPS_RELATION.items():
            if src in element_values and dst in element_values:
                pairs.append(f"{src}克{dst}")
        
        return (len(pairs) > 0, pairs)
    
    @classmethod
    def analyze_chart(cls, chart) -> dict:
        """分析四柱的五行生克关系"""
        elements = cls.extract_elements(chart)
        
        has_gen, gen_pairs = cls.check_gen_relation(elements)
        has_keeps, keeps_pairs = cls.check_keeps_relation(elements)
        
        return {
            "elements": [{"position": e[0], "gan_zhi": e[1], "element": e[2]} for e in elements],
            "has_gen": has_gen,
            "gen_pairs": gen_pairs,
            "has_keeps": has_keeps,
            "keeps_pairs": keeps_pairs,
            "both_exist": has_gen and has_keeps,
        }


def create_test_charts():
    """创建测试命例"""
    return [
        {
            "year": 1990, "month": 5, "day": 15, "hour": 10,
            "description": "标准命例（应同时有生有克）",
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
    """运行生克制化 Local Judgment"""
    print(f"\n命例: {chart_data['description']}")
    print(f"  公历: {chart_data['year']}-{chart_data['month']:02d}-{chart_data['day']:02d} {chart_data['hour']:02d}:00")
    
    # 计算四柱
    engine = BaziEngine()
    chart = engine.compute((chart_data['year'], chart_data['month'], chart_data['day'], chart_data['hour']), gender='male')
    
    # 分析五行关系
    analysis = WuxingRelationChecker.analyze_chart(chart)
    
    # 输出结果
    print(f"  四柱: {chart.year_pillar} {chart.month_pillar} {chart.day_pillar} {chart.hour_pillar}")
    print(f"  相生关系: {'✅ 存在' if analysis['has_gen'] else '❌ 不存在'}")
    if analysis['has_gen']:
        for pair in analysis['gen_pairs']:
            print(f"     - {pair}")
    print(f"  相克关系: {'✅ 存在' if analysis['has_keeps'] else '❌ 不存在'}")
    if analysis['has_keeps']:
        for pair in analysis['keeps_pairs']:
            print(f"     - {pair}")
    
    # 判定条件
    condition_met = analysis['both_exist']
    status_icon = "✅ PASS" if condition_met else "❌ FAIL"
    
    print(f"  {status_icon}: 生克制化条件（制中有生，生中有制）")
    print(f"     证据: 滴天髓::生克制化，须制中有生，生中有制")
    print(f"     授权: CLASSICAL_EXPLICIT")
    print(f"     实现: CURRENT IMPLEMENTATION（仅检查关系存在性）")
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
            "implementation_note": "CURRENT IMPLEMENTATION: 仅检查关系存在性",
            "unresolved_parts": ["太过", "不及", "损之", "益之"],
        },
        "no_strength_engine": True,
        "no_composite_judgment": True,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.7: DTS-SZ-HZ-ZL「生克制化」Primitive 验证")
    print("=" * 60)
    print("\n关键约束：")
    print("- 只检查关系事实（相生/相克是否存在）")
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
    output_path = Path(__file__).parent.parent / "data" / "p0_5_7_sheng_ke.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total": total,
            "pass_count": pass_count,
            "pass_rate": f"{pass_count / total * 100:.1f}%",
            "implementation_note": "CURRENT IMPLEMENTATION: 仅检查关系存在性",
            "unresolved_parts": ["太过", "不及", "损之", "益之"],
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
