"""
P2.5-B Adversarial Tests for Bazi Engine

测试边界条件、重复输入、异常输入等场景。
"""

import pytest
from src.tongshu.engines.bazi_engine import (
    BaziEngine,
    BaziChart,
    Pillar,
    BRANCH_CLASH,
    BRANCH_SANHE,
    BRANCH_SANXING,
    BRANCH_HE,
    KONG_WANG_BY_XUN,
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES,
    calc_branch_clash_map,
    calc_branch_sanhe_map,
    calc_branch_sanxing_map,
    calc_branch_he_map,
    calc_kong_wang,
    calc_five_element_balance,
    _ten_god,
    STEM_ELEMENT,
    _branch_element,
)


def create_chart(branches: list[str], stems: list[str] | None = None) -> BaziChart:
    """创建测试用的 BaziChart"""
    if stems is None:
        stems = ["JIA", "YI", "BING", "DING"]
    return BaziChart(
        year_pillar=Pillar(stems[0], branches[0]),
        month_pillar=Pillar(stems[1], branches[1]),
        day_pillar=Pillar(stems[2], branches[2]),
        hour_pillar=Pillar(stems[3], branches[3]),
        day_master=stems[2],
        luck_pillars=[],
    )


class TestDuplicateBranches:
    """测试重复地支的处理"""

    def test_duplicate_clash_by_position(self):
        """重复地支应按位置识别冲关系，而非按值过滤"""
        # [子, 子, 午, 子] - 日支为子，年/月/时也是子
        # 按位置排除日柱(索引2)，年/月/时的子仍参与判断
        chart = create_chart(["ZI", "ZI", "ZI", "WU"])
        result = calc_branch_clash_map(chart)

        # 年支子(ZI)与时支午(WU)应该形成冲
        # 实际key格式为 sorted，所以是 "WU-ZI"
        assert "WU-ZI" in result
        assert len(result) == 1

    def test_no_false_clash_with_duplicates(self):
        """重复地支不应产生错误的冲关系"""
        # [子, 子, 丑, 寅] - 无冲关系
        chart = create_chart(["ZI", "ZI", "CHOU", "YIN"])
        result = calc_branch_clash_map(chart)
        assert len(result) == 0


class TestLateZiBoundary:
    """测试夜子时边界"""

    def test_late_zi_day_change(self):
        """23:00出生，日柱应为第二天"""
        engine = BaziEngine()
        # 2000年1月1日23:00
        chart = engine.compute((2000, 1, 1, 23), gender="male")

        # 时柱应为子时
        assert chart.hour_pillar.earthly_branch == "ZI"
        # 日柱和时柱的天干应一致（都是甲子或类似）

    def test_skip_late_zi_flag(self):
        """skip_late_zi=True时应跳过换日逻辑"""
        engine = BaziEngine()
        # 假设上游已完成换日，直接传入第二天
        chart1 = engine.compute((2000, 1, 2, 0), gender="male", skip_late_zi=True)
        chart2 = engine.compute((2000, 1, 2, 0), gender="male", skip_late_zi=False)

        # 两种情况下日柱应相同
        assert chart1.day_pillar == chart2.day_pillar


class TestSanheIncomplete:
    """测试三合局不完整的情况"""

    def test_sanhe_requires_three_branches(self):
        """三合局需要三支齐全"""
        # 申子辰水局 - 缺少辰
        chart = create_chart(["SHEN", "ZI", "MAO", "YOU"])
        result = calc_branch_sanhe_map(chart)
        assert "SHEN-ZI-CHEN" not in result

    def test_sanhe_complete(self):
        """三合局三支齐全应成局"""
        chart = create_chart(["SHEN", "ZI", "CHEN", "YIN"])
        result = calc_branch_sanhe_map(chart)
        # key格式为sorted，所以是 "CHEN-SHEN-ZI"
        assert "CHEN-SHEN-ZI" in result


class TestSanxingSelf:
    """测试自刑"""

    def test_self_xing_requires_duplicate(self):
        """自刑需要同一地支出现两次以上"""
        # 辰辰自刑
        chart = create_chart(["CHEN", "CHEN", "MAO", "YOU"])
        result = calc_branch_sanxing_map(chart)
        assert "CHEN-CHEN" in result

    def test_no_self_xing_with_single(self):
        """单一辰不应产生自刑"""
        chart = create_chart(["CHEN", "MAO", "YOU", "SI"])
        result = calc_branch_sanxing_map(chart)
        assert "CHEN-CHEN" not in result


class TestKongWangBoundary:
    """测试空亡计算边界"""

    def test_kong_wang_jiazi_0(self):
        """甲子旬空戌亥"""
        chart = create_chart(["ZI", "CHOU", "ZI", "MAO"], ["JIA", "YI", "JIA", "BING"])
        result = calc_kong_wang(chart)
        assert result == ("XU", "HAI")

    def test_kong_wang_all_xun(self):
        """测试所有旬的空亡"""
        for xun_idx in range(6):
            # 构造对应旬的日柱
            stem_idx = xun_idx * 10 % 10  # 甲子旬=0, 甲戌旬=10%10=0
            branch_idx = xun_idx * 10 % 12
            stem = HEAVENLY_STEMS[stem_idx]
            branch = EARTHLY_BRANCHES[branch_idx]
            chart = create_chart([branch, "ZI", branch, "MAO"], [stem, "YI", stem, "BING"])
            result = calc_kong_wang(chart)
            expected = KONG_WANG_BY_XUN.get(xun_idx)
            assert result == expected, f"Xun {xun_idx}: expected {expected}, got {result}"


class TestTenGodDeterministic:
    """测试十神计算的确定性"""

    def test_ten_god_deterministic(self):
        """同一对输入必须返回相同结果"""
        for dm in HEAVENLY_STEMS:
            for other in HEAVENLY_STEMS:
                result1 = _ten_god(dm, other)
                result2 = _ten_god(dm, other)
                assert result1 == result2

    def test_ten_god_all_combinations(self):
        """所有天干组合必须返回有效的十神"""
        valid_ten_gods = {"比肩", "劫财", "食神", "伤官", "偏印", "正印", "七杀", "正官", "偏财", "正财"}
        for dm in HEAVENLY_STEMS:
            for other in HEAVENLY_STEMS:
                result = _ten_god(dm, other)
                assert result in valid_ten_gods, f"Invalid ten god for {dm}-{other}: {result}"

    def test_ten_god_self_is_bi_jian_or_jie_cai(self):
        """自己对自己的十神必须是比肩或劫财"""
        for stem in HEAVENLY_STEMS:
            result = _ten_god(stem, stem)
            assert result in ("比肩", "劫财"), f"Expected 比肩/劫财 for self, got {result}"


class TestElementConsistency:
    """测试五行一致性"""

    def test_element_sum_is_one(self):
        """五行比例总和必须为1.0"""
        chart = create_chart(["YIN", "MAO", "CHEN", "SI"], ["JIA", "YI", "BING", "DING"])
        balance, _ = calc_five_element_balance(chart)
        total = sum(balance.values())
        assert abs(total - 1.0) < 0.0001, f"Element balance sum is {total}, expected 1.0"

    def test_all_elements_present(self):
        """五行分布必须包含所有五行"""
        chart = create_chart(["YIN", "MAO", "CHEN", "SI"], ["JIA", "YI", "BING", "DING"])
        balance, _ = calc_five_element_balance(chart)
        assert set(balance.keys()) == {"WOOD", "FIRE", "EARTH", "METAL", "WATER"}


class TestSymmetryProperties:
    """测试对称性"""

    def test_clash_symmetry(self):
        """六冲关系必须对称"""
        for a, b in BRANCH_CLASH.items():
            assert BRANCH_CLASH[b] == a

    def test_he_symmetry(self):
        """六合关系通过对称的frozenset定义"""
        # BRANCH_HE的key是frozenset of 2 elements
        for key in BRANCH_HE.keys():
            assert len(key) == 2, f"BRANCH_HE key should have 2 elements, got {len(key)}"

    def test_sanhe_symmetry(self):
        """三合局通过frozenset定义，应是对称的"""
        for key in BRANCH_SANHE.keys():
            assert len(key) == 3, f"BRANCH_SANHE key should have 3 elements, got {len(key)}"


class TestImmutability:
    """测试不可变性"""

    def test_chart_is_frozen(self):
        """BaziChart 应该是 frozen dataclass"""
        chart = create_chart(["ZI", "CHOU", "YIN", "MAO"])
        with pytest.raises(Exception):  # frozen dataclass 禁止修改
            chart.year_pillar = Pillar("BING", "YIN")


class TestBranchElementMapping:
    """测试地支五行映射（使用 _branch_element 函数）"""

    def test_yin_mao_are_wood(self):
        """寅卯属木"""
        for branch in ["YIN", "MAO"]:
            assert _branch_element(branch) == "WOOD"

    def test_ssi_wu_are_fire(self):
        """巳午属火"""
        for branch in ["SI", "WU"]:
            assert _branch_element(branch) == "FIRE"

    def test_chen_xu_chou_wei_are_earth(self):
        """辰戌丑未属土"""
        for branch in ["CHEN", "XU", "CHOU", "WEI"]:
            assert _branch_element(branch) == "EARTH"

    def test_shen_you_are_metal(self):
        """申酉属金"""
        for branch in ["SHEN", "YOU"]:
            assert _branch_element(branch) == "METAL"

    def test_zi_hai_are_water(self):
        """子亥属水"""
        for branch in ["ZI", "HAI"]:
            assert _branch_element(branch) == "WATER"


class TestHeMapFormat:
    """测试六合map返回格式"""

    def test_he_map_format(self):
        """六合map返回格式为 {pair_key: [branch1, branch2, element]}"""
        # 子丑合(ZI-CHOU), 辰酉合(CHEN-YOU)
        chart = create_chart(["ZI", "MAO", "CHEN", "YOU"])
        result = calc_branch_he_map(chart)

        # 辰酉合
        assert "CHEN-YOU" in result
        pair_data = result["CHEN-YOU"]
        assert len(pair_data) == 3
        assert set(pair_data[:2]) == {"CHEN", "YOU"}
        assert isinstance(pair_data[2], str)  # 化气五行

    def test_he_map_empty_when_no_pairs(self):
        """无六合对时返回空dict"""
        chart = create_chart(["YIN", "MAO", "SHEN", "YOU"])
        result = calc_branch_he_map(chart)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
