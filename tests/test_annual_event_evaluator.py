# -*- coding: utf-8 -*-
"""IMP-08 V2: 四体系交叉验证流年事件评估层测试

测试 AnnualEventEvaluator 功能：
1. BaziScorer 基本评分逻辑
2. 跨体系信号综合
3. 选项解析
4. 实际案例评测
"""

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tongshu.engines.annual_event_evaluator import (
    AnnualEventEvaluator,
    BaziScorer,
    CrossValidationLayer,
    EventResult,
)


class TestBaziScorer:
    """子平/盲派评分测试"""

    def setup_method(self):
        self.scorer = BaziScorer()

    def test_ten_god_basic(self):
        """十神计算基本逻辑"""
        # 甲日主 + 甲年干 = 比肩
        assert self.scorer.ten_god("JIA", "JIA") == "比肩"
        # 甲日主 + 乙年干 = 劫财
        assert self.scorer.ten_god("JIA", "YI") == "劫财"
        # 甲日主 + 丙年干 = 食神
        assert self.scorer.ten_god("JIA", "BING") == "食神"
        # 甲日主 + 戊年干 = 偏财 (我克，同性)
        assert self.scorer.ten_god("JIA", "WU") == "偏财"
        # 甲日主 + 己年干 = 正财 (我克，异性)
        assert self.scorer.ten_god("JIA", "JI") == "正财"
        # 甲日主 + 壬年干 = 偏印/枭神 (生我，同性)
        assert self.scorer.ten_god("JIA", "REN") == "枭神"
        # 甲日主 + 癸年干 = 正印 (生我，异性)
        assert self.scorer.ten_god("JIA", "GUI") == "正印"
        # 甲日主 + 庚年干 = 七杀 (克我，同性)
        assert self.scorer.ten_god("JIA", "GENG") == "七杀"
        # 甲日主 + 辛年干 = 正官 (克我，异性)
        assert self.scorer.ten_god("JIA", "XIN") == "正官"

    def test_ganzhi_basic(self):
        """干支计算基本逻辑"""
        # 2020 = 庚子
        assert self.scorer.ganzhi(2020) == ("GENG", "ZI")
        # 2021 = 辛丑
        assert self.scorer.ganzhi(2021) == ("XIN", "CHOU")
        # 2022 = 壬寅
        assert self.scorer.ganzhi(2022) == ("REN", "YIN")

    def test_disaster_score_chaji(self):
        """灾劫评分：七杀冲"""
        dm, fourb, _, verdict = self.scorer.compute(1982, 9, 27, 15, "female")
        fs, fb = self.scorer.ganzhi(2002)  # 壬午 - 午冲子
        score = self.scorer.score_disaster(dm, fs, fb, fourb, verdict)
        assert score >= 0  # 非负

    def test_wealth_score_caizen(self):
        """财运评分：正财/偏财"""
        dm, fourb, _, verdict = self.scorer.compute(1983, 11, 1, 21, "male")
        fs, fb = self.scorer.ganzhi(2010)  # 庚寅 - 看十神
        score = self.scorer.score_wealth(dm, fs, fb, fourb, verdict)
        assert score >= 0  # 非负


class TestCrossValidationLayer:
    """交叉验证层测试"""

    def setup_method(self):
        self.cv = CrossValidationLayer()

    def test_combine_signals_weights(self):
        """V4 五体系权重综合"""
        bazi_d, blind_d, ziwei_d, heluo_d, yi_d = 2.0, 1.0, 0.8, 0.5, 0.1
        bazi_w, blind_w, ziwei_w, heluo_w, yi_w = 1.5, 0.8, 0.6, 0.3, 0.1
        d_score, w_score = self.cv.combine_signals(
            bazi_d, blind_d, ziwei_d, heluo_d, yi_d,
            bazi_w, blind_w, ziwei_w, heluo_w, yi_w,
        )
        # V4 权重: 子平40% + 盲派20% + 紫微20% + 河洛12% + 易经8%
        expected_d = (2.0 * 0.40 + 1.0 * 0.20 + 0.8 * 0.20 + 0.5 * 0.12 + 0.1 * 0.08)
        expected_w = (1.5 * 0.40 + 0.8 * 0.20 + 0.6 * 0.20 + 0.3 * 0.12 + 0.1 * 0.08)
        assert abs(d_score - expected_d) < 0.01
        assert abs(w_score - expected_w) < 0.01

    def test_rank_years(self):
        """年份排序"""
        from tongshu.engines.annual_event_evaluator import AnnualPrediction
        preds = [
            AnnualPrediction(2010, 5.0, 3.0),
            AnnualPrediction(2005, 8.0, 2.0),
            AnnualPrediction(2015, 3.0, 5.0),
        ]
        ranked = self.cv.rank_years(preds)
        assert ranked[0].year == 2005  # 灾劫分最高


class TestAnnualEventEvaluator:
    """主评估器测试"""

    def setup_method(self):
        self.evaluator = AnnualEventEvaluator()
        with open(".tmp_cases/fate_bench/data/hkjfma_qa.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def test_parse_options_with_years(self):
        """选项年份解析"""
        options = [
            {"letter": "A", "text": "2002年财运"},
            {"letter": "B", "text": "2008年破财"},
            {"letter": "C", "text": "其他"},
        ]
        year_map = self.evaluator._parse_options(options)
        assert year_map == {"2002": "A", "2008": "B"}

    def test_parse_options_without_years(self):
        """无年份选项"""
        options = [
            {"letter": "A", "text": "被劫"},
            {"letter": "B", "text": "破产"},
        ]
        year_map = self.evaluator._parse_options(options)
        assert year_map == {}

    def test_disaster_case_with_year(self):
        """灾劫案例（有年份选项）"""
        # hkjfma_2010_01: 女命 1982-09-27 申时
        case = next(c for c in self.data if c["id"] == "hkjfma_2010_01")
        result = self.evaluator.evaluate_case(case, "disaster")
        assert result.case_id == "hkjfma_2010_01"
        assert result.predicted in ["A", "B", "C", "D", "E"]
        assert result.actual == "A"
        # 检查证据链
        assert len(result.evidence) > 0

    def test_wealth_case_with_year(self):
        """财运案例（有年份选项）"""
        # hkjfma_2018_06: 男命 1972-01-26 卯时
        case = next(c for c in self.data if c["id"] == "hkjfma_2018_06")
        result = self.evaluator.evaluate_case(case, "wealth")
        assert result.case_id == "hkjfma_2018_06"
        assert result.predicted in ["A", "B", "C", "D"]

    @pytest.mark.slow
    def test_full_evaluation(self):
        """完整评测（耗时）"""
        disaster_cases = [c for c in self.data if c.get("category") == "灾劫"]
        wealth_cases = [c for c in self.data if c.get("category") == "财运"]

        disaster_result = self.evaluator.run_evaluation(disaster_cases, "disaster")
        wealth_result = self.evaluator.run_evaluation(wealth_cases, "wealth")

        # 统计
        assert disaster_result["total"] == len(disaster_cases)
        assert wealth_result["total"] == len(wealth_cases)
        assert 0 <= disaster_result["accuracy"] <= 100
        assert 0 <= wealth_result["accuracy"] <= 100


class TestYearParsing:
    """年份解析边界测试"""

    def setup_method(self):
        self.evaluator = AnnualEventEvaluator()

    def test_option_text_patterns(self):
        """选项文本中的年份模式"""
        patterns = [
            ("2002壬午", "2002"),
            ("1965年4岁", "1965"),
            ("2010财运", "2010"),
            ("1999年破财", "1999"),
        ]
        for text, expected in patterns:
            match = re.search(r"(19\d{2}|20\d{2})", text)
            assert match and match.group(1) == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
