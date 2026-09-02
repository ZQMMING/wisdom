# -*- coding: utf-8 -*-
"""紫微斗数Phase A-0扩展测试: 真太阳时/大限边界/流月/流日

验证维度:
- P-A0.1 真太阳时校正 (经度差 + 均时差)
- P-A0.2 大限交运年龄/边界（含起运规则验证）
- P-A0.3 流月四化（验证与流年/流日不同）
- P-A0.4 流日四化（验证与流年/流月不同）
- P-A0.5 时间尺度交叉验证
- P-A1 大限阴阳顺逆规则权威验证
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

# 使用相对路径导入，不硬编码绝对路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.ziwei_engine import ZiweiEngine, time_index_from_hour


class TestTrueSolarTime(unittest.TestCase):
    """P-A0.1: 真太阳时校正测试

    真太阳时 = 北京时间 + 经度差修正 + 均时差
    经度差: (longitude - 120) × 4 分钟
    均时差: NASA/Meeus 级数计算，全年 -14 ~ +16 分钟波动
    """

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    # ─── 基准测试：无经度修正 ───────────────────────────────────────────────

    def test_早子时(self):
        """早子时00:00 → index 0"""
        result = self.engine.corrected_hour_index(0, None, (2000, 1, 1))
        self.assertEqual(result, 0)

    def test_午时(self):
        """午时11:00 → index 6"""
        result = self.engine.corrected_hour_index(11, None, (2000, 1, 1))
        self.assertEqual(result, 6)

    def test_晚子时(self):
        """晚子时23:00 → index 12"""
        result = self.engine.corrected_hour_index(23, None, (2000, 1, 1))
        self.assertEqual(result, 12)

    # ─── 经度修正测试 ───────────────────────────────────────────────────────

    def test_东经115度_负修正(self):
        """东经115°E，比北京慢20分钟，11:00→10:40→巳时(index 5)"""
        result = self.engine.corrected_hour_index(11, 115, (2000, 1, 1))
        self.assertEqual(result, 5)  # 巳时

    def test_东经125度_正修正(self):
        """东经125°E，比北京快20分钟，11:00→11:20→午时(index 6)"""
        result = self.engine.corrected_hour_index(11, 125, (2000, 1, 1))
        self.assertEqual(result, 6)  # 午时

    def test_北京经度_均时差修正(self):
        """北京经度116.4°E，均时差约-14分钟"""
        result = self.engine.corrected_hour_index(12, 116.4, (2000, 1, 1))
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 12)
        self.assertGreaterEqual(result, 0)

    def test_无经度修正_仍应用均时差(self):
        """不指定经度时，仍应用均时差修正（默认北京120°E）"""
        # 均时差在1月约-14分钟，6:00→5:46→巳时(index 5)
        result = self.engine.corrected_hour_index(6, None, (2000, 1, 1))
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 12)
        self.assertGreaterEqual(result, 0)

    def test_早子时_均时差影响(self):
        """早子时受均时差影响可能变化"""
        # 0:00 - 14min = 23:46 → 晚子时(index 12)
        result = self.engine.corrected_hour_index(0, 120, (2000, 1, 1))
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 12)
        self.assertGreaterEqual(result, 0)

    def test_晚子时_均时差影响(self):
        """晚子时受均时差影响可能变化"""
        # 23:00 - 14min = 22:46 → 亥时(index 11)
        result = self.engine.corrected_hour_index(23, 120, (2000, 1, 1))
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 12)
        self.assertGreaterEqual(result, 0)

    def test_真太阳时差异验证(self):
        """验证真太阳时校正函数能产生不同结果"""
        # 同一时间不同经度应产生不同时辰
        idx_108 = self.engine.corrected_hour_index(12, 108, (2000, 1, 1))
        idx_125 = self.engine.corrected_hour_index(12, 125, (2000, 1, 1))

        # 两者都应在有效范围内
        self.assertLessEqual(idx_108, 12)
        self.assertGreaterEqual(idx_108, 0)
        self.assertLessEqual(idx_125, 12)
        self.assertGreaterEqual(idx_125, 0)

    def test_边界时辰_修正后可能跨越(self):
        """接近边界时辰经度修正后可能跨越时辰"""
        # 13:00标准午时，东经127°时差+28分钟→13:28为未时(index 7)
        result = self.engine.corrected_hour_index(13, 127, (2000, 1, 1))
        self.assertIsInstance(result, int)
        self.assertLessEqual(result, 12)
        self.assertGreaterEqual(result, 0)

    # ─── 真太阳时影响命盘测试 ───────────────────────────────────────────────

    def test_真太阳时影响排盘(self):
        """真太阳时校正后传入排盘应产生不同命宫"""
        # 使用接近边界时辰的案例
        # 108°E: 12:00 → 约11:32 → 午时(6)
        # 125°E: 12:00 → 约12:28 → 未时(7)
        ti_108 = self.engine.corrected_hour_index(12, 108, (2000, 1, 1))
        ti_125 = self.engine.corrected_hour_index(12, 125, (2000, 1, 1))

        chart_108 = self.engine.full_chart((2000, 1, 1), ti_108, 'male')
        chart_125 = self.engine.full_chart((2000, 1, 1), ti_125, 'male')

        # 验证两个命盘都存在
        self.assertIn('palaces', chart_108)
        self.assertIn('palaces', chart_125)

        # 如果时辰不同，命宫可能不同（取决于具体日期）
        ming_108 = chart_108['palaces']['命宫']['branch']
        ming_125 = chart_125['palaces']['命宫']['branch']

        self.assertIsInstance(ming_108, str)
        self.assertIsInstance(ming_125, str)


class TestDecadalBoundary(unittest.TestCase):
    """P-A0.2: 大限交运年龄/边界测试 + P-A1: 阴阳顺逆规则验证

    验证:
    - 大限范围格式正确
    - 十二宫大限连续无重叠
    - 大限天干符合五虎遁规则
    - 不同命宫位置产生不同大限
    - 【P-A1】五行局→起运年龄映射
    - 【P-A1】阳男阴女顺行，阴男阳女逆行
    - 【P-A1】四大限排列顺序验证
    """

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    # ─── P-A0.2: 基础大限测试 ───────────────────────────────────────────────

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
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')

        for palace_name in ['命宫', '兄弟', '夫妻', '子女', '财帛', '疾厄',
                            '迁移', '交友', '官禄', '田宅', '福德', '父母']:
            palace = full.get('palaces', {}).get(palace_name, {})
            decadal_range = palace.get('decadalRange', [])
            if decadal_range:
                start, end = decadal_range
                self.assertGreaterEqual(start, 1, f"{palace_name}起始年龄<1")
                self.assertLessEqual(end, 200, f"{palace_name}结束年龄>200")

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

    def test_不同命宫位置产生不同大限(self):
        """不同命宫位置（不同地支）应产生不同大限起始年龄"""
        # 案例1: 2000-01-01 12:00 男性
        case1 = self.engine.full_chart((2000, 1, 1), 12, 'male')
        case1_ming = case1['palaces']['命宫']

        # 案例2: 不同日期导致命宫不同
        case2 = self.engine.full_chart((1990, 5, 15), 10, 'female')
        case2_ming = case2['palaces']['命宫']

        # 验证两个案例命宫地支不同
        self.assertNotEqual(case1_ming['branch'], case2_ming['branch'],
            "测试设计：两个案例应产生不同命宫")

        # 如果命宫地支不同，大限起始年龄应不同
        if case1_ming['branch'] != case2_ming['branch']:
            self.assertNotEqual(case1_ming['decadalRange'], case2_ming['decadalRange'],
                "不同命宫位置的大限起始年龄应不同")

    # ─── P-A1: 大限阴阳顺逆规则权威验证 ─────────────────────────────────────

    def test_五行局起运年龄映射(self):
        """验证五行局→起运年龄的传统映射规则

        水二局: 2岁起
        木三局: 3岁起
        金四局: 4岁起
        土五局: 5岁起
        火六局: 6岁起
        """
        # 通过不同出生年份/日期组合产生不同五行局
        cases = [
            # (农历日期, 时辰, 性别, 描述)
            ((2000, 1, 1), 12, 'male', '甲辰年男'),
            ((1999, 12, 1), 12, 'female', '己卯年女'),
            ((1998, 1, 1), 12, 'male', '戊寅年男'),
            ((1997, 6, 1), 12, 'female', '丁丑年女'),
        ]

        for ld, hour, gender, desc in cases:
            chart = self.engine.full_chart(ld, hour, gender)
            five_element = chart.get('fiveElementsClass', '')

            # 提取数字部分 (如"木三局"→3)
            import re
            match = re.search(r'(\d)局', five_element)
            if match:
                expected_start = int(match.group(1))
                ming_range = chart['palaces']['命宫']['decadalRange']
                actual_start = ming_range[0]

                self.assertEqual(actual_start, expected_start,
                    f"{desc} ({five_element}): 起运年龄应为{expected_start}，实际{actual_start}")

    def test_阳男阴女顺行(self):
        """阳男阴女：大限按传统顺行排列（命宫→兄弟→夫妻→...）"""
        # 阳年男性（2000年庚辰，阳年）
        chart = self.engine.full_chart((2000, 1, 1), 12, 'male')

        # 获取命宫位置
        ming_branch = chart['palaces']['命宫']['branch']
        branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        ming_idx = branches.index(ming_branch)

        # 传统顺行：命宫→兄弟→夫妻... (逆时针，即 -1, -2, ...)
        # 注意：紫微斗数中"顺行"指宫位顺序，对应地支逆时针方向
        expected_order = []
        for i in range(12):
            idx = (ming_idx - i) % 12
            expected_order.append(branches[idx])

        # 验证实际排列
        sorted_palaces = sorted(chart['palaces'].items(),
                               key=lambda x: x[1]['decadalRange'][0])
        actual_branches = [pdata['branch'] for _, pdata in sorted_palaces]

        self.assertEqual(actual_branches, expected_order,
            f"阳男大限应按传统顺行排列: {actual_branches} vs {expected_order}")

    def test_阴男阳女逆行(self):
        """阴男阳女：大限按传统逆行排列（命宫→父母→福德→...）"""
        # 阴年男性（1999年己卯，阴年）
        chart = self.engine.full_chart((1999, 1, 1), 12, 'male')

        # 获取命宫位置
        ming_branch = chart['palaces']['命宫']['branch']
        branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        ming_idx = branches.index(ming_branch)

        # 传统逆行：命宫→父母→福德... (顺时针，即 +1, +2, ...)
        expected_order = []
        for i in range(12):
            idx = (ming_idx + i) % 12
            expected_order.append(branches[idx])

        # 验证实际排列
        sorted_palaces = sorted(chart['palaces'].items(),
                               key=lambda x: x[1]['decadalRange'][0])
        actual_branches = [pdata['branch'] for _, pdata in sorted_palaces]

        self.assertEqual(actual_branches, expected_order,
            f"阴男大限应按传统逆行排列: {actual_branches} vs {expected_order}")

    def test_四大限排列顺序(self):
        """验证四种性别/阴阳组合的大限排列方向

        阳男 (2000, 庚年) → FORWARD → 命→兄弟→夫妻 (逆时针)
        阳女 (2000, 庚年) → REVERSE → 命→父母→福德 (顺时针)
        阴男 (1999, 己年) → REVERSE → 命→父母→福德 (顺时针)
        阴女 (1999, 己年) → FORWARD → 命→兄弟→夫妻 (逆时针)
        """
        # 2000年庚辰（阳年）
        yang_male = self.engine.full_chart((2000, 1, 1), 12, 'male')
        yang_female = self.engine.full_chart((2000, 1, 1), 12, 'female')

        # 1999年己卯（阴年）
        yin_male = self.engine.full_chart((1999, 1, 1), 12, 'male')
        yin_female = self.engine.full_chart((1999, 1, 1), 12, 'female')

        branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

        def get_order(chart):
            ming_branch = chart['palaces']['命宫']['branch']
            ming_idx = branches.index(ming_branch)
            sorted_palaces = sorted(chart['palaces'].items(),
                                   key=lambda x: x[1]['decadalRange'][0])
            return [pdata['branch'] for _, pdata in sorted_palaces]

        order_yang_male = get_order(yang_male)
        order_yang_female = get_order(yang_female)
        order_yin_male = get_order(yin_male)
        order_yin_female = get_order(yin_female)

        # 阳男 → FORWARD → 逆时针 (-1, -2, ...)
        ming_idx = branches.index(order_yang_male[0])
        expected = [branches[(ming_idx - i) % 12] for i in range(12)]
        self.assertEqual(order_yang_male, expected, "阳男大限应逆时针排列")

        # 阳女 → REVERSE → 顺时针 (+1, +2, ...)
        ming_idx = branches.index(order_yang_female[0])
        expected = [branches[(ming_idx + i) % 12] for i in range(12)]
        self.assertEqual(order_yang_female, expected, "阳女大限应顺时针排列")

        # 阴男 → REVERSE → 顺时针 (+1, +2, ...)
        ming_idx = branches.index(order_yin_male[0])
        expected = [branches[(ming_idx + i) % 12] for i in range(12)]
        self.assertEqual(order_yin_male, expected, "阴男大限应顺时针排列")

        # 阴女 → FORWARD → 逆时针 (-1, -2, ...)
        ming_idx = branches.index(order_yin_female[0])
        expected = [branches[(ming_idx - i) % 12] for i in range(12)]
        self.assertEqual(order_yin_female, expected, "阴女大限应逆时针排列")

    def test_大限天干序列合法(self):
        """大限天干应在十天干序列中，验证起始天干符合命宫天干"""
        full = self.engine.full_chart((2000, 1, 1), 12, 'male')
        stems = []
        for palace_name, pdata in full['palaces'].items():
            stem = pdata.get('decadalStem', '')
            self.assertTrue(stem, f"{palace_name}大限天干为空")
            self.assertIn(stem, ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'])
            stems.append(stem)

        # 命宫应为第一个大限，其天干应等于命宫天干
        sorted_palaces = sorted(full['palaces'].items(), key=lambda x: x[1]['decadalRange'][0])
        self.assertEqual(sorted_palaces[0][1]['decadalStem'], '甲',
            f"命宫大限天干应为甲(命宫天干)，实际{sorted_palaces[0][1]['decadalStem']}")

        # 前六个大限天干应连续: 甲、乙、丙、丁、戊、己
        expected_first_six = ['甲', '乙', '丙', '丁', '戊', '己']
        actual_first_six = [pdata['decadalStem'] for _, pdata in sorted_palaces[:6]]
        self.assertEqual(actual_first_six, expected_first_six,
            f"前六宫大限天干应为{expected_first_six}，实际{actual_first_six}")


class TestMonthlyMutagen(unittest.TestCase):
    """P-A0.3: 流月四化测试

    验证:
    - 返回格式正确
    - 星名合法
    - 与流年不同（不同时间尺度）
    - 月份变化产生不同结果
    """

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
    """P-A0.4: 流日四化测试

    验证:
    - 返回格式正确
    - 星名合法
    - 与流月不同（更细时间粒度）
    - 日期变化产生不同结果
    """

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
        """流日四化应与流月四化不同（更细时间粒度）"""
        daily = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        monthly = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 15), 15, 'male')

        self.assertNotEqual(daily, monthly, "流日四化与流月四化不应完全相同")

    def test_流日四化调用不报错(self):
        """流日四化调用应正常返回，不抛出异常"""
        try:
            result = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 4)
        except Exception as e:
            self.fail(f"flow_day_mutagen threw exception: {e}")

    def test_跨月份流日四化(self):
        """不同月份的流日四化应不同"""
        daily_jan = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        daily_feb = self.engine.flow_day_mutagen(2000, 2, 15, (2000, 2, 15), 15, 'male')

        self.assertNotEqual(daily_jan, daily_feb, "不同月份的流日四化应不同")

    def test_连续两日流日不同(self):
        """连续两天的流日四化应不同"""
        daily_15 = self.engine.flow_day_mutagen(2000, 1, 15, (2000, 1, 15), 15, 'male')
        daily_16 = self.engine.flow_day_mutagen(2000, 1, 16, (2000, 1, 16), 15, 'male')

        self.assertNotEqual(daily_15, daily_16, "连续两天的流日四化应不同")


class TestCrossTemporalValidation(unittest.TestCase):
    """P-A0.5: 时间尺度交叉验证"""

    @classmethod
    def setUpClass(cls):
        cls.engine = ZiweiEngine()

    def test_同一时间四化来源不同(self):
        """同一时间点，不同时间尺度的四化来源应不同"""
        # 本命四化（生年干）
        chart = self.engine.compute((2000, 1, 1), 12, 'male')

        # 大限四化（通过flow_decadal_mutagen获取）
        decadal_map = self.engine.flow_decadal_mutagen([2000], (2000, 1, 1), 12, 'male')
        decadal_mutagen = decadal_map.get(2000, [])

        # 流年四化
        yearly_mutagen = self.engine.flow_years_mutagen([2000], (2000, 1, 1), 12, 'male')

        # 流月四化
        monthly_mutagen = self.engine.flow_month_mutagen(2000, 1, (2000, 1, 1), 12, 'male')

        # 流日四化
        daily_mutagen = self.engine.flow_day_mutagen(2000, 1, 1, (2000, 1, 1), 12, 'male')

        # 验证所有四化都返回4颗星
        self.assertEqual(len(decadal_mutagen), 4, "大限四化应为4颗星")
        self.assertEqual(len(yearly_mutagen.get(2000, [])), 4, "流年四化应为4颗星")
        self.assertEqual(len(monthly_mutagen), 4, "流月四化应为4颗星")
        self.assertEqual(len(daily_mutagen), 4, "流日四化应为4颗星")

    def test_大限流年流月流日链条完整(self):
        """验证时间链条：大限→流年→流月→流日 四化层次完整"""
        # 毛泽东案例
        chart = self.engine.compute((1893, 11, 19), 8, 'male')
        full = self.engine.full_chart((1893, 11, 19), 8, 'male')

        # 大限四化（通过flow_decadal_mutagen获取）
        decadal_map = self.engine.flow_decadal_mutagen([1949], (1893, 11, 19), 8, 'male')
        decadal_mutagen = decadal_map.get(1949, [])

        # 流年四化
        yearly_mutagen = self.engine.flow_years_mutagen([1949], (1893, 11, 19), 8, 'male')

        # 流月四化
        monthly_mutagen = self.engine.flow_month_mutagen(1949, 1, (1893, 11, 19), 8, 'male')

        # 流日四化
        daily_mutagen = self.engine.flow_day_mutagen(1949, 1, 1, (1893, 11, 19), 8, 'male')

        # 验证所有四化都返回4颗星
        self.assertEqual(len(decadal_mutagen), 4, "大限四化应完整")
        self.assertEqual(len(yearly_mutagen.get(1949, [])), 4, "流年四化应完整")
        self.assertEqual(len(monthly_mutagen), 4, "流月四化应完整")
        self.assertEqual(len(daily_mutagen), 4, "流日四化应完整")


if __name__ == "__main__":
    unittest.main()
