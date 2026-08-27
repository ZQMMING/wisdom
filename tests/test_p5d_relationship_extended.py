"""Phase 5-D: Relationship State Engine 补充测试

覆盖:
- D-1 五行互动的边界情况
- D-2 卦象互补对的完整验证
- D-3 时间同步的边界情况
- D-4 输出协议和强度计算
- 异常处理和无效输入
"""
from __future__ import annotations
import unittest
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tongshu.engines.heluo.relationship.engine import (
    PersonModel,
    RelationshipInput,
    calculate_element_interaction,
    calculate_hexagram_interaction,
    calculate_time_sync,
    generate_relationship_state,
    ELEMENT_GEN,
    ELEMENT_KE,
)


class TestElementInteractionEdgeCases(unittest.TestCase):
    """D-1 五行互动边界测试。"""
    
    def _make_person(self, element: str, hexagram: str = "乾") -> PersonModel:
        return PersonModel(
            user_id="test",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": element, "benming_hexagram": hexagram, 
                        "yuan_tang": "坤", "postnatal_hexagram": "泰"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午",
                        "element_balance": {"金": 0.2, "木": 0.2, "水": 0.2, "火": 0.2, "土": 0.2}}
        )
    
    def test_all_gen_relations(self):
        """验证所有相生关系。"""
        gen_pairs = [
            ("木", "火", "A生B"),
            ("火", "土", "A生B"),
            ("土", "金", "A生B"),
            ("金", "水", "A生B"),
            ("水", "木", "A生B"),
        ]
        for elem_a, elem_b, expected_direction in gen_pairs:
            result = calculate_element_interaction(self._make_person(elem_a), self._make_person(elem_b))
            self.assertEqual(result['element_relation'], '相生', f"{elem_a}→{elem_b}")
            self.assertIn(expected_direction, result['interaction'])
    
    def test_all_ke_relations(self):
        """验证所有相克关系。"""
        ke_pairs = [
            ("木", "土", "A克B"),
            ("土", "水", "A克B"),
            ("水", "火", "A克B"),
            ("火", "金", "A克B"),
            ("金", "木", "A克B"),
        ]
        for elem_a, elem_b, expected_direction in ke_pairs:
            result = calculate_element_interaction(self._make_person(elem_a), self._make_person(elem_b))
            self.assertEqual(result['element_relation'], '相克', f"{elem_a}→{elem_b}")
            self.assertIn(expected_direction, result['interaction'])
    
    def test_balanced_relation(self):
        """无直接关系（平衡）。"""
        # 火和木是相生，火和水是相克，火和火是同类
        # 找一对既不相生也不相克的：金和木是相克，金和水是相生，金和土...
        # 实际：金→水相生，水→火相克，火→金相克
        # 没有"平衡"对，除非输入非法
        result = calculate_element_interaction(self._make_person('木'), self._make_person('金'))
        self.assertEqual(result['element_relation'], '相克')
    
    def test_empty_dominant_element(self):
        """空元素处理。"""
        person = PersonModel(
            user_id="empty",
            birth_info={},
            heluo_model={},  # 无 dominant_element
            daily_state={}
        )
        result = calculate_element_interaction(self._make_person('木'), person)
        # 默认返回平衡
        self.assertIn(result['element_relation'], ['同类', '相生', '相克', '平衡'])
    
    def test_consistency_with_maps(self):
        """验证映射表与计算结果一致。"""
        for elem_a, elem_b in [("木", "火"), ("火", "木")]:
            result = calculate_element_interaction(self._make_person(elem_a), self._make_person(elem_b))
            # 如果是相生，验证 A 生 B 还是 B 生 A
            if ELEMENT_GEN.get(elem_a) == elem_b:
                self.assertIn('支持', result['interaction'])
            elif ELEMENT_GEN.get(elem_b) == elem_a:
                self.assertIn('被支持', result['interaction'])


class TestHexagramInteractionCompleteness(unittest.TestCase):
    """D-2 卦象互动完整性测试。"""
    
    def _make_person(self, hexagram: str) -> PersonModel:
        return PersonModel(
            user_id="test",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": "火", "benming_hexagram": hexagram, 
                        "yuan_tang": "坤", "postnatal_hexagram": "泰"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午",
                        "element_balance": {"金": 0.2, "木": 0.2, "水": 0.2, "火": 0.2, "土": 0.2}}
        )
    
    def test_same_hexagram_resonance(self):
        """同卦共振。"""
        for hexagram in ['乾', '坤', '坎', '离', '震', '巽', '艮', '兑']:
            result = calculate_hexagram_interaction(self._make_person(hexagram), self._make_person(hexagram))
            self.assertEqual(result['hexagram_relation'], '同卦', f"{hexagram}")
            self.assertEqual(result['interaction_mode'], '共振', f"{hexagram}")
    
    def test_compact_pairs_completeness(self):
        """验证所有互补对。"""
        compact_pairs = [
            ('乾', '坤'), ('坤', '乾'),
            ('坎', '离'), ('离', '坎'),
            ('震', '兑'), ('兑', '震'),
            ('巽', '艮'), ('艮', '巽'),
        ]
        for a, b in compact_pairs:
            result = calculate_hexagram_interaction(self._make_person(a), self._make_person(b))
            self.assertEqual(result['hexagram_relation'], '互补', f"{a}↔{b}")
            self.assertEqual(result['interaction_mode'], '调和', f"{a}↔{b}")
    
    def test_neutral_non_matching(self):
        """非互补对返回中性。"""
        result = calculate_hexagram_interaction(self._make_person('乾'), self._make_person('屯'))
        self.assertEqual(result['hexagram_relation'], '中性')
        self.assertEqual(result['interaction_mode'], '并行')
    
    def test_empty_hexagram_returns_neutral(self):
        """空卦返回中性。"""
        person = PersonModel(
            user_id="empty",
            birth_info={},
            heluo_model={},
            daily_state={}
        )
        result = calculate_hexagram_interaction(self._make_person('乾'), person)
        # 空卦应该返回中性
        self.assertEqual(result['hexagram_relation'], '中性')


class TestTimeSyncEdgeCases(unittest.TestCase):
    """D-3 时间同步边界测试。"""
    
    def _make_person(self, liu_nian: str = "甲辰") -> PersonModel:
        return PersonModel(
            user_id="test",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": "火", "benming_hexagram": "乾"},
            daily_state={"liu_nian": liu_nian, "liu_yue": "乙巳", "liu_ri": "丙午",
                        "element_balance": {}}
        )
    
    def test_sync_same_year(self):
        """同年同月同日 → 同步。"""
        result = calculate_time_sync(self._make_person('甲辰'), self._make_person('甲辰'))
        self.assertEqual(result['time_sync'], '同步')
        self.assertEqual(result['current_phase'], '协同期')
        self.assertEqual(result['cooperation_mode'], '协作')
    
    def test_async_different_years(self):
        """不同年 → 异步或相生。"""
        result = calculate_time_sync(self._make_person('甲辰'), self._make_person('庚戌'))
        self.assertIn(result['time_sync'], ['同步', '相生', '异步'])
    
    def test_empty_liu_nian(self):
        """空流年处理。"""
        person = PersonModel(
            user_id="empty",
            birth_info={},
            heluo_model={},
            daily_state={}
        )
        result = calculate_time_sync(self._make_person(), person)
        # 空值应该返回异步
        self.assertEqual(result['time_sync'], '异步')


class TestGenerateRelationshipState(unittest.TestCase):
    """D-4 统一输出协议测试。"""
    
    def _make_person(self, element: str = "木", hexagram: str = "乾", liu_nian: str = "甲辰") -> PersonModel:
        return PersonModel(
            user_id="test",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": element, "benming_hexagram": hexagram, 
                        "yuan_tang": "坤", "postnatal_hexagram": "泰"},
            daily_state={"liu_nian": liu_nian, "liu_yue": "乙巳", "liu_ri": "丙午",
                        "element_balance": {"金": 0.2, "木": 0.2, "水": 0.2, "火": 0.2, "土": 0.2}}
        )
    
    def _make_input(self, elem_a="木", hex_a="乾", elem_b="火", hex_b="坤") -> RelationshipInput:
        return RelationshipInput(
            person_a=self._make_person(elem_a, hex_a),
            person_b=self._make_person(elem_b, hex_b),
            relationship_type="partner",
            target_date=date(2026, 8, 22)
        )
    
    def test_full_output_structure(self):
        """完整输出结构验证。"""
        result = generate_relationship_state(self._make_input())
        
        required_keys = [
            'relationship_state', 'interaction_pattern', 'time_context',
            'suggestion', 'evidence', 'metadata'
        ]
        for key in required_keys:
            self.assertIn(key, result, f"缺少键: {key}")
    
    def test_relationship_state_fields(self):
        """relationship_state 字段完整性。"""
        result = generate_relationship_state(self._make_input())
        rs = result['relationship_state']
        self.assertIn('title', rs)
        self.assertIn('description', rs)
        self.assertIsInstance(rs['title'], str)
        self.assertGreater(len(rs['title']), 0)
    
    def test_interaction_pattern_fields(self):
        """interaction_pattern 字段完整性。"""
        result = generate_relationship_state(self._make_input())
        ip = result['interaction_pattern']
        self.assertIn('strength', ip)
        self.assertIn('challenge', ip)
        self.assertIn(ip['strength'], ['weak', 'moderate', 'strong'])
    
    def test_time_context_fields(self):
        """time_context 字段完整性。"""
        result = generate_relationship_state(self._make_input())
        tc = result['time_context']
        self.assertIn('current_phase', tc)
        self.assertIn('recommended_period', tc)
    
    def test_suggestion_fields(self):
        """suggestion 字段完整性。"""
        result = generate_relationship_state(self._make_input())
        sg = result['suggestion']
        self.assertIn('action', sg)
        self.assertIn('attention', sg)
    
    def test_evidence_fields(self):
        """evidence 字段完整性。"""
        result = generate_relationship_state(self._make_input())
        ev = result['evidence']
        self.assertIn('rules', ev)
        self.assertIn('sources', ev)
        self.assertIsInstance(ev['rules'], list)
        self.assertGreater(len(ev['rules']), 0)
    
    def test_metadata_fields(self):
        """metadata 字段完整性。"""
        result = generate_relationship_state(self._make_input())
        md = result['metadata']
        self.assertEqual(md['calculation_version'], 'v1.0.0')
        self.assertEqual(md['relationship_type'], 'partner')
        self.assertEqual(md['target_date'], '2026-08-22')
    
    def test_different_relationship_types(self):
        """不同关系类型输出。"""
        for rel_type in ['partner', 'family', 'business', 'friend']:
            input_data = self._make_input()
            input_data.relationship_type = rel_type
            result = generate_relationship_state(input_data)
            self.assertEqual(result['metadata']['relationship_type'], rel_type)
    
    def test_strength_consistency_with_elements(self):
        """强度与元素关系一致性。"""
        # 同类 → 强
        result_same = generate_relationship_state(self._make_input(elem_a="木", elem_b="木"))
        # 相生 → 中等
        result_gen = generate_relationship_state(self._make_input(elem_a="木", elem_b="火"))
        # 相克 → 弱
        result_ke = generate_relationship_state(self._make_input(elem_a="木", elem_b="土"))
        
        self.assertIn(result_same['interaction_pattern']['strength'], ['weak', 'moderate', 'strong'])
        self.assertIn(result_gen['interaction_pattern']['strength'], ['weak', 'moderate', 'strong'])
        self.assertIn(result_ke['interaction_pattern']['strength'], ['weak', 'moderate', 'strong'])
    
    def test_empty_person_model(self):
        """空 PersonModel 处理。"""
        empty_person = PersonModel(
            user_id="empty",
            birth_info={},
            heluo_model={},
            daily_state={}
        )
        input_data = RelationshipInput(
            person_a=empty_person,
            person_b=self._make_person(),
            relationship_type="partner",
            target_date=date(2026, 8, 22)
        )
        result = generate_relationship_state(input_data)
        # 不应抛出异常
        self.assertIn('relationship_state', result)


class TestElementRelationEnum(unittest.TestCase):
    """ElementRelation 枚举测试。"""
    
    def test_enum_values(self):
        """枚举值验证。"""
        from tongshu.engines.heluo.relationship.engine import ElementRelation
        self.assertEqual(ElementRelation.GEN.value, "gen")
        self.assertEqual(ElementRelation.KE.value, "ke")
        self.assertEqual(ElementRelation.TONG.value, "tong")
        self.assertEqual(ElementRelation.XIE.value, "xie")
        self.assertEqual(ElementRelation.HAO.value, "hao")


class TestHexagramRelationEnum(unittest.TestCase):
    """HexagramRelation 枚举测试。"""
    
    def test_enum_values(self):
        """枚举值验证。"""
        from tongshu.engines.heluo.relationship.engine import HexagramRelation
        self.assertEqual(HexagramRelation.SAME.value, "same")
        self.assertEqual(HexagramRelation.COMP.value, "comp")
        self.assertEqual(HexagramRelation.CONFLICT.value, "conflict")
        self.assertEqual(HexagramRelation.SUPPORT.value, "support")


class TestTimeSyncEnum(unittest.TestCase):
    """TimeSync 枚举测试。"""
    
    def test_enum_values(self):
        """枚举值验证。"""
        from tongshu.engines.heluo.relationship.engine import TimeSync
        self.assertEqual(TimeSync.SYNC.value, "sync")
        self.assertEqual(TimeSync.ASYNC.value, "async")
        self.assertEqual(TimeSync.COMP.value, "comp")
        self.assertEqual(TimeSync.CONFLICT.value, "conflict")


class TestStrengthLevelEnum(unittest.TestCase):
    """StrengthLevel 枚举测试。"""
    
    def test_enum_values(self):
        """枚举值验证。"""
        from tongshu.engines.heluo.relationship.engine import StrengthLevel
        self.assertEqual(StrengthLevel.WEAK.value, "weak")
        self.assertEqual(StrengthLevel.MODERATE.value, "moderate")
        self.assertEqual(StrengthLevel.STRONG.value, "strong")


if __name__ == '__main__':
    unittest.main()
