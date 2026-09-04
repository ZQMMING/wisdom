"""
P2.6-B Algorithm Authority Mapping: 验证 _ten_god 算法的经典授权完整性
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from tongshu.engines.bazi_engine import (
    _ten_god,
    STEM_ELEMENT,
    STEM_POLARITY,
    _GENERATES,
    _CONTROLS,
    HEAVENLY_STEMS,
)


class TestTenGodAlgorithmAuthority:
    """验证 _ten_god 算法的每一步都有经典原文对应"""

    def test_algorithm_step1_element_extraction(self):
        """Step 1: 五行提取 - 对应 E-ZQ-051-001"""
        # 验证所有天干都有五行定义
        for stem in HEAVENLY_STEMS:
            assert stem in STEM_ELEMENT, f"{stem} missing from STEM_ELEMENT"
        
        # 验证五行定义与经典一致
        assert STEM_ELEMENT["JIA"] == "WOOD"   # 甲木
        assert STEM_ELEMENT["YI"] == "WOOD"    # 乙木
        assert STEM_ELEMENT["BING"] == "FIRE"  # 丙火
        assert STEM_ELEMENT["DING"] == "FIRE"  # 丁火
        assert STEM_ELEMENT["WU"] == "EARTH"   # 戊土
        assert STEM_ELEMENT["JI"] == "EARTH"   # 己土
        assert STEM_ELEMENT["GENG"] == "METAL" # 庚金
        assert STEM_ELEMENT["XIN"] == "METAL"  # 辛金
        assert STEM_ELEMENT["REN"] == "WATER"  # 壬水
        assert STEM_ELEMENT["GUI"] == "WATER"  # 癸水

    def test_algorithm_step2_polarity_extraction(self):
        """Step 2: 阴阳提取 - 对应 E-ZQ-051-001"""
        # 验证所有天干都有阴阳定义
        for stem in HEAVENLY_STEMS:
            assert stem in STEM_POLARITY, f"{stem} missing from STEM_POLARITY"
        
        # 验证阴阳交替与经典一致
        # 阳干: 甲丙戊庚壬
        assert STEM_POLARITY["JIA"] == "YANG"
        assert STEM_POLARITY["BING"] == "YANG"
        assert STEM_POLARITY["WU"] == "YANG"
        assert STEM_POLARITY["GENG"] == "YANG"
        assert STEM_POLARITY["REN"] == "YANG"
        # 阴干: 乙丁己辛癸
        assert STEM_POLARITY["YI"] == "YIN"
        assert STEM_POLARITY["DING"] == "YIN"
        assert STEM_POLARITY["JI"] == "YIN"
        assert STEM_POLARITY["XIN"] == "YIN"
        assert STEM_POLARITY["GUI"] == "YIN"

    def test_algorithm_step3_generates_mapping(self):
        """Step 3: 相生关系 - 对应 E-ZQ-051-001"""
        # 经典: 木生火，火生土，土生金，金生水，水生木
        assert _GENERATES["WOOD"] == "FIRE"
        assert _GENERATES["FIRE"] == "EARTH"
        assert _GENERATES["EARTH"] == "METAL"
        assert _GENERATES["METAL"] == "WATER"
        assert _GENERATES["WATER"] == "WOOD"

    def test_algorithm_step4_controls_mapping(self):
        """Step 4: 相克关系 - 对应 E-ZQ-051-001"""
        # 经典: 木克土，土克水，水克火，火克金，金克木
        assert _CONTROLS["WOOD"] == "EARTH"
        assert _CONTROLS["EARTH"] == "WATER"
        assert _CONTROLS["WATER"] == "FIRE"
        assert _CONTROLS["FIRE"] == "METAL"
        assert _CONTROLS["METAL"] == "WOOD"

    def test_algorithm_step5_ten_god_naming(self):
        """Step 5: 十神命名 - 对应 E-ZQ-052-001"""
        # 验证十神命名体系与经典一致
        # 同我者: 比肩(同阴阳), 劫财(异阴阳)
        assert _ten_god("JIA", "JIA") == "比肩"  # 阳+阳=比肩
        assert _ten_god("JIA", "YI") == "劫财"  # 阳+阴=劫财
        assert _ten_god("YI", "YI") == "比肩"   # 阴+阴=比肩
        assert _ten_god("YI", "JIA") == "劫财"  # 阴+阳=劫财
        
        # 我生者: 食神(同阴阳), 伤官(异阴阳)
        assert _ten_god("JIA", "BING") == "食神"  # 木生火，阳+阳=食神
        assert _ten_god("JIA", "DING") == "伤官"  # 木生火，阳+阴=伤官
        
        # 生我者: 偏印(同阴阳), 正印(异阴阳)
        assert _ten_god("JIA", "REN") == "偏印"   # 水生木，阳+阳=偏印
        assert _ten_god("YI", "REN") == "正印"    # 水生木，阴+阳=正印
        
        # 克我者: 七杀(同阴阳), 正官(异阴阳)
        assert _ten_god("JIA", "GENG") == "七杀"  # 金克木，阳+阳=七杀
        assert _ten_god("JIA", "XIN") == "正官"   # 金克木，阳+阴=正官
        
        # 我克者: 偏财(同阴阳), 正财(异阴阳)
        assert _ten_god("JIA", "WU") == "偏财"    # 木克土，阳+阳=偏财
        assert _ten_god("JIA", "JI") == "正财"    # 木克土，阳+阴=正财

    def test_algorithm_completeness(self):
        """验证所有100种组合都有有效输出"""
        valid_ten_gods = {
            "比肩", "劫财", "食神", "伤官",
            "偏印", "正印", "七杀", "正官", "偏财", "正财"
        }
        for dm in HEAVENLY_STEMS:
            for other in HEAVENLY_STEMS:
                result = _ten_god(dm, other)
                assert result in valid_ten_gods, f"Invalid: {dm}-{other} -> {result}"


class TestFiveElementBalanceEngineeringHeuristics:
    """验证五行权重算法的工程自定义部分"""

    def test_classical_basis_exists(self):
        """理论基础证据存在"""
        # 这不是测试代码正确性，而是确认理论基础证据存在
        # 实际权重算法是工程自定义
        pass  # 已在P2.6报告中记录

    def test_thresholds_are_engineering(self):
        """确认阈值是工程自定义，不是经典授权"""
        # 0.40 和 0.05 没有经典出处
        # 这是 Engineering Heuristic
        # 测试验证：算法确实使用这些阈值
        from tongshu.engines.bazi_engine import BaziChart, Pillar, calc_five_element_balance
        
        # 构造极端案例：所有木
        chart = BaziChart(
            year_pillar=Pillar("JIA", "YIN"),
            month_pillar=Pillar("YI", "MAO"),
            day_pillar=Pillar("BING", "YIN"),
            hour_pillar=Pillar("DING", "MAO"),
            day_master="BING",
            luck_pillars=[],
        )
        balance, imbalance = calc_five_element_balance(chart)
        
        # 验证算法行为（不验证阈值正确性）
        assert balance["WOOD"] > 0.5  # 木应该占主导
        assert imbalance == True       # 应该标记失衡


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
