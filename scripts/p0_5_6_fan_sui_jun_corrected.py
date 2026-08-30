# -*- coding: utf-8 -*-
"""P0-5.6: 日犯岁君 Local Judgment Replay（修正版）

目标：
- 使用正确的测试用例（日干确实克年干）
- 明确标注 CURRENT IMPLEMENTATION
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '.')

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT


class CanonicalYearState:
    """岁君的 Canonical 表示"""
    
    def __init__(self, year_stem: str, year_branch: str):
        self.year_stem = year_stem
        self.year_branch = year_branch
        self.year_element = STEM_ELEMENT.get(year_stem, "UNKNOWN")
        self.canonical_name = "岁君"
    
    def to_dict(self):
        return {
            "canonical_name": self.canonical_name,
            "year_stem": self.year_stem,
            "year_branch": self.year_branch,
            "year_element": self.year_element,
        }


class DayMasterVsYearRelation:
    DAY_KEEPS_YEAR = "day_keeps_year"
    YEAR_KEEPS_DAY = "year_keeps_day"
    DAY_GENERATES_YEAR = "day_generates_year"
    YEAR_GENERATES_DAY = "year_generates_day"
    SAME_ELEMENT = "same_element"
    UNKNOWN = "unknown"


class DayMasterVsYearChecker:
    KEEPS_RELATION = {
        "WOOD": "EARTH",
        "EARTH": "WATER",
        "WATER": "FIRE",
        "FIRE": "METAL",
        "METAL": "WOOD",
    }
    
    @classmethod
    def check_relation(cls, day_stem: str, year_state: CanonicalYearState):
        day_element = STEM_ELEMENT.get(day_stem, "UNKNOWN")
        year_element = year_state.year_element
        
        if day_element == "UNKNOWN" or year_element == "UNKNOWN":
            return DayMasterVsYearRelation.UNKNOWN
        
        if cls.KEEPS_RELATION.get(day_element) == year_element:
            return DayMasterVsYearRelation.DAY_KEEPS_YEAR
        if cls.KEEPS_RELATION.get(year_element) == day_element:
            return DayMasterVsYearRelation.YEAR_KEEPS_DAY
        if day_element == year_element:
            return DayMasterVsYearRelation.SAME_ELEMENT
        if cls.KEEPS_RELATION.get(day_element) == year_element:
            return DayMasterVsYearRelation.DAY_GENERATES_YEAR
        
        return DayMasterVsYearRelation.UNKNOWN
    
    @classmethod
    def is_fan_sui_jun(cls, relation: str) -> bool:
        return relation == DayMasterVsYearRelation.DAY_KEEPS_YEAR


def test_known_case():
    """使用已知的日犯岁君案例测试
    
    渊海子平例子：甲日见戊年（甲木克戊土）
    
    我们需要找一个公历日期，使得：
    - 年干 = 戊（戊土）
    - 日干 = 甲（甲木）
    
    戊年：1958, 2018, ...
    让我们验证这些年份的日干
    """
    print("=" * 60)
    print("P0-5.6: 寻找甲日见戊年的公历日期")
    print("=" * 60)
    
    # 戊年列表
    wu_years = [1958, 2018, 2078]
    
    for year in wu_years:
        # 尝试几个日期，找到甲日
        for month in [1, 6, 12]:
            for day in [1, 15]:
                engine = BaziEngine()
                chart = engine.compute((year, month, day, 12), gender='male')
                
                day_stem = chart.day_pillar.heavenly_stem
                year_stem = chart.year_pillar.heavenly_stem
                
                if day_stem == "JIA" and year_stem == "WU":
                    print(f"\n✅ 找到: {year}-{month:02d}-{day:02d}")
                    print(f"   年柱: {chart.year_pillar}")
                    print(f"   日柱: {chart.day_pillar}")
                    print(f"   日干={day_stem}（甲木），年干={year_stem}（戊土）")
                    print(f"   甲木克戊土 → 犯岁君 ✅")
                    return (year, month, day, 12)
    
    print("\n❌ 未找到甲日见戊年的日期")
    return None


def run_test_with_correct_case(solar_date):
    """运行正确的测试用例"""
    year, month, day, hour = solar_date
    
    print(f"\n{'='*60}")
    print(f"命例: 甲日见戊年（日干甲木克年干戊土）")
    print(f"公历: {year}-{month:02d}-{day:02d} {hour}:00")
    
    engine = BaziEngine()
    chart = engine.compute(solar_date, gender='male')
    
    day_stem = chart.day_pillar.heavenly_stem
    year_stem = chart.year_pillar.heavenly_stem
    
    print(f"  日干: {day_stem}, 年干: {year_stem}")
    
    year_state = CanonicalYearState(
        year_stem=year_stem,
        year_branch=chart.year_pillar.earthly_branch,
    )
    
    relation = DayMasterVsYearChecker.check_relation(day_stem, year_state)
    is_fan_sui_jun = DayMasterVsYearChecker.is_fan_sui_jun(relation)
    
    status_icon = "✅ 犯岁君" if is_fan_sui_jun else "❌ 不犯岁君"
    print(f"  {status_icon}: 日犯岁君条件")
    print(f"     证据: 渊海子平::日犯岁君，灾殃必重")
    print(f"     关系: {relation}")
    print(f"     授权: CLASSICAL_EXPLICIT")
    print(f"     实现: CURRENT IMPLEMENTATION（仅检查日干克年干）")
    
    return {
        "description": "甲日见戊年（日干甲木克年干戊土）",
        "solar_date": solar_date,
        "four_pillars": {
            "year": str(chart.year_pillar),
            "month": str(chart.month_pillar),
            "day": str(chart.day_pillar),
            "hour": str(chart.hour_pillar),
        },
        "day_stem": day_stem,
        "year_state": year_state.to_dict(),
        "relation": relation,
        "judgment": {
            "primitive": "日犯岁君",
            "condition_met": is_fan_sui_jun,
            "status": "PASS" if is_fan_sui_jun else "FAIL",
            "evidence": "渊海子平::日犯岁君，灾殃必重；五行有救，其年反必招财",
            "authorization": StateAuthorizationLevel.CLASSICAL_EXPLICIT.value,
            "layer": "生产层",
            "implementation_note": "CURRENT IMPLEMENTATION: 仅检查日干克年干",
            "missing_relations": ["日支克年支", "运克岁君", "岁运冲刑", "日支冲年支"],
        },
        "no_strength_engine": True,
        "no_composite_judgment": True,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.6: 日犯岁君 Local Judgment Replay（修正版）")
    print("=" * 60)
    
    # Step 1: 找到正确的测试用例
    solar_date = test_known_case()
    
    if solar_date:
        # Step 2: 运行验证
        result = run_test_with_correct_case(solar_date)
        
        # 汇总
        print("\n" + "=" * 60)
        print("验证结果")
        print("=" * 60)
        print(f"总测试: 1 条命例")
        print(f"犯岁君: {'✅ PASS' if result['judgment']['condition_met'] else '❌ FAIL'}")
        
        # 保存
        output_path = Path(__file__).parent.parent / "data" / "p0_5_6_fan_sui_jun_corrected.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "total": 1,
                "pass_count": 1 if result['judgment']['condition_met'] else 0,
                "implementation_note": "CURRENT IMPLEMENTATION: 仅检查日干克年干",
                "missing_relations": ["日支克年支", "运克岁君", "岁运冲刑", "日支冲年支"],
                "result": result,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到 {output_path}")
    else:
        print("\n❌ 无法找到正确的测试用例")
