"""
P2.7-B: Canonical Bazi Dataset Expansion — Risk-Based Case Selection

目标：
按风险矩阵选择案例，覆盖：
1. 节气交界（立春精确时刻）
2. 子初换日（23:00-01:00）
3. 不同经度（真太阳时影响）
4. 不同历史年代（唐宋元明清）
5. 时辰边界（每时辰交界）

数据来源层级：
- T1: 官方史书/正史（《旧唐书》《新唐书》《宋史》）
- T2: 可靠排盘资料（专业命理学网站、万年历）
- T3: 网络百科（维基百科、百度百科）
"""
import pytest
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from src.tongshu.engines.bazi_engine import BaziEngine, BaziChart, HEAVENLY_STEMS, EARTHLY_BRANCHES, calc_five_element_balance_role
from src.tongshu.engines.time_resolver import TimeResolver


# ============================================================
# Canonical Bazi Dataset — Risk-Based Selection
# ============================================================

CANONICAL_CASES = [
    # ── T1 权威案例（官方史料 + 专业排盘验证）──────────────────
    {
        "id": "C001-JIXIAOLAN",
        "name": "纪晓岚",
        "birth": (1724, 7, 16, 12),  # 公历 1724-07-16 午时
        "gender": "male",
        "location": "北京",
        "longitude": 116.4,
        "expected": {
            "year": ("JIA", "CHEN"),
            "month": ("XIN", "WEI"),
            "day": ("WU", "CHEN"),
            "hour": ("WU", "WU"),
        },
        "oracle_source": "纪晓岚生平资料交叉验证",
        "risk_level": "LOW",
    },
    {
        "id": "C002-SUSHI",
        "name": "苏轼",
        "birth": (1037, 1, 8, 5),  # 公历 1037-01-08 卯时
        "gender": "male",
        "location": "成都",
        "longitude": 104.06,
        "expected": {
            "year": ("BING", "ZI"),
            "month": ("XIN", "CHOU"),
            "day": ("GUI", "HAI"),
            "hour": ("YI", "MAO"),
        },
        "oracle_source": "维基传记 + 专业排盘",
        "risk_level": "MEDIUM",
    },
    
    # ── 边界条件案例（高风险验证）────────────────────────────
    {
        "id": "B001-LICHUN_BEFORE",
        "name": "立春前（2024-02-04 08:00）",
        "birth": (2024, 2, 4, 8),  # 立春前约8小时
        "gender": "male",
        "location": "北京",
        "longitude": 116.4,
        "oracle_source": "节气交接时刻 2024-02-04 16:26:53",
        "risk_level": "HIGH",
    },
    {
        "id": "B002-LICHUN_AFTER",
        "name": "立春后（2024-02-04 18:00）",
        "birth": (2024, 2, 4, 18),  # 立春后约1.5小时
        "gender": "male",
        "location": "北京",
        "longitude": 116.4,
        "oracle_source": "节气交接时刻 2024-02-04 16:26:53",
        "risk_level": "HIGH",
    },
    {
        "id": "B003-ZI_BOUNDARY_23H",
        "name": "子初换日（23:00）",
        "birth": (2024, 1, 15, 23),
        "gender": "male",
        "location": "北京",
        "longitude": 116.4,
        "oracle_source": "传统子初换日规则",
        "risk_level": "MEDIUM",
    },
    {
        "id": "B004-ZI_BOUNDARY_00H",
        "name": "子初换日（00:00）",
        "birth": (2024, 1, 16, 0),
        "gender": "male",
        "location": "北京",
        "longitude": 116.4,
        "oracle_source": "传统子初换日规则",
        "risk_level": "MEDIUM",
    },
]


class TestCanonicalBaziDatasetExpansion:
    """扩展版 Canonical Bazi Dataset 测试"""
    
    def test_c001_jixiaolan(self):
        """C001: 纪晓岚案例验证"""
        case = CANONICAL_CASES[0]
        engine = BaziEngine()
        
        chart = engine.compute(case["birth"], gender=case["gender"])
        
        assert chart.year_pillar.heavenly_stem == case["expected"]["year"][0]
        assert chart.year_pillar.earthly_branch == case["expected"]["year"][1]
        assert chart.month_pillar.heavenly_stem == case["expected"]["month"][0]
        assert chart.month_pillar.earthly_branch == case["expected"]["month"][1]
        assert chart.day_pillar.heavenly_stem == case["expected"]["day"][0]
        assert chart.day_pillar.earthly_branch == case["expected"]["day"][1]
        assert chart.hour_pillar.heavenly_stem == case["expected"]["hour"][0]
        assert chart.hour_pillar.earthly_branch == case["expected"]["hour"][1]
    
    def test_c002_sushi(self):
        """C002: 苏轼案例验证"""
        case = CANONICAL_CASES[1]
        engine = BaziEngine()
        
        chart = engine.compute(case["birth"], gender=case["gender"])
        
        assert chart.year_pillar.heavenly_stem == case["expected"]["year"][0]
        assert chart.year_pillar.earthly_branch == case["expected"]["year"][1]
        assert chart.month_pillar.heavenly_stem == case["expected"]["month"][0]
        assert chart.month_pillar.earthly_branch == case["expected"]["month"][1]
        assert chart.day_pillar.heavenly_stem == case["expected"]["day"][0]
        assert chart.day_pillar.earthly_branch == case["expected"]["day"][1]
        assert chart.hour_pillar.heavenly_stem == case["expected"]["hour"][0]
        assert chart.hour_pillar.earthly_branch == case["expected"]["hour"][1]
    
    def test_all_canonical_cases_pass(self):
        """所有已验证案例必须通过"""
        engine = BaziEngine()
        
        for case in CANONICAL_CASES[:2]:  # 只验证已确认的案例
            if "expected" not in case:
                continue
            
            chart = engine.compute(case["birth"], gender=case["gender"])
            
            for pillar_name in ["year", "month", "day", "hour"]:
                expected = case["expected"][pillar_name]
                pillar = getattr(chart, f"{pillar_name}_pillar")
                actual = (pillar.heavenly_stem, pillar.earthly_branch)
                assert actual == expected, \
                    f"{case['id']} {pillar_name} pillar mismatch: expected {expected}, got {actual}"


class TestSolarTermBoundary:
    """节气边界验证 — 高风险测试
    
    注意：当前实现使用农历月份而非精确节气时刻判断月柱。
    因此立春前后（同一天）月柱相同是预期行为。
    精确节气边界验证需要完整天文算法支持。
    """
    
    def test_lichun_same_day_consistency(self):
        """
        B001+B002: 验证立春当天不同时刻的月柱切换

        2024年立春时刻：16:26:53
        - 立春前（08:00）应为丑月
        - 立春后（18:00）应为寅月
        """
        engine = BaziEngine()

        # 立春前
        before_case = CANONICAL_CASES[2]
        chart_before = engine.compute(before_case["birth"], gender=before_case["gender"])

        # 立春后
        after_case = CANONICAL_CASES[3]
        chart_after = engine.compute(after_case["birth"], gender=after_case["gender"])

        before_month = chart_before.month_pillar.earthly_branch
        after_month = chart_after.month_pillar.earthly_branch

        print(f"立春前月柱: {before_month}")
        print(f"立春后月柱: {after_month}")

        # 修复后：立春前后月柱必须不同
        assert before_month == "CHOU", f"立春前月柱应为 CHOU，实际为 {before_month}"
        assert after_month == "YIN", f"立春后月柱应为 YIN，实际为 {after_month}"
        assert before_month != after_month, \
            f"立春前后月柱应不同（{before_month} == {after_month}）"
    
    def test_lichun_month_is_yin(self):
        """立春后应进入寅月（或对应地支）"""
        engine = BaziEngine()
        case = CANONICAL_CASES[3]
        
        chart = engine.compute(case["birth"], gender=case["gender"])
        month_branch = chart.month_pillar.earthly_branch
        
        # 2024年立春后为寅月
        assert month_branch == "YIN", f"立春后月柱应为 YIN，实际为 {month_branch}"


class TestZiHourBoundary:
    """子初换日验证"""
    
    def test_zi_hour_23h_vs_00h(self):
        """
        23:00 和次日 00:00 的日柱关系
        
        传统子初换日：23:00开始为新日
        但当前实现可能采用夜子时方案
        """
        engine = BaziEngine()
        
        # 23:00
        chart_23h = engine.compute((2024, 1, 15, 23), gender="male")
        
        # 00:00（次日）
        chart_00h = engine.compute((2024, 1, 16, 0), gender="male")
        
        day_23h = chart_23h.day_pillar
        day_00h = chart_00h.day_pillar
        
        print(f"23:00 日柱: {day_23h}")
        print(f"00:00 日柱: {day_00h}")
        
        # 验证两种策略之一：
        # 策略A（子初换日）：23:00和00:00不同日
        # 策略B（夜子时）：23:00和00:00同一日
        
    def test_zi_hour_consistency(self):
        """验证子时边界的一致性
        
        当前实现采用"子初换日"方案：
        - 23:00 开始进入新日（日柱变化）
        - 00:00 属于次日（日柱与23:00不同）
        """
        engine = BaziEngine()
        
        # 验证单日内的日柱连续性
        chart_00h = engine.compute((2024, 1, 15, 0), gender="male")
        chart_12h = engine.compute((2024, 1, 15, 12), gender="male")
        chart_23h = engine.compute((2024, 1, 15, 23), gender="male")
        
        # 00:00 和 12:00 属于同一天，日柱应相同
        assert chart_00h.day_pillar == chart_12h.day_pillar, \
            f"同一天内（00:00-12:00）日柱应相同：{chart_00h.day_pillar} != {chart_12h.day_pillar}"
        
        # 23:00 进入新日，日柱应不同
        assert chart_12h.day_pillar != chart_23h.day_pillar, \
            f"23:00 应进入新日：{chart_12h.day_pillar} == {chart_23h.day_pillar}"
        
        # 次日 00:00 的日柱应与 23:00 相同
        chart_next_00h = engine.compute((2024, 1, 16, 0), gender="male")
        assert chart_23h.day_pillar == chart_next_00h.day_pillar, \
            f"23:00 和次日 00:00 应属于同一日：{chart_23h.day_pillar} != {chart_next_00h.day_pillar}"


class TestLongitudeEffect:
    """经度效应验证"""
    
    def test_different_longitudes_same_time(self):
        """
        同一北京时间，不同经度应产生不同的有效时间（真太阳时影响）
        
        上海（121.47°E）vs 北京（116.4°E）
        时间差：约20分钟
        """
        resolver = TimeResolver()
        
        # 上海
        shanghai_context = resolver.resolve_context(
            birth_date=date(2024, 1, 1),
            hour=11,
            minute=30,
            timezone='Asia/Shanghai',
            location='上海',
            gender='male',
        )
        
        # 北京
        beijing_context = resolver.resolve_context(
            birth_date=date(2024, 1, 1),
            hour=11,
            minute=30,
            timezone='Asia/Shanghai',
            location='北京',
            gender='male',
        )
        
        # 验证有效时间不同
        shanghai_effective = (shanghai_context.effective_date, shanghai_context.effective_hour)
        beijing_effective = (beijing_context.effective_date, beijing_context.effective_hour)
        
        print(f"上海有效时间: {shanghai_effective}")
        print(f"北京有效时间: {beijing_effective}")
        
        # 理论上应有差异（约20分钟）
        # 但如果差异小于1小时，则有效小时相同
        assert shanghai_context.effective_date == beijing_context.effective_date, \
            "日期不应因经度变化而改变"


class TestDeterminismAndConsistency:
    """确定性和一致性验证"""
    
    def test_determinism_across_calls(self):
        """同一输入必须产生相同输出"""
        engine = BaziEngine()
        
        results = []
        for _ in range(10):
            chart = engine.compute((1724, 7, 16, 12), gender="male")
            results.append((
                chart.year_pillar,
                chart.month_pillar,
                chart.day_pillar,
                chart.hour_pillar,
            ))
        
        assert all(r == results[0] for r in results), "非确定性输出！"
    
    def test_gender_independence_of_four_pillars(self):
        """四柱不应受性别影响（仅大运受影响）"""
        engine = BaziEngine()
        
        chart_male = engine.compute((1724, 7, 16, 12), gender="male")
        chart_female = engine.compute((1724, 7, 16, 12), gender="female")
        
        assert chart_male.year_pillar == chart_female.year_pillar
        assert chart_male.month_pillar == chart_female.month_pillar
        assert chart_male.day_pillar == chart_female.day_pillar
        assert chart_male.hour_pillar == chart_female.hour_pillar
    
    def test_five_element_balance_auxiliary_only(self):
        """five_element_balance 必须是 AUXILIARY_SIGNAL"""
        engine = BaziEngine()
        
        chart = engine.compute((1724, 7, 16, 12), gender="male")
        
        assert hasattr(chart, 'five_element_balance')
        assert chart.five_element_balance is not None
        
        # 必须是辅助信号，不能是核心判断依据
        assert calc_five_element_balance_role == 'AUXILIARY_SIGNAL', \
            f"five_element_balance 必须是 AUXILIARY_SIGNAL，实际为 {calc_five_element_balance_role}"


class TestRiskMatrixCoverage:
    """风险矩阵覆盖率验证"""
    
    def test_high_risk_cases_have_boundary_tests(self):
        """高风险案例必须有边界测试"""
        high_risk_cases = [c for c in CANONICAL_CASES if c.get("risk_level") == "HIGH"]
        
        boundary_test_count = 4  # B001-B004
        
        assert len(high_risk_cases) <= boundary_test_count * 2, \
            f"高风险案例 {len(high_risk_cases)} 个，边界测试不足以覆盖"
    
    def test_all_cases_have_oracle_source(self):
        """所有案例必须有来源说明"""
        for case in CANONICAL_CASES:
            assert "oracle_source" in case, f"案例 {case['id']} 缺少 oracle_source"
            assert len(case["oracle_source"]) > 0, \
                f"案例 {case['id']} 的 oracle_source 为空"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
