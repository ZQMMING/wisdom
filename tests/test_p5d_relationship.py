"""Phase 5-D: Relationship State Engine 测试"""
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
    ENGINE_VERSION
)


class TestElementInteraction(unittest.TestCase):
    """D-1 五行互动测试。"""
    
    def _make_person(self, element: str) -> PersonModel:
        return PersonModel(
            user_id=f"user_{element}",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": element, "benming_hexagram": "乾", 
                        "yuan_tang": "坤", "postnatal_hexagram": "泰"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午",
                        "element_balance": {"金": 0.2, "木": 0.2, "水": 0.2, "火": 0.2, "土": 0.2}}
        )
    
    def test_same_element(self):
        """同类元素。"""
        result = calculate_element_interaction(self._make_person('木'), self._make_person('木'))
        self.assertEqual(result['element_relation'], '同类')
        self.assertEqual(result['interaction'], '同类增强')
    
    def test_gen_relation(self):
        """相生关系 (木生火)。"""
        result = calculate_element_interaction(self._make_person('木'), self._make_person('火'))
        self.assertEqual(result['element_relation'], '相生')
        self.assertIn('支持', result['interaction'])
    
    def test_ke_relation(self):
        """相克关系 (木克土)。"""
        result = calculate_element_interaction(self._make_person('木'), self._make_person('土'))
        self.assertEqual(result['element_relation'], '相克')
    
    def test_b_gen_a(self):
        """B生A关系。"""
        result = calculate_element_interaction(self._make_person('火'), self._make_person('木'))
        self.assertEqual(result['element_relation'], '相生')
        self.assertIn('被支持', result['interaction'])
    
    def test_b_ke_a(self):
        """B克A关系。"""
        result = calculate_element_interaction(self._make_person('土'), self._make_person('木'))
        self.assertEqual(result['element_relation'], '相克')
        self.assertIn('被制约', result['interaction'])


class TestHexagramInteraction(unittest.TestCase):
    """D-2 卦象互动测试。"""
    
    def _make_person(self, hexagram: str) -> PersonModel:
        return PersonModel(
            user_id=f"user_{hexagram}",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": "火", "benming_hexagram": hexagram, 
                        "yuan_tang": "坤", "postnatal_hexagram": "泰"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午",
                        "element_balance": {"金": 0.2, "木": 0.2, "水": 0.2, "火": 0.2, "土": 0.2}}
        )
    
    def test_same_hexagram(self):
        """同卦。"""
        result = calculate_hexagram_interaction(self._make_person('乾'), self._make_person('乾'))
        self.assertEqual(result['hexagram_relation'], '同卦')
        self.assertEqual(result['interaction_mode'], '共振')
    
    def test_compact_hexagram(self):
        """互补卦 (乾↔坤)。"""
        result = calculate_hexagram_interaction(self._make_person('乾'), self._make_person('坤'))
        self.assertEqual(result['hexagram_relation'], '互补')
        self.assertEqual(result['interaction_mode'], '调和')
    
    def test_neutral_hexagram(self):
        """中性卦。"""
        result = calculate_hexagram_interaction(self._make_person('乾'), self._make_person('屯'))
        self.assertEqual(result['hexagram_relation'], '中性')


class TestTimeSync(unittest.TestCase):
    """D-3 时间同步测试。"""
    
    def _make_person(self, liu_nian: str) -> PersonModel:
        return PersonModel(
            user_id="test_user",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": "火", "benming_hexagram": "乾"},
            daily_state={"liu_nian": liu_nian, "liu_yue": "乙巳", "liu_ri": "丙午",
                        "element_balance": {"金": 0.2, "木": 0.2, "水": 0.2, "火": 0.2, "土": 0.2}}
        )
    
    def test_sync_time(self):
        """同步时间。"""
        result = calculate_time_sync(self._make_person('甲辰'), self._make_person('甲辰'))
        self.assertEqual(result['time_sync'], '同步')
        self.assertEqual(result['current_phase'], '协同期')
    
    def test_async_time(self):
        """异步时间。"""
        result = calculate_time_sync(self._make_person('甲辰'), self._make_person('庚戌'))
        self.assertIn(result['time_sync'], ['异步', '相生'])


class TestGenerateState(unittest.TestCase):
    """D-4 统一输出测试。"""
    
    def test_output_structure(self):
        """输出结构完整性。"""
        person_a = PersonModel(
            user_id="A",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": "木", "benming_hexagram": "乾"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午"}
        )
        person_b = PersonModel(
            user_id="B",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "female"},
            heluo_model={"dominant_element": "火", "benming_hexagram": "坤"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午"}
        )
        
        input_data = RelationshipInput(
            person_a=person_a,
            person_b=person_b,
            relationship_type="partner",
            target_date=date(2026, 8, 21)
        )
        
        result = generate_relationship_state(input_data)
        
        # 核心字段检查
        self.assertIn('relationship_state', result)
        self.assertIn('interaction_pattern', result)
        self.assertIn('time_context', result)
        self.assertIn('suggestion', result)
        self.assertIn('evidence', result)
        self.assertIn('metadata', result)
        
        # 版本检查
        self.assertEqual(result['metadata']['calculation_version'], ENGINE_VERSION)
        self.assertEqual(result['metadata']['relationship_type'], 'partner')
    
    def test_strength_levels(self):
        """强度等级合理性。"""
        person_a = PersonModel(
            user_id="A",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "male"},
            heluo_model={"dominant_element": "木", "benming_hexagram": "乾"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午"}
        )
        person_b = PersonModel(
            user_id="B",
            birth_info={"year_ganzhi": "甲子", "month_ganzhi": "乙丑", 
                       "day_ganzhi": "丙寅", "hour_ganzhi": "丁卯", "gender": "female"},
            heluo_model={"dominant_element": "火", "benming_hexagram": "坤"},
            daily_state={"liu_nian": "甲辰", "liu_yue": "乙巳", "liu_ri": "丙午"}
        )
        
        input_data = RelationshipInput(
            person_a=person_a,
            person_b=person_b,
            relationship_type="friend",
            target_date=date(2026, 8, 21)
        )
        
        result = generate_relationship_state(input_data)
        strength = result['interaction_pattern']['strength']
        
        self.assertIn(strength, ['weak', 'moderate', 'strong'])


if __name__ == '__main__':
    unittest.main()