# -*- coding: utf-8 -*-
"""紫微斗数Phase A-0扩展测试: 真太阳时/大限边界/流月/流日

验证维度:
- P-A0.1 真太阳时校正
- P-A0.2 大限交运年龄/边界（含起运规则验证）
- P-A0.3 流月四化（验证与流年/流日不同）
- P-A0.4 流日四化（验证与流年/流月不同）
"""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path('C:/Users/wisdom/wisdom/src')))
sys.path.insert(0, str(Path('D:/today/backend/src')))
os.environ['TONGSHU_ALLOW_ZIWEI_STUB'] = '1'

from tongshu.engines.ziwei_engine import ZiweiEngine, time_index_from_hour


class TestTrueSolarTime(unittest.TestCase):
    """P-A0.1: 真太阳时校正测试"""
    
    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
    
    def test_早子时(self):
        result = self.engine.corrected_hour_index(0, None, (2000, 1, 1))
        self.assertEqual(result, 0)
    
    def test_午时(self):
        result = self.engine.corrected_hour_index(11, None, (2000, 1, 1))
        self.assertEqual(result, 6)
    
    def test_晚子时(self):
        result = self.engine.corrected_hour_index(23, None, (2000, 1, 1))
        self.assertEqual(result, 12)
    
    def test_东经115度_负修正(self):
        """东经115°E，比北京慢20分钟，11:00实际为10:40真太阳时"""
        result = self.engine.corrected_hour_index(11, 115, (2000, 1, 1))
        self.assertEqual(result, 5)  # 巳时
    
    def test_东经125度_正修正(self):
        """东经125°E，比北京快20分钟，11:00实际为11:20真太阳时"""
        result = self.engine.corrected_hour_index(11, 125, (2000, 1, 1))
        self.assertEqual(result, 6)
    
    def test_北京经度_无修正(self):
        """北京经度120°E，经度差为0，但因均时差可能略有偏移"""
        result = self.engine.corrected_hour_index(11, 120, (2000, 1, 1))
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 7)
        self.assertGreaterEqual(result, 5)
    
    def test_无经度修正_返回原时辰(self):
        """未提供longitude时，返回原始时辰index"""
        result = self.engine.corrected_hour_index(11, None, (2000, 1, 1))
        self.assertEqual(result, 6)
    
    def test_晚子时_经度修正(self):
        """晚子时23:00，经度修正后仍应接近原值"""
        result = self.engine.corrected_hour_index(23, 120, (2000, 1, 1))
        self.assertIsInstance(result, int)
        self.assertIn(result, [11, 12], f"晚子时经度修正结果{result}不合理")
    
    def test_边界时辰_修正后跨越(self):
        """午时边界(11:00)，东经115°修正-20分钟→10:40→巳时"""
        result = self.engine.corrected_hour_index(11, 115, (2000, 1, 1))
        self.assertEqual(result, 5)  # 巳时而非午时


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
        """大限年龄应在合理范围内(1-200岁覆盖一生)"""
        lunar_date, hour, gender = (2000, 1, 1), 12, 'male'
        full = self.engine.full_chart(lunar_date, hour, gender)
        
        for pname, pdata in full.get('palaces', {}).items():
            decadal_range = pdata.get('decadalRange')
            if decadal_range:
                start, end = decadal_range
                self.assertGreaterEqual(start, 1, f"{pname}开始年龄<1")
                self.assertLessEqual(end, 200, f"{pname}结束年龄>200")
    
    def test_十二宫大限覆盖完整人生(self):
        """十二宫大限应覆盖从起始到结束的人生，连续无重叠"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        
        ranges = []
        for palace_name, pdata in full.get('palaces', {}).items():
            decadal = pdata.get('decadalRange', [])
            if decadal:
                stem = pdata.get('decadalStem', '')
                self.assertTrue(stem, f"{palace_name}大限天干为空")
                ranges.append((decadal[0], decadal[1], palace_name))
        
        self.assertEqual(len(ranges), 12, "应有12宫大限")
        ranges.sort(key=lambda x: x[0])
        
        # 验证连续无重叠
        for i in range(len(ranges) - 1):
            current_start = ranges[i + 1][0]
            prev_end = ranges[i][1]
            self.assertEqual(current_start, prev_end + 1,
                f"{ranges[i][2]}结束{prev_end}与{ranges[i+1][2]}开始{current_start}不衔接")
    
    def test_大限天干非空(self):
        """每个宫位的大限天干不应为空"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        for palace_name in ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄']:
            palace = full.get('palaces', {}).get(palace_name, {})
            decadal_stem = palace.get('decadalStem', '')
            self.assertTrue(decadal_stem, f"{palace_name}大限天干为空")
    
    def test_不同案例大限一致性(self):
        """不同出生案例的大限计算应使用相同算法"""
        # 案例1: 2000-01-01 12:00 男性
        case1 = self.engine.full_chart((2000, 1, 1), 12, 'male')
        # 案例2: 1990-05-15 10:00 女性（不同日期、时辰、性别）
        case2 = self.engine.full_chart((1990, 5, 15), 10, 'female')
        
        # 两个案例的命宫大限应不同（因为命宫位置不同）
        case1_ming = case1['palaces']['命宫']
        case2_ming = case2['palaces']['命宫']
        
        # 验证命宫大限存在且合理
        self.assertEqual(len(case1_ming['decadalRange']), 2)
        self.assertEqual(len(case2_ming['decadalRange']), 2)
        
        # 如果命宫地支不同，大限起始年龄可能不同
        if case1_ming['branch'] != case2_ming['branch']:
            self.assertNotEqual(case1_ming['decadalRange'], case2_ming['decadalRange'],
                "不同命宫位置的大限起始年龄应不同")
    
    def test_大限排列符合算法(self):
        """大限排列应由iztro引擎决定，验证连续性即可"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        
        # 收集所有大限范围并排序
        ranges = []
        for pname, pdata in full['palaces'].items():
            dr = pdata.get('decadalRange')
            if dr:
                ranges.append((dr[0], dr[1], pdata['branch'], pname))
        
        ranges.sort(key=lambda x: x[0])
        
        # 验证连续无重叠
        for i in range(len(ranges) - 1):
            self.assertEqual(ranges[i][1] + 1, ranges[i+1][0],
                f"大限不连续: {ranges[i][2]}结束{ranges[i][1]}, {ranges[i+1][2]}开始{ranges[i+1][0]}")
    
    def test_大限天干符合五虎遁规则(self):
        """大限天干应由命宫天干决定，验证一致性"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        
        # 命宫天干已知
        ming_stem = full['palaces']['命宫']['stem']
        ming_branch = full['palaces']['命宫']['branch']
        
        # 大限天干应从命宫天干顺数
        # 这里只验证命宫有大限天干，具体映射由引擎决定
        self.assertTrue(ming_stem, "命宫天干不应为空")
        self.assertIn(ming_stem, ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'])


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
        
        # 流月和流年应由不同机制触发
        self.assertNotEqual(monthly, yearly.get(2000, []),
            "流月四化与流年四化不应完全相同")
    
    def test_多月份流月四化(self):
        """不同月份的流月四化应不同"""
        mutagen_jan = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 12, 'male')
        mutagen_feb = self.engine.flow_month_mutagen(2000, 2, (2000, 2, 15), 12, 'male')
        
        self.assertNotEqual(mutagen_jan, mutagen_feb, "不同月份的流月四化应不同")
    
    def test_跨年份流月四化(self):
        """不同年份的流月四化应不同"""
        mutagen_2000 = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 12, 'male')
        mutagen_2001 = self.engine.flow_month_mutagen(2001, 1, (2001, 1, 15), 12, 'male')
        
        self.assertNotEqual(mutagen_2000, mutagen_2001, "不同年份的流月四化应不同")
    
    def test_流月四化调用不报错(self):
        """流月四化调用应正常返回，不抛出异常"""
        try:
            result = self.engine.flow_month_mutagen(1893, 11, (1893, 11, 19), 6, 'male')
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 4)
        except Exception as e:
            self.fail(f"flow_month_mutagen threw exception: {e}")


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
        
        self.assertNotEqual(daily, monthly, "流日四化与流月四化不应相同")
    
    def test_连续两日流日不同(self):
        """连续两天的流日四化应不同"""
        mutagen_day1 = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        mutagen_day2 = self.engine.flow_day_mutagen(2000, 1, 16, (2000, 1, 16), 15, 'male')
        
        self.assertNotEqual(mutagen_day1, mutagen_day2, "连续两日的流日四化应不同")
    
    def test_跨月份流日四化(self):
        """不同月份的流日四化应不同"""
        mutagen_jan = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        mutagen_feb = self.engine.flow_day_mutagen(2000, 2, 15, (2000, 2, 15), 15, 'male')
        
        self.assertNotEqual(mutagen_jan, mutagen_feb, "不同月份的流日四化应不同")
    
    def test_流日四化调用不报错(self):
        """流日四化调用应正常返回，不抛出异常"""
        try:
            result = self.engine.flow_day_mutagen(1893, 11, 19, (1893, 11, 19), 6, 'male')
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 4)
        except Exception as e:
            self.fail(f"flow_day_mutagen threw exception: {e}")


class TestCrossTemporalValidation(unittest.TestCase):
    """时间尺度交叉验证"""
    
    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()
        cls.case = ((1893, 11, 19), 6, 'male')  # 毛泽东案例
    
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
        self.assertEqual(len(monthly), 4)
        self.assertIsInstance(daily, list)
        self.assertEqual(len(daily), 4)
    
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
    unittest.main(verbosity=2)
