"""
P2.5-B Integration Tests: 八字排盘接入验证

通过真实历史案例验证计算结果的准确性。
重点测试：
1. 历法计算（年柱、月柱、日柱、时柱）
2. 十神计算
3. 地支关系（冲、合、害、刑、空亡、桃花）
4. 五行分布
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from tongshu.engines.bazi_engine import (
    BaziEngine,
    BaziChart,
    Pillar,
    calc_branch_clash_map,
    calc_branch_harm_map,
    calc_branch_he_map,
    calc_branch_sanhe_map,
    calc_branch_sanxing_map,
    calc_kong_wang,
    calc_peach_blossom,
    calc_five_element_balance,
    _ten_god,
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES,
    STEM_ELEMENT,
)


def create_chart(year, month, day, hour, gender="male"):
    """创建测试用chart"""
    engine = BaziEngine()
    return engine.compute((year, month, day, hour), gender=gender)


class TestHistoricalCases:
    """历史案例验证"""

    def test_jixiaolan(self):
        """纪晓岚：1724年7月16日 午时
        
        传统排盘结果：
        年柱：甲辰
        月柱：辛未
        日柱：戊辰
        时柱：戊午
        """
        chart = create_chart(1724, 7, 16, 12)

        # 年柱：甲辰
        assert chart.year_pillar.heavenly_stem == "JIA"
        assert chart.year_pillar.earthly_branch == "CHEN"

        # 月柱：辛未
        assert chart.month_pillar.heavenly_stem == "XIN"
        assert chart.month_pillar.earthly_branch == "WEI"

        # 日柱：戊辰
        assert chart.day_pillar.heavenly_stem == "WU"
        assert chart.day_pillar.earthly_branch == "CHEN"

        # 时柱：戊午
        assert chart.hour_pillar.heavenly_stem == "WU"
        assert chart.hour_pillar.earthly_branch == "WU"

        print(f"✓ 纪晓岚八字验证通过: 甲辰 辛未 戊辰 戊午")

    def test_test_case_known_answer(self):
        """已知答案的测试案例"""
        # 2000年1月1日 0时0分（公历）
        # 验证边界情况
        chart = create_chart(2000, 1, 1, 0)

        # 四柱应已正确计算
        assert chart.year_pillar is not None
        assert chart.month_pillar is not None
        assert chart.day_pillar is not None
        assert chart.hour_pillar is not None

        # 日主应与日干一致
        assert chart.day_master == chart.day_pillar.heavenly_stem

        # 四干四支应各4个
        assert len(chart.four_stems()) == 4
        assert len(chart.four_branches()) == 4

        print(f"✓ 边界案例验证通过")


class TestTenGodCalculation:
    """十神计算验证
    
    注意：_ten_god(day_master, other) 的第一个参数是日主
    """

    def test_bi_jian(self):
        """比肩：同五行同阴阳"""
        # 甲见甲
        assert _ten_god("JIA", "JIA") == "比肩"
        # 乙见乙
        assert _ten_god("YI", "YI") == "比肩"

    def test_jie_cai(self):
        """劫财：同五行异阴阳"""
        # 甲见乙
        assert _ten_god("JIA", "YI") == "劫财"
        # 乙见甲
        assert _ten_god("YI", "JIA") == "劫财"

    def test_shi_shen(self):
        """食神：日主生他，同阴阳"""
        # 甲木生丙火（阳生阳）
        assert _ten_god("JIA", "BING") == "食神"
        # 乙木生丁火（阴生阴）
        assert _ten_god("YI", "DING") == "食神"

    def test_shang_guan(self):
        """伤官：日主生他，异阴阳"""
        # 甲木生丁火（阳生阴）
        assert _ten_god("JIA", "DING") == "伤官"
        # 乙木生丙火（阴生阳）
        assert _ten_god("YI", "BING") == "伤官"

    def test_pian_yin(self):
        """偏印：他生日主，同阴阳
        
        壬水生甲木（阳水生日主阳木）→ 偏印
        """
        assert _ten_god("JIA", "REN") == "偏印"
        assert _ten_god("YI", "GUI") == "偏印"

    def test_zheng_yin(self):
        """正印：他生日主，异阴阳
        
        壬水生乙木（阳水生日主阴木）→ 正印
        """
        assert _ten_god("YI", "REN") == "正印"
        assert _ten_god("JIA", "GUI") == "正印"

    def test_qi_sha(self):
        """七杀：他克日主，同阴阳
        
        庚金克甲木（阳金克日主阳木）→ 七杀
        """
        assert _ten_god("JIA", "GENG") == "七杀"
        assert _ten_god("YI", "XIN") == "七杀"

    def test_zheng_guan(self):
        """正官：他克日主，异阴阳
        
        辛金克甲木（阴金克日主阳木）→ 正官
        """
        assert _ten_god("JIA", "XIN") == "正官"
        assert _ten_god("YI", "GENG") == "正官"

    def test_pian_cai(self):
        """偏财：日主克他，同阴阳"""
        # 甲木克戊土（阳克阳）
        assert _ten_god("JIA", "WU") == "偏财"
        # 乙木克己土（阴克阴）
        assert _ten_god("YI", "JI") == "偏财"

    def test_zheng_cai(self):
        """正财：日主克他，异阴阳"""
        # 甲木克己土（阳克阴）
        assert _ten_god("JIA", "JI") == "正财"
        # 乙木克戊土（阴克阳）
        assert _ten_god("YI", "WU") == "正财"

    def test_ten_god_completeness(self):
        """所有天干组合必须返回有效十神"""
        valid_ten_gods = {
            "比肩", "劫财", "食神", "伤官",
            "偏印", "正印", "七杀", "正官", "偏财", "正财"
        }
        for dm in HEAVENLY_STEMS:
            for other in HEAVENLY_STEMS:
                result = _ten_god(dm, other)
                assert result in valid_ten_gods, f"Invalid ten god: {dm}-{other} -> {result}"

    def test_ten_god_from_jixiaolan(self):
        """从纪晓岚八字验证十神
        
        纪晓岚：戊日主
        年干甲 → 七杀（甲木克戊土，阳克阳）
        月干辛 → 伤官（戊土生辛金，阳生阴）
        时干戊 → 比肩（戊见戊，同五行同阴阳）
        """
        chart = create_chart(1724, 7, 16, 12)
        
        assert _ten_god("WU", "JIA") == "七杀"
        assert _ten_god("WU", "XIN") == "伤官"
        assert _ten_god("WU", "WU") == "比肩"


class TestBranchRelationships:
    """地支关系验证"""

    def test_chong_from_jixiaolan(self):
        """从纪晓岚八字验证六冲
        
        纪晓岚八字：甲辰 辛未 戊辰 戊午
        - 年支辰与时支午无冲
        - 日支辰与年支辰相同（自刑）
        """
        chart = create_chart(1724, 7, 16, 12)
        result = calc_branch_clash_map(chart)

        # 辰午无冲关系
        clash_pairs = list(result.keys())
        assert "CHEN-WU" not in clash_pairs

    def test_he_from_jixiaolan(self):
        """从纪晓岚八字验证六合"""
        chart = create_chart(1724, 7, 16, 12)
        result = calc_branch_he_map(chart)

        # 辰酉合，但纪晓岚八字无酉
        # 只验证函数不报错且返回正确格式
        assert isinstance(result, dict)

    def test_kong_wang_from_jixiaolan(self):
        """从纪晓岚八字验证空亡
        
        戊辰日属于甲子旬（0-9），空亡为戌亥
        """
        chart = create_chart(1724, 7, 16, 12)
        result = calc_kong_wang(chart)

        # 戊辰日属于甲子旬，空亡应为戌亥
        assert result == ("XU", "HAI"), f"Expected ('XU', 'HAI'), got {result}"

    def test_peach_blossom_from_jixiaolan(self):
        """从纪晓岚八字验证桃花"""
        chart = create_chart(1724, 7, 16, 12)
        result = calc_peach_blossom(chart)

        # 戊日主，桃花在卯
        # 纪晓岚八字无卯，应为False
        assert result == False

    def test_sanhe_incomplete(self):
        """三合局不完整不应成局"""
        # 申子辰水局 - 缺少辰
        from tongshu.engines.bazi_engine import Pillar, BaziChart
        test_chart = BaziChart(
            year_pillar=Pillar("JIA", "SHEN"),
            month_pillar=Pillar("XIN", "ZI"),
            day_pillar=Pillar("WU", "MAO"),
            hour_pillar=Pillar("WU", "YOU"),
            day_master="WU",
            luck_pillars=[],
        )
        result = calc_branch_sanhe_map(test_chart)
        assert "SHEN-ZI-CHEN" not in result

    def test_sanxing_complete(self):
        """三刑局三支齐全应成局"""
        from tongshu.engines.bazi_engine import Pillar, BaziChart
        # 寅巳申三刑
        test_chart = BaziChart(
            year_pillar=Pillar("JIA", "YIN"),
            month_pillar=Pillar("BING", "SI"),
            day_pillar=Pillar("WU", "SHEN"),
            hour_pillar=Pillar("DING", "MAO"),
            day_master="WU",
            luck_pillars=[],
        )
        result = calc_branch_sanxing_map(test_chart)
        # key是sorted的，所以是 SHEN-SI-YIN
        assert "SHEN-SI-YIN" in result


class TestElementBalance:
    """五行分布验证"""

    def test_five_element_sum_is_one(self):
        """五行比例总和必须为1.0"""
        chart = create_chart(1724, 7, 16, 12)
        balance, imbalance = calc_five_element_balance(chart)

        total = sum(balance.values())
        assert abs(total - 1.0) < 0.0001, f"Sum is {total}, expected 1.0"

    def test_all_elements_present(self):
        """五行分布必须包含所有五行"""
        chart = create_chart(1724, 7, 16, 12)
        balance, _ = calc_five_element_balance(chart)

        assert set(balance.keys()) == {"WOOD", "FIRE", "EARTH", "METAL", "WATER"}

    def test_wood_dominant_case(self):
        """木旺案例验证"""
        # 构造木旺的八字
        chart = BaziChart(
            year_pillar=Pillar("JIA", "YIN"),
            month_pillar=Pillar("YI", "MAO"),
            day_pillar=Pillar("BING", "YIN"),
            hour_pillar=Pillar("DING", "MAO"),
            day_master="BING",
            luck_pillars=[],
        )
        balance, imbalance = calc_five_element_balance(chart)

        # 木应该占主导
        assert balance["WOOD"] > 0.5
        # 应该标记失衡
        assert imbalance == True


class TestDateBoundary:
    """日期边界验证"""

    def test_late_zi_boundary(self):
        """验证夜子时边界（23:00）"""
        # 晚上23:00出生，应该是第二天的子时
        chart = create_chart(2000, 1, 1, 23)

        # 时柱应该是子时
        assert chart.hour_pillar.earthly_branch == "ZI"

    def test_day_change_at_midnight(self):
        """验证午夜换日"""
        chart1 = create_chart(2000, 1, 1, 23)
        chart2 = create_chart(2000, 1, 2, 0)

        # 两个时间应该是同一个日柱
        assert chart1.day_pillar == chart2.day_pillar

    def test_day_change_sequence(self):
        """验证连续几天的日柱变化"""
        chart1 = create_chart(2000, 1, 1, 12)
        chart2 = create_chart(2000, 1, 2, 12)
        chart3 = create_chart(2000, 1, 3, 12)

        # 日柱应该每天变化
        assert chart1.day_pillar != chart2.day_pillar
        assert chart2.day_pillar != chart3.day_pillar


class TestDeterminism:
    """确定性验证"""

    def test_same_input_same_output(self):
        """相同输入必须产生相同输出"""
        chart1 = create_chart(1724, 7, 16, 12)
        chart2 = create_chart(1724, 7, 16, 12)

        assert chart1 == chart2

    def test_deterministic_tengod(self):
        """十神计算必须确定性"""
        for _ in range(100):
            chart1 = create_chart(1724, 7, 16, 12)
            chart2 = create_chart(1724, 7, 16, 12)
            assert chart1 == chart2

    def test_multiple_cases_consistent(self):
        """多组案例保持一致性"""
        cases = [
            (1724, 7, 16, 12),
            (1983, 11, 3, 12),  # 用户提到的案例
            (2000, 1, 1, 0),
            (1990, 5, 15, 14),
        ]
        for year, month, day, hour in cases:
            chart = create_chart(year, month, day, hour)
            # 每个案例都应产生有效的四柱
            assert chart.year_pillar is not None
            assert chart.month_pillar is not None
            assert chart.day_pillar is not None
            assert chart.hour_pillar is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
