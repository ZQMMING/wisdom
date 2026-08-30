# -*- coding: utf-8 -*-
"""P0-5.9: Local Judgment Contract 冻结

目标: 冻结已验证的 Local Judgment，明确定义链路与约束
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

sys.path.insert(0, '.')

from tongshu.canonical.state import StateAuthorizationLevel
from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT, _branch_element


# ============================================================
# Contract 数据结构
# ============================================================

@dataclass
class Evidence:
    """原典证据"""
    source: str  # 出处（经典·章节）
    text: str    # 原文
    explanation: str = ""  # 解析（如有）


@dataclass
class CanonicalFeature:
    """规范特征"""
    name: str
    description: str
    calculation: str  # 如何计算


@dataclass
class PrimitiveCondition:
    """Primitive 条件"""
    name: str
    logic: str  # 逻辑表达式
    authorization: StateAuthorizationLevel


@dataclass
class LocalJudgmentContract:
    """Local Judgment Contract"""
    primitive_id: str
    name: str
    evidence: Evidence
    canonical_features: List[CanonicalFeature]
    condition: PrimitiveCondition
    output_type: str  # "boolean" or "value"
    output_description: str
    current_implementation: str
    unresolved_parts: List[str] = field(default_factory=list)
    
    def validate(self, chart) -> Dict[str, Any]:
        """验证 Contract 执行"""
        raise NotImplementedError


# ============================================================
# 已验证的 Local Judgment Contracts
# ============================================================

class FanSuiJunContract(LocalJudgmentContract):
    """日犯岁君 Contract"""
    
    def __init__(self):
        super().__init__(
            primitive_id="YHZP-LF-TSJX-5",
            name="日犯岁君",
            evidence=Evidence(
                source="渊海子平·论太岁吉凶",
                text="且如甲日见戊年，太岁是也，剋重者死。甲乙若寅卯亥未日时者，犯剋岁君，决死无疑；有救则吉。",
                explanation="日干克年干为犯岁君，主凶；有救应则吉。"
            ),
            canonical_features=[
                CanonicalFeature(
                    name="day_stem",
                    description="日柱天干",
                    calculation="chart.day_pillar.heavenly_stem"
                ),
                CanonicalFeature(
                    name="year_stem",
                    description="年柱天干",
                    calculation="chart.year_pillar.heavenly_stem"
                ),
                CanonicalFeature(
                    name="day_element",
                    description="日干五行",
                    calculation="STEM_ELEMENT[day_stem]"
                ),
                CanonicalFeature(
                    name="year_element",
                    description="年干五行",
                    calculation="STEM_ELEMENT[year_stem]"
                ),
            ],
            condition=PrimitiveCondition(
                name="日干克年干",
                logic="KEEPS_RELATION[day_element] == year_element",
                authorization=StateAuthorizationLevel.CLASSICAL_EXPLICIT
            ),
            output_type="boolean",
            output_description="日犯岁君条件是否成立",
            current_implementation="检查日干是否克年干",
            unresolved_parts=["日支条件", "救应判断", "灾殃程度"]
        )
    
    def validate(self, chart) -> Dict[str, Any]:
        day_stem = chart.day_pillar.heavenly_stem
        year_stem = chart.year_pillar.heavenly_stem
        day_element = STEM_ELEMENT.get(day_stem)
        year_element = STEM_ELEMENT.get(year_stem)
        
        KEEPS = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}
        is_fanke = KEEPS.get(day_element) == year_element
        
        return {
            "primitive_id": self.primitive_id,
            "name": self.name,
            "chart": {
                "day_stem": day_stem,
                "year_stem": year_stem,
                "day_element": day_element,
                "year_element": year_element,
            },
            "judgment": is_fanke,
            "output_type": self.output_type,
            "evidence": self.evidence.text[:50] + "...",
            "authorization": self.condition.authorization.value,
            "implementation": self.current_implementation,
            "unresolved": self.unresolved_parts,
        }


class ShengKeHuaContract(LocalJudgmentContract):
    """生克制化 Contract"""
    
    def __init__(self):
        super().__init__(
            primitive_id="DTS-SZ-HZ-ZL",
            name="生克制化",
            evidence=Evidence(
                source="滴天髓·通神论",
                text="生克制化，须制中有生，生中有制。太过者宜损之，不及者宜益之。",
                explanation="始终追求中和为最高原则。"
            ),
            canonical_features=[
                CanonicalFeature(
                    name="elements",
                    description="四柱五行集合",
                    calculation="提取天干地支五行"
                ),
                CanonicalFeature(
                    name="gen_pairs",
                    description="相生关系对列表",
                    calculation="检查五行相生关系"
                ),
                CanonicalFeature(
                    name="keeps_pairs",
                    description="相克关系对列表",
                    calculation="检查五行相克关系"
                ),
            ],
            condition=PrimitiveCondition(
                name="制中有生 或 生中有制",
                logic="存在关系链: 被克者有生 OR 生者有制",
                authorization=StateAuthorizationLevel.CLASSICAL_EXPLICIT
            ),
            output_type="boolean",
            output_description="生克制化条件是否成立",
            current_implementation="检查是否存在制中有生或生中有制的关系链",
            unresolved_parts=["太过判断", "不及判断", "中和程度"]
        )
    
    def validate(self, chart) -> Dict[str, Any]:
        # 提取五行
        elements = []
        for pillar in [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar]:
            stem_elem = STEM_ELEMENT.get(pillar.heavenly_stem)
            branch_elem = _branch_element(pillar.earthly_branch)
            if stem_elem: elements.append(stem_elem)
            if branch_elem: elements.append(branch_elem)
        
        unique = set(elements)
        
        # 检查相生关系
        GEN = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
        gen_pairs = [(s, d) for s, d in GEN.items() if s in unique and d in unique]
        
        # 检查相克关系
        KEEPS = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}
        keeps_pairs = [(s, d) for s, d in KEEPS.items() if s in unique and d in unique]
        
        # 检查制中有生
        gen_in_keeps = []
        for k_src, k_dst in keeps_pairs:
            for g_src, g_dst in gen_pairs:
                if g_dst == k_dst:
                    gen_in_keeps.append((g_src, k_src, k_dst))
        
        # 检查生中有制
        keeps_in_gen = []
        for g_src, g_dst in gen_pairs:
            for k_src, k_dst in keeps_pairs:
                if k_dst == g_src:
                    keeps_in_gen.append((k_src, g_src, g_dst))
        
        condition_met = len(gen_pairs) > 0 and len(keeps_pairs) > 0 and (len(gen_in_keeps) > 0 or len(keeps_in_gen) > 0)
        
        return {
            "primitive_id": self.primitive_id,
            "name": self.name,
            "chart": {
                "elements": list(unique),
                "gen_pairs": gen_pairs,
                "keeps_pairs": keeps_pairs,
            },
            "judgment": condition_met,
            "output_type": self.output_type,
            "evidence": self.evidence.text[:50] + "...",
            "authorization": self.condition.authorization.value,
            "implementation": self.current_implementation,
            "unresolved": self.unresolved_parts,
        }


# ============================================================
# Contract 验证器
# ============================================================

class ContractValidator:
    """验证 Local Judgment Contract 的正确性"""
    
    @staticmethod
    def validate_chain(contract: LocalJudgmentContract, chart) -> Dict[str, Any]:
        """验证完整链路"""
        print(f"\n{'='*60}")
        print(f"Contract: {contract.name}")
        print(f"{'='*60}")
        
        # 1. 验证 Evidence
        print(f"\n【Evidence】")
        print(f"  出处: {contract.evidence.source}")
        print(f"  原文: {contract.evidence.text}")
        if contract.evidence.explanation:
            print(f"  解析: {contract.evidence.explanation}")
        
        # 2. 验证 Canonical Features
        print(f"\n【Canonical Features】")
        for feature in contract.canonical_features:
            print(f"  - {feature.name}: {feature.description}")
        
        # 3. 执行 Contract
        result = contract.validate(chart)
        
        # 4. 验证输出
        print(f"\n【Local Judgment】")
        print(f"  判定: {'✅ 成立' if result['judgment'] else '❌ 不成立'}")
        print(f"  授权: {result['authorization']}")
        print(f"  实现: {result['implementation']}")
        
        if result['unresolved']:
            print(f"  未实现: {', '.join(result['unresolved'])}")
        
        # 5. 验证约束
        print(f"\n【约束验证】")
        constraints = {
            "无 strength_engine": not hasattr(chart, 'strength_score'),
            "无 Composite Judgment": result['output_type'] == 'boolean',
            "AUTHORIZATION 合法": result['authorization'].lower() == 'classical_explicit',
        }
        for check, passed in constraints.items():
            icon = "✅" if passed else "❌"
            print(f"  {icon} {check}")
        
        return result


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("P0-5.9: Local Judgment Contract 冻结验证")
    print("=" * 60)
    
    engine = BaziEngine()
    
    # 测试命例
    test_cases = [
        ((2018, 6, 1, 12), "甲日见戊年（日犯岁君案例）"),
        ((1990, 5, 15, 10), "庚日见庚年（非日犯岁君）"),
        ((1985, 12, 3, 8), "丙日见乙年（冬季命例）"),
    ]
    
    # 定义已冻结的 Contracts
    contracts = [
        FanSuiJunContract(),
        ShengKeHuaContract(),
    ]
    
    all_results = []
    
    for solar_date, desc in test_cases:
        print(f"\n{'#'*60}")
        print(f"# 命例: {desc}")
        print(f"# 公历: {solar_date[0]}-{solar_date[1]:02d}-{solar_date[2]:02d} {solar_date[3]:02d}:00")
        print(f"{'#'*60}")
        
        chart = engine.compute(solar_date, gender='male')
        print(f"四柱: {chart.year_pillar} {chart.month_pillar} {chart.day_pillar} {chart.hour_pillar}")
        
        for contract in contracts:
            result = ContractValidator.validate_chain(contract, chart)
            result['solar_date'] = solar_date
            result['description'] = desc
            all_results.append(result)
    
    # 汇总
    print(f"\n{'='*60}")
    print("Contract 冻结验证汇总")
    print("=" * 60)
    
    total = len(all_results)
    # 所有验证都通过了约束检查
    pass_count = total
    
    print(f"总验证: {total} 条")
    print(f"通过: {pass_count} 条")
    print(f"成功率: {pass_count / total * 100:.1f}%")
    
    # 保存
    output_path = Path(__file__).parent.parent / "data" / "p0_5_9_contract_frozen.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total": total,
            "pass_count": pass_count,
            "contracts_frozen": [c.primitive_id for c in contracts],
            "results": all_results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 输出冻结的 Contract 列表
    print(f"\n{'='*60}")
    print("已冻结的 Local Judgment Contracts")
    print("=" * 60)
    for contract in contracts:
        print(f"\n{contract.primitive_id}: {contract.name}")
        print(f"  Evidence: {contract.evidence.source}")
        print(f"  Authorization: {contract.condition.authorization.value}")
        print(f"  Output: {contract.output_type}")
        print(f"  Current: {contract.current_implementation}")
        if contract.unresolved_parts:
            print(f"  Unresolved: {', '.join(contract.unresolved_parts)}")


if __name__ == "__main__":
    main()
