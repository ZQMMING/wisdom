# -*- coding: utf-8 -*-
"""紫微断事层V2.7测试: 生年四化落宫 + 主题评分"""
from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path("D:/today/backend/src")))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"

from tongshu.engines.ziwei_engine import ZiweiEngine


class TestZiweiSihuaPalace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = ZiweiEngine()

    def test_癸年四化落宫(self):
        """癸年: 破军禄 巨门权 太阴科 贪狼忌"""
        # 1893年11月19日(农历) 辰时 男 (毛泽东)
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        sihua = self.e.get_sihua_palaces(full, '癸')
        # 贪狼化忌应在命宫(申)
        self.assertEqual(sihua['hua_ji'], '命宫')
        # 破军化禄应在财帛
        self.assertEqual(sihua['hua_lu'], '财帛')
        # 巨门化权应在父母
        self.assertEqual(sihua['hua_quan'], '父母')

    def test_甲年四化落宫(self):
        """甲年: 廉贞禄 破军权 武曲科 太阳忌"""
        full = self.e.full_chart((1984, 10, 15), 16, 'female')
        sihua = self.e.get_sihua_palaces(full, '甲')
        # 太阳化忌
        self.assertIsNotNone(sihua['hua_ji'])
        # 廉贞化禄
        self.assertIsNotNone(sihua['hua_lu'])

    def test_庚年四化落宫(self):
        """庚年: 太阳禄 武曲权 太阴科 天同忌"""
        full = self.e.full_chart((1960, 5, 5), 4, 'male')
        sihua = self.e.get_sihua_palaces(full, '庚')
        self.assertIsNotNone(sihua['hua_lu'])
        self.assertIsNotNone(sihua['hua_ji'])

    def test_己年文曲化忌落宫(self):
        """己年文曲化忌(辅星)应能找到落宫(V2.7.1)"""
        # 刘坤一 1830-01-21 子时 -> 农历1829-12-27
        full = self.e.full_chart((1829, 12, 27), 0, 'male')
        sihua = self.e.get_sihua_palaces(full, '己')
        self.assertIsNotNone(sihua['hua_ji'], '文曲化忌应找到落宫(辅星)')

    def test_辛年文昌化忌落宫(self):
        """辛年文昌化忌(辅星)应能找到落宫(V2.7.1)"""
        # 鲁迅 1881-09-25 辰时 -> 农历1881-8-3
        full = self.e.full_chart((1881, 8, 3), 8, 'male')
        sihua = self.e.get_sihua_palaces(full, '辛')
        self.assertIsNotNone(sihua['hua_ji'], '文昌化忌应找到落宫(辅星)')

    def test_未知年干返回None(self):
        """未知年干返回全None"""
        full = self.e.full_chart((1960, 5, 5), 4, 'male')
        sihua = self.e.get_sihua_palaces(full, 'X')
        self.assertIsNone(sihua['hua_lu'])
        self.assertIsNone(sihua['hua_ji'])


class TestZiweiTopicScore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = ZiweiEngine()

    def test_财运化禄加分(self):
        """化禄在财帛宫, 财运主题应加分"""
        chart = self.e.compute((1893, 11, 19), 8, 'male')
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        result = self.e.score_topic(chart, full, '财运', lunar_date=(1893, 11, 19))
        self.assertGreater(result['score'], 0)
        self.assertIn('化禄', result['sihua_in_palace'])

    def test_化忌扣分(self):
        """化忌在对应宫位应扣分"""
        # 甲年太阳化忌在子女宫 (公历1984-10-15 -> 农历1984-9-21)
        chart = self.e.compute((1984, 9, 21), 16, 'female')
        full = self.e.full_chart((1984, 9, 21), 16, 'female')
        result = self.e.score_topic(chart, full, '子女', lunar_date=(1984, 9, 21))
        # 太阳化忌在子女宫, 子女主题应含化忌
        self.assertIn('化忌', result['sihua_in_palace'])
        self.assertLess(result['score'], 0)

    def test_空宫扣分(self):
        """空宫应扣分"""
        chart = self.e.compute((1893, 11, 19), 8, 'male')
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        result = self.e.score_topic(chart, full, '健康', lunar_date=(1893, 11, 19))
        # 疾厄宫空宫, 应扣分
        self.assertEqual(result['major_stars'], [])
        self.assertLess(result['score'], 0)

    def test_未知主题返回0(self):
        """未知主题返回0分"""
        chart = self.e.compute((1960, 5, 5), 4, 'male')
        full = self.e.full_chart((1960, 5, 5), 4, 'male')
        result = self.e.score_topic(chart, full, '未知主题')
        self.assertEqual(result['score'], 0)
        self.assertIsNone(result['palace'])


class TestZiweiSanfangSizheng(unittest.TestCase):
    """三方四正分析测试 V2.8"""
    @classmethod
    def setUpClass(cls):
        cls.e = ZiweiEngine()

    def test_地支对宫关系(self):
        """对宫: 地支+6(对冲)"""
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        # 夫妻宫在午, 对宫应在子(官禄)
        sfsz = self.e.get_sanfang_sizheng(full, '夫妻')
        self.assertEqual(sfsz['ben_branch'], '午')
        self.assertEqual(sfsz['dui_branch'], '子')

    def test_地支三合关系(self):
        """三合: 地支+4和+8"""
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        sfsz = self.e.get_sanfang_sizheng(full, '夫妻')
        # 午的三合: 寅(+4=寅? 午6+4=10=戌, +8=14%12=2=寅)
        self.assertEqual(set([sfsz['sanhe1_branch'], sfsz['sanhe2_branch']]),
                         {'寅', '戌'})

    def test_三方四正主星合集(self):
        """四方主星合集应包含本宫+对宫+两个三合宫的主星"""
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        sfsz = self.e.get_sanfang_sizheng(full, '财帛')
        all_major = sfsz['all_major']
        # 财帛宫(辰)主星破军, 对宫福德(戌)紫微天相, 三合命宫(申)贪狼, 官禄(子)七杀
        self.assertIn('破军', all_major)
        self.assertIn('紫微', all_major)
        self.assertIn('贪狼', all_major)

    def test_三方四正评分与本宫不同(self):
        """三方四正评分应与本宫评分有差异(综合了对宫和三合)"""
        chart = self.e.compute((1893, 11, 19), 8, 'male')
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        base = self.e.score_topic(chart, full, '健康', lunar_date=(1893, 11, 19))
        sf = self.e.score_topic_sanfang(chart, full, '健康', lunar_date=(1893, 11, 19))
        # 疾厄宫空宫, 但三方四正有吉星, 评分应不同
        self.assertNotEqual(base['score'], sf['score'])

    def test_三方四正返回结构(self):
        """score_topic_sanfang应返回sanfang_sizheng结构"""
        chart = self.e.compute((1960, 5, 5), 4, 'male')
        full = self.e.full_chart((1960, 5, 5), 4, 'male')
        result = self.e.score_topic_sanfang(chart, full, '财运', lunar_date=(1960, 5, 5))
        self.assertIn('sanfang_sizheng', result)
        self.assertIn('ben', result['sanfang_sizheng'])
        self.assertIn('dui', result['sanfang_sizheng'])
        self.assertIn('all_major', result['sanfang_sizheng'])


class TestZiweiZihuaLaiyin(unittest.TestCase):
    """宫干自化 + 来因宫测试 V2.9"""
    @classmethod
    def setUpClass(cls):
        cls.e = ZiweiEngine()

    def test_宫干自化禄(self):
        """甲干宫有廉贞主星应自化禄"""
        # 毛泽东命盘: 迁移宫甲干, 主星廉贞 -> 自化禄
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        zihua = self.e.get_zigong_zihua(full, '迁移')
        self.assertIn('自化禄', zihua)

    def test_宫干自化权(self):
        """丁干宫有天同主星应自化权"""
        # 毛泽东命盘: 子女宫丁干, 主星天同 -> 自化权
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        zihua = self.e.get_zigong_zihua(full, '子女')
        self.assertIn('自化权', zihua)

    def test_无自化宫位(self):
        """宫干四化星不在本宫应无自化"""
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        # 命宫庚干, 四化太阳/武曲/太阴/天同, 都不在命宫(命宫贪狼)
        zihua = self.e.get_zigong_zihua(full, '命宫')
        self.assertEqual(zihua, [])

    def test_来因宫_化忌(self):
        """贪狼化忌的来因宫应是癸干宫(田宅)"""
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        laiyin = self.e.get_laiyin_gong(full, '贪狼', '化忌')
        self.assertEqual(laiyin, '田宅')

    def test_来因宫_化禄(self):
        """廉贞化禄的来因宫应是甲干宫"""
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        laiyin = self.e.get_laiyin_gong(full, '廉贞', '化禄')
        # 甲干宫有迁移和官禄, 来因宫应是其中之一
        self.assertIn(laiyin, ['迁移', '官禄'])

    def test_所有自化宫位(self):
        """get_all_zihua应返回所有有自化的宫位"""
        full = self.e.full_chart((1893, 11, 19), 8, 'male')
        all_zihua = self.e.get_all_zihua(full)
        self.assertIsInstance(all_zihua, dict)
        self.assertGreater(len(all_zihua), 0)
        # 迁移宫应有自化禄
        self.assertIn('迁移', all_zihua)
        self.assertIn('自化禄', all_zihua['迁移'])


class TestZiweiLiunianSihua(unittest.TestCase):
    """流年四化测试 V3.0"""
    @classmethod
    def setUpClass(cls):
        cls.e = ZiweiEngine()
        # 毛泽东: 阳历1893-12-26寅时, 阴历1893-11-19, hour=4
        cls.ld = (1893, 11, 19)
        cls.hour = 4
        cls.chart = cls.e.compute(cls.ld, cls.hour, 'male')
        cls.full = cls.e.full_chart(cls.ld, cls.hour, 'male')

    def test_流年四化落入本宫(self):
        """1949年己干贪狼权应入夫妻宫(贪狼为本宫主星), 详情含流年权且评分高于本命"""
        base = self.e.score_topic(self.chart, self.full, '婚姻', lunar_date=self.ld)
        r = self.e.score_topic(self.chart, self.full, '婚姻', lunar_date=self.ld, target_year=1949)
        self.assertIn('流年权', r['details'])
        self.assertGreater(r['score'], base['score'])

    def test_流年四化辅星检测(self):
        """1966年丙干文昌科应入夫妻宫(文昌为辅星), 详情含流年科"""
        # 丙干四化: 天同禄/天机权/文昌科/廉贞忌
        # hour=4命盘夫妻宫辅星文昌(化科), 验证辅星也能被流年四化检测到
        base = self.e.score_topic(self.chart, self.full, '婚姻', lunar_date=self.ld)
        r = self.e.score_topic(self.chart, self.full, '婚姻', lunar_date=self.ld, target_year=1966)
        self.assertIn('流年科', r['details'])
        self.assertGreaterEqual(r['score'], base['score'])

    def test_无target_year无流年四化(self):
        """不传target_year时不应有流年四化"""
        r = self.e.score_topic(self.chart, self.full, '婚姻', lunar_date=self.ld)
        self.assertNotIn('流年', r['details'])

    def test_不同年份评分不同(self):
        """不同流年天干应产生不同评分"""
        r1 = self.e.score_topic(self.chart, self.full, '婚姻', lunar_date=self.ld, target_year=1949)
        r2 = self.e.score_topic(self.chart, self.full, '婚姻', lunar_date=self.ld, target_year=1966)
        self.assertNotEqual(r1['score'], r2['score'])
        self.assertGreater(r1['score'], r2['score'])


if __name__ == "__main__":
    unittest.main()
