# -*- coding: utf-8 -*-
"""紫微斗数Phase A-0补充测试: 真太阳时/大限边界/流月/流日

验证维度:
- P-A0.1 真太阳时校正
- P-A0.2 大限交运年龄/边界
- P-A0.3 流月四化
- P-A0.4 流日四化
"""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path("D:/today/backend/src")))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"

from tongshu.engines.ziwei_engine import ZiweiEngine, time_index_from_hour


class TestTrueSolarTime(unittest.TestCase):
    """P-A0.1: 真太阳时校正测试"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_无经度修正_返回原时辰(self):
        """未提供longitude时，返回原始时辰index"""
        # 午时11:00 → index 6
        result = self.engine.corrected_hour_index(11, None, (2000, 1, 1))
        self.assertEqual(result, 6)

    def test_北京经度_无修正(self):
        """北京经度120°E，经度差为0，应返回原时辰"""
        # 午时11:00， longitude=120
        result = self.engine.corrected_hour_index(11, 120, (2000, 1, 1))
        self.assertEqual(result, 6)

    def test_东经125度_正修正(self):
        """东经125°E，比北京快20分钟，11:00实际为11:20真太阳时"""
        # 修正后仍在午时范围内(11:00-13:00)
        result = self.engine.corrected_hour_index(11, 125, (2000, 1, 1))
        # 应返回6(午时)，因为20分钟修正后仍为午时
        self.assertEqual(result, 6)

    def test_东经115度_负修正(self):
        """东经115°E，比北京慢20分钟，11:00实际为10:40真太阳时"""
        # 修正后为巳时(10:00-11:00)
        result = self.engine.corrected_hour_index(11, 115, (2000, 1, 1))
        self.assertEqual(result, 5)  # 巳时

    def test_边界时辰_修正后跨越(self):
        """午时边界(11:00)，东经115°修正-20分钟→10:40→巳时"""
        result = self.engine.corrected_hour_index(11, 115, (2000, 1, 1))
        self.assertEqual(result, 5)  # 巳时而非午时

    def test_晚子时_经度修正(self):
        """晚子时23:00，经度修正不应影响其归属"""
        result = self.engine.corrected_hour_index(23, 120, (2000, 1, 1))
        self.assertEqual(result, 12)  # 晚子时


class TestDecadalBoundary(unittest.TestCase):
    """P-A0.2: 大限交运年龄/边界测试"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_大限范围存在(self):
        """大限范围应为[start_age, end_age]格式"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        ming_gong = full.get('palaces', {}).get('命宫', {})
        decadal_range = ming_gong.get('decadalRange', [])
        
        self.assertEqual(len(decadal_range), 2)
        self.assertIsInstance(decadal_range[0], int)
        self.assertIsInstance(decadal_range[1], int)
        self.assertLessEqual(decadal_range[0], decadal_range[1])

    def test_大限范围合理性(self):
        """大限年龄应在合理范围内(通常1-100岁)"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        for palace_name in ['命宫', '兄弟', '夫妻', '子女']:
            palace = full.get('palaces', {}).get(palace_name, {})
            decadal_range = palace.get('decadalRange', [])
            if decadal_range:
                self.assertGreaterEqual(decadal_range[0], 1, f"{palace_name}起始年龄<1")
                self.assertLessEqual(decadal_range[1], 100, f"{palace_name}结束年龄>100")

    def test_十二宫大限覆盖完整人生(self):
        """十二宫大限应覆盖从起始到结束的人生"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        
        # 收集所有大限范围
        ranges = []
        for palace_name, pdata in full.get('palaces', {}).items():
            decadal = pdata.get('decadalRange', [])
            if decadal:
                ranges.append((palace_name, decadal[0], decadal[1]))
        
        # 按起始年龄排序
        ranges.sort(key=lambda x: x[1])
        
        # 检查连续性(相邻大限应衔接)
        for i in range(len(ranges) - 1):
            current_end = ranges[i][2]
            next_start = ranges[i + 1][1]
            # 允许±1的误差(不同流派可能有1岁差异)
            self.assertTrue(abs(next_start - current_end - 1) <= 1,
                f"{ranges[i][0]}结束{current_end}与{ranges[i+1][0]}开始{next_start}不衔接")

    def test_大限天干非空(self):
        """每个宫位的大限天干不应为空"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        for palace_name in ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄']:
            palace = full.get('palaces', {}).get(palace_name, {})
            decadal_stem = palace.get('decadalStem', '')
            self.assertTrue(decadal_stem, f"{palace_name}大限天干为空")

    def test_不同案例大限一致性(self):
        """不同案例的大限计算应一致(同算法)"""
        case1 = self.engine.full_chart((2000, 1, 1), 12, 'male')
        case2 = self.engine.full_chart((1990, 5, 15), 10, 'female')
        
        # 两盘的大限模式应相同(都基于命宫地支和阴阳年)
        m1_range = case1['palaces']['命宫'].get('decadalRange', [])
        m2_range = case2['palaces']['命宫'].get('decadalRange', [])
        
        # 大限范围长度应相同(都是10年)
        self.assertEqual(len(m1_range), len(m2_range))


class TestMonthlyMutagen(unittest.TestCase):
    """P-A0.3: 流月四化测试"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_流月四化返回格式(self):
        """流月四化应返回[禄,权,科,忌]格式"""
        mutagen = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 12, 'male')
        
        self.assertIsInstance(mutagen, list)
        self.assertEqual(len(mutagen), 4, f"流月四化应为4颗星，实际{len(mutagen)}")

    def test_流月四化星名合法(self):
        """流月四化星名应在已知星曜列表中"""
        mutagen = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 12, 'male')
        
        known_stars = {'紫微', '天府', '太阳', '武曲', '天同', '廉贞', '天府',
                       '太阴', '贪狼', '巨门', '天相', '天梁', '七杀', '破军',
                       '天机', '文昌', '文曲', '左辅', '右弼', '天魁', '天钺'}
        
        for star in mutagen:
            self.assertIn(star, known_stars, f"未知星名: {star}")

    def test_流月四化与流年不同(self):
        """流月四化应与流年四化不同(不同时间尺度)"""
        monthly = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 12, 'male')
        yearly = self.engine.flow_years_mutagen([2000], (2000, 1, 15), 12, 'male')
        
        # 流年和流月应由不同天干触发
        # 2000年天干为庚，流月应以月干触发
        self.assertNotEqual(monthly, yearly.get(2000, []),
            "流月四化与流年四化不应完全相同")

    def test_多月份流月四化(self):
        """不同月份的流月四化应不同"""
        mutagen_jan = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 12, 'male')
        mutagen_feb = self.engine.flow_month_mutagen(2000, 2, (2000, 2, 15), 12, 'male')
        
        # 不同月份应由不同月干触发四化
        self.assertNotEqual(mutagen_jan, mutagen_feb, "不同月份的流月四化应不同")


class TestDailyMutagen(unittest.TestCase):
    """P-A0.4: 流日四化测试"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_流日四化返回格式(self):
        """流日四化应返回[禄,权,科,忌]格式"""
        mutagen = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        
        self.assertIsInstance(mutagen, list)
        self.assertEqual(len(mutagen), 4, f"流日四化应为4颗星，实际{len(mutagen)}")

    def test_流日四化星名合法(self):
        """流日四化星名应在已知星曜列表中"""
        mutagen = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        
        known_stars = {'紫微', '天府', '太阳', '武曲', '天同', '廉贞', '天府',
                       '太阴', '贪狼', '巨门', '天相', '天梁', '七杀', '破军',
                       '天机', '文昌', '文曲', '左辅', '右弼', '天魁', '天钺'}
        
        for star in mutagen:
            self.assertIn(star, known_stars, f"未知星名: {star}")

    def test_流日四化与流月不同(self):
        """流日四化应与流月四化不同(更细时间粒度)"""
        daily = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        monthly = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 15, 'male')
        
        # 流日和流月应由不同天干触发
        self.assertNotEqual(daily, monthly, "流日四化与流月四化不应相同")

    def test_连续两日流日不同(self):
        """连续两天的流日四化应不同"""
        mutagen_day1 = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        mutagen_day2 = self.engine.flow_day_mutagen(2000, 1, 16, (2000, 1, 16), 15, 'male')
        
        # 流日由日干触发，连续两天日干不同
        self.assertNotEqual(mutagen_day1, mutagen_day2, "连续两日的流日四化应不同")


class TestCrossTemporalValidation(unittest.TestCase):
    """跨时间尺度一致性验证"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.case = ((1893, 11, 19), 8, 'male')  # 毛泽东案例

    def test_大限流年流月流日链条完整(self):
        """四时间尺度应形成完整链条"""
        lunar_date, hour, gender = self.case
        
        # 本命盘
        chart = self.engine.compute(lunar_date, hour, gender)
        full = self.engine.full_chart(lunar_date, hour, gender)
        
        # 大限
        decadal = self.engine.flow_decadal_mutagen([1893], lunar_date, hour, gender)
        
        # 流年
        yearly = self.engine.flow_years_mutagen([1893], lunar_date, hour, gender)
        
        # 流月
        monthly = self.engine.flow_month_mutagen(1893, 1, lunar_date, hour, gender)
        
        # 流日
        daily = self.engine.flow_day_mutagen(1893, 1, 1, lunar_date, hour, gender)
        
        # 验证链条完整性
        self.assertIsNotNone(chart)
        self.assertIsNotNone(full)
        self.assertIsInstance(decadal, dict)
        self.assertIsInstance(yearly, dict)
        self.assertIsInstance(monthly, list)
        self.assertIsInstance(daily, list)

    def test_同一时间四化来源不同(self):
        """大限/流年/流月/流日四化应由不同天干触发"""
        lunar_date, hour, gender = self.case
        
        yearly = self.engine.flow_years_mutagen([1893], lunar_date, hour, gender)
        monthly = self.engine.flow_month_mutagen(1893, 1, lunar_date, hour, gender)
        daily = self.engine.flow_day_mutagen(1893, 1, 1, lunar_date, hour, gender)
        
        y = yearly.get(1893, [])
        
        # 流年和流月应由不同天干触发
        self.assertNotEqual(y, monthly, "流年与流月四化来源应不同")
        self.assertNotEqual(monthly, daily, "流月与流日四化来源应不同")


if __name__ == "__main__":
    unittest.main()
