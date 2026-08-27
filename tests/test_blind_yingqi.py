# -*- coding: utf-8 -*-
"""盲派应期断法引擎测试
交叉验证源: D:/today/盲派命理-案例资料集.md §6应期断法 + §2应期断案例
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path("D:/today/backend/src")))

from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine, DAXIAN_SEGMENTS


class TestBlindYingqi(unittest.TestCase):
    def setUp(self):
        self.engine = BlindYingqiEngine()
        self.be = BaziEngine()

    def test_daxian_segments(self):
        """大限分段: 年柱1-18/月柱18-35/日柱35-55/时柱55+(典籍)."""
        eng = self.engine
        self.assertEqual(eng._daxian_of_age(10)[0], "year")
        self.assertEqual(eng._daxian_of_age(25)[0], "month")
        self.assertEqual(eng._daxian_of_age(45)[0], "day")
        self.assertEqual(eng._daxian_of_age(70)[0], "hour")

    def test_flow_year_ganzhi(self):
        """流年干支计算正确."""
        eng = self.engine
        # 2024甲辰, 2025乙巳, 2026丙午
        self.assertEqual(eng._ganzhi_of_year(2024), ("JIA", "CHEN"))
        self.assertEqual(eng._ganzhi_of_year(2025), ("YI", "SI"))
        self.assertEqual(eng._ganzhi_of_year(2026), ("BING", "WU"))

    def test_analyze_basic(self):
        """基本分析: 返回大限/大运/流年."""
        r = self.engine.analyze((1990, 5, 15, 12), "male", target_age=40)
        self.assertEqual(r.age, 40)
        self.assertEqual(r.flow_year, 2030)
        self.assertIn(r.daxian_pillar, ("year", "month", "day", "hour"))
        self.assertTrue(r.luck_stem and r.luck_branch)
        self.assertTrue(r.flow_stem and r.flow_branch)

    def test_analyze_by_year(self):
        """按目标年份分析."""
        r = self.engine.analyze((1990, 5, 15, 12), "male", target_year=2025)
        self.assertEqual(r.age, 35)
        self.assertEqual(r.flow_year, 2025)

    def test_luck_pillars_ext(self):
        """扩展大运柱数量正确."""
        chart = self.be.compute((1990, 5, 15, 12), gender="male")
        pillars = self.engine._luck_pillars_ext(chart)
        self.assertEqual(len(pillars), 8)

    def test_trigger_cihong(self):
        """冲引动识别: 流年支冲命局支."""
        r = self.engine.analyze((1948, 1, 23, 18), "male", target_age=52)
        kinds = [e['mechanism'] for e in r.yingqi_events]
        # 案例48: 丑未冲开墓库
        self.assertIn('muku_kai', kinds)

    def test_case3_lu_chuan(self):
        """案例3(禄坏): 庚寅年寅申冲触两申(禄), 应灾."""
        # 戊申己未庚申辛巳近似: 用1968-07-01, 30岁
        r = self.engine.analyze((1968, 7, 1, 10), "male", target_age=30)
        # 流年YIN冲SHEN(禄)应为冲主位
        found_chong = any(
            e['mechanism'] == 'chong' and 'SHEN' in e['mech']
            for e in r.yingqi_events
        )
        # 寅申冲识别
        self.assertTrue(found_chong or any('YIN' in e['mech'] for e in r.yingqi_events))

    def test_tougan_yingqi(self):
        """遁藏透干应期: 命局藏干现于运年天干."""
        # 案例48(1948-01-23, 丁亥癸丑丁未己酉)大限day(未)藏丁透干
        r = self.engine.analyze((1948, 1, 23, 18), "male", target_age=52)
        kinds = [e['mechanism'] for e in r.yingqi_events]
        self.assertIn('tougan', kinds)

    def test_sanxing_yingqi(self):
        """三刑引动(恃势之刑): 案例15(乙未乙酉丙戌己丑)16岁死母."""
        # 丑未戌三刑: 未大限遇丑戌构成恃势之刑
        r = self.engine.analyze((1895, 10, 6, 2), "female", target_age=16)
        kinds = [e['mechanism'] for e in r.yingqi_events]
        self.assertIn('sanxing', kinds)

    def test_muku_kai_yingqi(self):
        """墓库开闭应期: 案例48(丁亥癸丑丁未己酉)大限未冲开丑金库."""
        r = self.engine.analyze((1948, 1, 23, 18), "male", target_age=50)
        kinds = [e['mechanism'] for e in r.yingqi_events]
        self.assertIn('muku_kai', kinds)


if __name__ == "__main__":
    unittest.main()
