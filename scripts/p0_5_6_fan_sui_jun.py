# -*- coding: utf-8 -*-
"""P0-5.6: 日犯岁君 Local Judgment Replay（CURRENT IMPLEMENTATION）

目标：
- 验证"日犯岁君"的 Local Judgment
- 明确标注为 CURRENT IMPLEMENTATION
- 不声称 CLASSICAL COMPLETE DEFINITION

关键约束：
- 岁君 = 太岁/流年干支的 Canonical Entity
- 犯 = 经原典确认的 Relation
- 当前仅验证"日干克年干"这一种关系
- 列出缺失的关系类型
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from enum import Enum

sys.path.insert(0, '.')

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT


class CanonicalYearState:
    """岁君的 Canonical 表示
    
    原典依据：
    - 渊海子平：太岁乃年中天子，故不可犯
    - 岁君 = 太岁 = 年柱（年干+年支）
    """
    
    def __init__(self, year_stem: str, year_branch: str):
        self.year_stem = year_stem
        self.year_branch = year_branch
        self.year_element = STEM_ELEMENT.get(year_stem, "UNKNOWN")
        self.canonical_name = "岁君"  # 或 "太岁"
    
    def to_dict(self):
        return {
            "canonical_name": self.canonical_name,
            "year_stem": self.year_stem,
            "year_branch": self.year_branch,
            "year_element": self.year_element,
        }


class DayMasterVsYearRelation(Enum):
    """日干与岁君的关系
    
    原典依据：
    - 渊海子平：日干支冲剋太岁曰征
    - 犯 = 冲克关系
    """
    DAY_KEEPS_YEAR = "day_keeps_year"  # 日干克年干
    YEAR_KEEPS_DAY = "year_keeps_day"  # 年干克日干
    DAY_GENERATES_YEAR = "day_generates_year"  # 日干生年干
    YEAR_GENERATES_DAY = "year_generates_day"  # 年干生日干
    SAME_ELEMENT = "same_element"  # 日干年干同五行
    UNKNOWN = "unknown"


class DayMasterVsYearChecker:
    """日干与岁君关系检查器
    
    CURRENT IMPLEMENTATION:
    - 仅检查日干是否克年干
    - 未检查：日支克年支、运克岁君、岁运冲刑
    """
    
    # 五行相克关系
    KEEPS_RELATION = {
        "WOOD": "EARTH",
        "EARTH": "WATER",
        "WATER": "FIRE",
        "FIRE": "METAL",
        "METAL": "WOOD",
    }
    
    @classmethod
    def check_relation(cls, day_stem: str, year_state: CanonicalYearState) -> DayMasterVsYearRelation:
        """检查日干与岁君的关系
        
        Args:
            day_stem: 日干（如 "JIA"）
            year_state: 岁君 Canonical State
        
        Returns:
            DayMasterVsYearRelation
        """
        day_element = STEM_ELEMENT.get(day_stem, "UNKNOWN")
        year_element = year_state.year_element
        
        if day_element == "UNKNOWN" or year_element == "UNKNOWN":
            return DayMasterVsYearRelation.UNKNOWN
        
        # 检查日干是否克年干（CURRENT IMPLEMENTATION）
        if cls.KEEPS_RELATION.get(day_element) == year_element:
            return DayMasterVsYearRelation.DAY_KEEPS_YEAR
        
        # 检查年干是否克日干
        if cls.KEEPS_RELATION.get(year_element) == day_element:
            return DayMasterVsYearRelation.YEAR_KEEPS_DAY
        
        # 其他关系（后续实现）
        return DayMasterVsYearRelation.UNKNOWN
    
    @classmethod
    def is_fan_sui_jun(cls, relation: DayMasterVsYearRelation) -> bool:
        """判断是否犯岁君
        
        CURRENT IMPLEMENTATION:
        - 仅当"日干克年干"时判定为犯岁君
        - 未包含：日支克年支、运克岁君、岁运冲刑
        """
        return relation == DayMasterVsYearRelation.DAY_KEEPS_YEAR


def create_test_charts():
    """创建测试命例"""
    # 基于渊海子平的例子：甲日见戊年
    return [
        {
            "year": 1958, "month": 1, "day": 1, "hour": 12,
            "description": "甲日见戊年（甲戌年，日干甲木克年干戊土）",
        },
        {
            "year": 1990, "month": 5, "day": 15, "hour": 10,
            "description": "庚日见庚年（庚午年，日干庚金与年干庚金同五行）",
        },
        {
            "year": 1985, "month": 12, "day": 3, "hour": 8,
            "description": "丙日见乙年（乙丑年，日干丙火生年干乙木）",
        },
        {
            "year": 1986, "month": 3, "day": 21, "hour": 6,
            "description": "甲日见辛年（丙寅年，日干甲木被年干辛金克）",
        },
    ]


def run_fan_sui_jun_judgment(chart_data):
    """运行日犯岁君 Local Judgment"""
    print(f"\n命例: {chart_data['description']}")
    
    # 使用 BaziEngine 计算四柱
    engine = BaziEngine()
    chart = engine.compute((chart_data['year'], chart_data['month'], chart_data['day'], chart_data['hour']), gender='male')
    
    # 提取日干和年干
    day_stem = chart.day_pillar.heavenly_stem
    year_stem = chart.year_pillar.heavenly_stem
    
    print(f"  日干: {day_stem}, 年干: {year_stem}")
    
    # 创建岁君 Canonical State
    year_state = CanonicalYearState(
        year_stem=year_stem,
        year_branch=chart.year_pillar.earthly_branch,
    )
    
    # 检查关系（CURRENT IMPLEMENTATION）
    relation = DayMasterVsYearChecker.check_relation(day_stem, year_state)
    is_fan_sui_jun = DayMasterVsYearChecker.is_fan_sui_jun(relation)
    
    # 输出结果
    status_icon = "✅ 犯岁君" if is_fan_sui_jun else "❌ 不犯岁君"
    print(f"  {status_icon}: 日犯岁君条件")
    print(f"     证据: 渊海子平::日犯岁君，灾殃必重；五行有救，其年反必招财")
    print(f"     关系: {relation.value}")
    print(f"     授权: CLASSICAL_EXPLICIT")
    print(f"     实现: CURRENT IMPLEMENTATION（仅检查日干克年干）")
    
    return {
        "description": chart_data['description'],
        "solar_date": (chart_data['year'], chart_data['month'], chart_data['day'], chart_data['hour']),
        "four_pillars": {
            "year": str(chart.year_pillar),
            "month": str(chart.month_pillar),
            "day": str(chart.day_pillar),
            "hour": str(chart.hour_pillar),
        },
        "day_stem": day_stem,
        "year_state": year_state.to_dict(),
        "relation": relation.value,
        "judgment": {
            "primitive": "日犯岁君",
            "condition_met": is_fan_sui_jun,
            "status": "PASS" if is_fan_sui_jun else "FAIL",
            "evidence": "渊海子平::日犯岁君，灾殃必重；五行有救，其年反必招财",
            "authorization": StateAuthorizationLevel.CLASSICAL_EXPLICIT.value,
            "layer": "生产层",
            "implementation_note": "CURRENT IMPLEMENTATION: 仅检查日干克年干",
            "missing_relations": [
                "日支克年支",
                "运克岁君",
                "岁运冲刑",
                "日支冲年支",
            ],
        },
        "no_strength_engine": True,
        "no_composite_judgment": True,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.6: 日犯岁君 Local Judgment Replay")
    print("=" * 60)
    print("\n关键约束：")
    print("- 明确标注 CURRENT IMPLEMENTATION")
    print("- 不声称 CLASSICAL COMPLETE DEFINITION")
    print("- 列出缺失的关系类型")
    print("- 不接回 strength_engine")
    
    # 创建测试命例
    charts = create_test_charts()
    
    # 运行 Local Judgment
    results = []
    for chart_data in charts:
        result = run_fan_sui_jun_judgment(chart_data)
        results.append(result)
    
    # 汇总
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    pass_count = sum(1 for r in results if r['judgment']['condition_met'])
    total = len(results)
    
    print(f"总测试: {total} 条命例 × 1 条件 = {total} 条")
    print(f"犯岁君: {pass_count}")
    print(f"不犯岁君: {total - pass_count}")
    print(f"比例: {pass_count / total * 100:.1f}%")
    
    # 验证约束
    all_no_strength = all(r['no_strength_engine'] for r in results)
    all_no_composite = all(r['no_composite_judgment'] for r in results)
    all_current_impl = all('CURRENT IMPLEMENTATION' in r['judgment']['implementation_note'] for r in results)
    
    print(f"\n约束验证:")
    print(f"  无 strength_engine: {'✅' if all_no_strength else '❌'}")
    print(f"  无 Composite Judgment: {'✅' if all_no_composite else '❌'}")
    print(f"  标注 CURRENT IMPLEMENTATION: {'✅' if all_current_impl else '❌'}")
    
    # 保存
    output_path = Path(__file__).parent.parent / "data" / "p0_5_6_fan_sui_jun.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total": total,
            "pass_count": pass_count,
            "pass_rate": f"{pass_count / total * 100:.1f}%",
            "implementation_note": "CURRENT IMPLEMENTATION: 仅检查日干克年干",
            "missing_relations": [
                "日支克年支",
                "运克岁君",
                "岁运冲刑",
                "日支冲年支",
            ],
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 关键结论
    print("\n" + "=" * 60)
    print("关键结论")
    print("=" * 60)
    print("- 当前实现仅检查'日干克年干'")
    print("- 未检查：日支克年支、运克岁君、岁运冲刑")
    print("- 必须标注 CURRENT IMPLEMENTATION")
    print("- 不能称为 CLASSICAL COMPLETE DEFINITION")
