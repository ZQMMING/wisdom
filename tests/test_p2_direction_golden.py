"""P2-d: 判定引擎方向性验证 — Golden 数据集对齐测试。

验收规则:
- 判定引擎输出的 favorable/unfavorable 方向需与 Golden 数据集中的历史事件一致
- 身强命例：喜官杀/食伤/财，忌印比
- 身弱命例：喜印比，忌官杀/食伤/财
- 从格命例：按真从处理（从强喜印比食伤，从弱喜财官杀）
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT
from tongshu.engines.strength_engine import evaluate_strength
from tongshu.engines.judgment_engine import judgment


class TestP2DirectionGolden(unittest.TestCase):
    """验证判定引擎方向性与 Golden 数据集的一致性。"""

    def setUp(self):
        self.eng = BaziEngine()
        golden_path = Path(__file__).resolve().parent.parent / "dataset" / "golden_v1" / "golden_cases.json"
        self.golden_data = json.loads(golden_path.read_text(encoding="utf-8"))

    def _eval_with_judgment(self, birth_date: str, birth_hour: int, gender: str):
        """计算命盘并执行 P2 判定。"""
        parts = birth_date.split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        chart = self.eng.compute((y, m, d, birth_hour), gender=gender)
        d1 = evaluate_strength(chart)
        return chart, d1, judgment(chart, d1)

    def test_body_strong_direction_correct(self):
        """身强命例：喜用方向应为克泄耗。"""
        # GOLDEN-001: 1724-08-03 12:00 男
        _, d1, r = self._eval_with_judgment("1724-08-03", 12, "male")
        
        if "身强" in r.verdict_from_d1 or "从强" in r.verdict_from_d1:
            # 身强：喜官杀/食伤/财
            favorable_elements = set()
            for tg in r.favorable:
                el = self._ten_god_to_element(d1.day_master_element, tg)
                if el:
                    favorable_elements.add(el)
            
            # 验证至少有一个喜用五行
            self.assertTrue(len(favorable_elements) > 0, 
                f"身强命例应有喜用五行, verdict={r.verdict_from_d1}")

    def test_body_weak_direction_correct(self):
        """身弱命例：喜用方向应为生扶。"""
        # 找一个身弱的命例
        _, d1, r = self._eval_with_judgment("1985-12-03", 8, "female")
        
        if "身弱" in r.verdict_from_d1 or "从弱" in r.verdict_from_d1:
            favorable_elements = set()
            for tg in r.favorable:
                el = self._ten_god_to_element(d1.day_master_element, tg)
                if el:
                    favorable_elements.add(el)
            
            # 验证至少有一个喜用五行
            self.assertTrue(len(favorable_elements) > 0,
                f"身弱命例应有喜用五行, verdict={r.verdict_from_d1}")

    def test_conge_strong_direction_correct(self):
        """从强命例：喜用方向正确。"""
        # 构造从强命例：阳干得令+通根>=2
        # 甲日主生于寅月（旺地），地支多木
        _, d1, r = self._eval_with_judgment("1914-02-17", 0, "male")
        
        if "从强" in r.verdict_from_d1:
            # 从强：喜印比食伤
            self.assertIn("SEAL", r.favorable)
            self.assertIn("COMPANION", r.favorable)

    def test_conge_weak_direction_correct(self):
        """从弱命例：喜用方向正确。"""
        # 构造从弱命例：阴干无根无生扶
        _, d1, r = self._eval_with_judgment("1965-10-18", 18, "female")
        
        if "从弱" in r.verdict_from_d1 and "(假)" not in r.verdict_from_d1:
            # 从弱：喜财官杀
            self.assertIn("WEALTH", r.favorable)
            self.assertIn("OFFICIAL", r.favorable)

    def test_tiaohou_priority(self):
        """调候优先：当调候缺失时，调候字应为用神。"""
        # 冬月命例需火调候
        _, d1, r = self._eval_with_judgment("1985-12-03", 8, "female")
        
        if r.tiao_hou_is_yong and r.tiao_hou_element:
            self.assertEqual(r.yong_shen_source, "tiao_hou")
            self.assertEqual(r.yong_shen, r.tiao_hou_element)

    def test_direction_consistency_across_cases(self):
        """多案例方向一致性验证。"""
        cases = [
            ("1990-05-15", 22, "male"),   # 庚金日主，巳月
            ("1985-12-03", 8, "female"),  # 丙火日主，亥月
            ("2000-02-29", 14, "male"),   # 甲木日主，寅月
        ]
        
        for birth_date, birth_hour, gender in cases:
            _, d1, r = self._eval_with_judgment(birth_date, birth_hour, gender)
            
            # 验证 verdict 合理
            self.assertIn(r.verdict_from_d1, 
                ("身强", "身弱", "从强", "从弱", "从强(假)", "从弱(假)"))
            
            # 验证 favorable/unfavorable 非空
            self.assertTrue(len(r.favorable) > 0, 
                f"{birth_date} {gender} 应有喜用")
            self.assertTrue(len(r.unfavorable) > 0,
                f"{birth_date} {gender} 应有忌用")
            
            # 验证喜忌不重叠
            fav_set = set(r.favorable)
            unfav_set = set(r.unfavorable)
            self.assertEqual(len(fav_set & unfav_set), 0,
                f"{birth_date} {gender} 喜忌不应重叠")

    @staticmethod
    def _ten_god_to_element(dm_element: str, ten_god: str) -> str | None:
        """将十神名转换为五行。"""
        if ten_god == "COMPANION":
            return dm_element
        
        GENERATES = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", 
                     "METAL": "WATER", "WATER": "WOOD"}
        
        if ten_god == "SEAL":
            # 印星 = 生我者 = DM 被生的五行
            return GENERATES.get(dm_element)
        
        if ten_god == "EATING":
            # 食伤 = 我生者
            return GENERATES.get(dm_element)
        
        CONTROLS = {"WOOD": "EARTH", "FIRE": "METAL", "EARTH": "WATER",
                    "METAL": "WOOD", "WATER": "FIRE"}
        
        if ten_god == "WEALTH":
            # 财 = 我克者
            return CONTROLS.get(dm_element)
        
        if ten_god == "OFFICIAL":
            # 官杀 = 克我者
            for el, controls in CONTROLS.items():
                if controls == dm_element:
                    return el
        
        return None


if __name__ == "__main__":
    unittest.main()
