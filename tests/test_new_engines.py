# -*- coding: utf-8 -*-
"""新增引擎测试: 调候用神/六爻/梅花易数/64卦完整数据."""
import pytest


class TestTiaohouLoader:
    """调候用神加载器测试."""

    def test_loader_available(self):
        from tongshu.engines.tiaohou_loader import is_available, count
        assert is_available() is True
        assert count() == 120

    def test_ji_xu_tiaohou(self):
        """己土戌月调候: 主用神甲丙, 次用神癸."""
        from tongshu.engines.tiaohou_loader import get_tiaohou, get_primary_yongshen, get_secondary_yongshen
        result = get_tiaohou("JI", "XU")
        assert result is not None
        assert result["day_stem"] == "己"
        assert result["month_branch"] == "戌"
        assert get_primary_yongshen("JI", "XU") == ["甲", "丙"]
        assert get_secondary_yongshen("JI", "XU") == ["癸"]

    def test_all_120_combinations(self):
        """验证120组合全部可查询."""
        from tongshu.engines.tiaohou_loader import get_tiaohou
        stems = ["JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI"]
        branches = ["ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"]
        count = 0
        for s in stems:
            for b in branches:
                r = get_tiaohou(s, b)
                assert r is not None, f"{s}{b} not found"
                count += 1
        assert count == 120


class TestGuaFourDimLoader:
    """64卦四维数据加载器测试."""

    def test_loader_available(self):
        from tongshu.engines.yi.gua_four_dim_loader import is_available, count
        assert is_available() is True
        assert count() == 64

    def test_qian_gua(self):
        """乾卦四维数据."""
        from tongshu.engines.yi.gua_four_dim_loader import get_gua_data, get_gua_ci, get_daxiang
        data = get_gua_data("乾为天")
        assert data is not None
        assert get_gua_ci("乾为天") == "元亨利贞。"
        assert "天行健" in get_daxiang("乾为天")

    def test_64hex_complete(self):
        """64卦完整数据(6爻辞)."""
        from tongshu.engines.yi.gua_four_dim_loader import get_64hex, get_yaoci, is_64hex_available
        assert is_64hex_available() is True
        data = get_64hex("乾为天")
        assert data is not None
        assert data["number"] == 1
        assert data["name_zh"] == "乾"
        # 6爻辞
        assert len(data["lines"]) == 6
        assert "潜龙勿用" in get_yaoci("乾为天", 1)
        assert "亢龙有悔" in get_yaoci("乾为天", 6)


class TestLiuYaoEngine:
    """六爻起卦引擎测试."""

    def test_cast_coins_deterministic(self):
        """种子可复现."""
        from tongshu.engines.liuyao_engine import cast_coins
        r1 = cast_coins(seed=42)
        r2 = cast_coins(seed=42)
        assert r1 == r2
        assert len(r1) == 6
        assert all(v in (6, 7, 8, 9) for v in r1)

    def test_cast_result(self):
        """起卦结果结构."""
        from tongshu.engines.liuyao_engine import cast
        result = cast(question="测试", seed=42)
        assert result.ben_gua
        assert result.upper_trigram
        assert result.lower_trigram
        assert len(result.lines) == 6
        assert result.question == "测试"

    def test_dong_yao(self):
        """动爻识别."""
        from tongshu.engines.liuyao_engine import get_dong_yao
        lines = [6, 7, 8, 9, 7, 8]  # 1爻和4爻动
        dong = get_dong_yao(lines)
        assert 1 in dong
        assert 4 in dong

    def test_line_visual(self):
        """爻象可视化."""
        from tongshu.engines.liuyao_engine import line_visual
        lines = [7, 8, 7, 9, 8, 6]
        visual = line_visual(lines)
        assert "━━━" in visual
        assert "━ ━" in visual
        assert "*" in visual  # 动爻标记


class TestMeihuaEngine:
    """梅花易数引擎测试."""

    def test_shichen_num(self):
        """时辰数."""
        from tongshu.engines.meihua_engine import shichen_num
        assert shichen_num(0) == 1   # 子时
        assert shichen_num(23) == 1  # 子时
        assert shichen_num(12) == 7  # 午时

    def test_cast_by_time(self):
        """时间起卦."""
        from tongshu.engines.meihua_engine import cast_by_time
        result = cast_by_time(2025, 6, 15, 12, question="测试")
        assert result.ben_gua
        assert result.upper_trigram
        assert result.lower_trigram
        assert 1 <= result.dong_yao <= 6
        assert result.ti_gua
        assert result.yong_gua
        assert result.ti_yong_relation
        assert result.method == "时间起卦"

    def test_cast_by_numbers(self):
        """数字起卦."""
        from tongshu.engines.meihua_engine import cast_by_numbers
        result = cast_by_numbers(3, 5, question="测试")
        assert result.ben_gua
        assert result.method == "数字起卦"

    def test_ti_yong_relation(self):
        """体用关系."""
        from tongshu.engines.meihua_engine import ti_yong_relation
        ti, yong, relation = ti_yong_relation("乾", "坤", 2)
        assert ti == "乾"  # 动爻在下卦, 上卦为体
        assert yong == "坤"
        assert relation  # 非空


class TestStrengthEngineTiaohou:
    """旺衰引擎调候用神集成测试."""

    def test_strength_result_has_tiaohou(self):
        """旺衰结果包含调候用神字段."""
        from tongshu.engines.bazi_engine import BaziEngine
        from tongshu.engines.strength_engine import evaluate_strength
        engine = BaziEngine()
        chart = engine.compute((1990, 5, 10, 12), gender="male")
        result = evaluate_strength(chart)
        assert hasattr(result, "tiaohou_primary")
        assert hasattr(result, "tiaohou_secondary")
        assert hasattr(result, "tiaohou_wuxing_state")
        assert hasattr(result, "tiaohou_notes")
        assert hasattr(result, "tiaohou_season")
        # 己土戌月(如果是这个组合)
        if result.day_master_element == "EARTH" and result.month_command == "XU":
            assert "甲" in result.tiaohou_primary
            assert "癸" in result.tiaohou_secondary
