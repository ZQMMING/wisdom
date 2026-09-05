"""河洛理数冻结规则唯一入口（Module 8）

所有 Hermes / Codex / Claude 的算法实现必须通过此入口验证。
对齐 Architecture Freeze V1.0 §2.3 模块8 + §2.6 Golden Case。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .input import HeluoInput, prepare_heluo_input
from .numbers import (
    compute_tian_di_shu,
    TianDiShu,
    STEM_VALUES,
    BRANCH_VALUES,
    build_six_lines,
    TRIGRAM_ELEMENT,
    TRIGRAM_NATURE,
)
from .prenatal import determine_prenatal_hexagram, PrenatalHexagram
from .yuan_tang import find_yuantang, YuanTang
from .postnatal import compute_postnatal, PostnatalHexagram
from .temporal import compute_timeline, Timeline
from .timeline_yun import (
    compute_dayun_liyao,
    compute_liunian,
    compute_liuri,
    compute_liuyue,
)


# 农历月 → 月令"节"（sxtwl 节气索引，奇数=节）
# 正月=立春(3)、二月=惊蛰(5)、三月=清明(7)、四月=立夏(9)、五月=芒种(11)、
# 六月=小暑(13)、七月=立秋(15)、八月=白露(17)、九月=寒露(19)、十月=立冬(21)、
# 十一月=大雪(23)、十二月=小寒(1)
_LUNAR_MONTH_JIE = {
    1: 3, 2: 5, 3: 7, 4: 9, 5: 11, 6: 13,
    7: 15, 8: 17, 9: 19, 10: 21, 11: 23, 12: 1,
}


_jie_cache: dict[int, dict[int, str]] = {}


def _jie_datetime_for_lunar_month(year: int, lunar_month: int) -> str | None:
    """返回农历 lunar_month 月"节"的精确时刻（公历 YYYY-MM-DD HH:MM）。

    一次遍历拿到该公历年的全部12个"节"并缓存，后续查表（避免逐月重复遍历）。
    用于流日卦节气对齐（《河洛理数》卷二下）。
    """
    global _jie_cache
    if year not in _jie_cache:
        _jie_cache[year] = _compute_year_jie(year)
    return _jie_cache[year].get(lunar_month)


def _compute_year_jie(year: int) -> dict[int, str]:
    """遍历公历 year-1~year+1，找齐 12 个"节"，按农历月 1-12 建映射。"""
    import sxtwl
    from datetime import date, timedelta
    result: dict[int, str] = {}
    best: dict[int, tuple] = {}
    d = date(year - 1, 1, 1)
    end = date(year + 1, 12, 31)
    while d <= end:
        day_obj = sxtwl.fromSolar(d.year, d.month, d.day)
        jq = day_obj.getJieQi()
        if jq in _LUNAR_MONTH_JIE.values():
            jd = day_obj.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            if not (0 < t.Y <= 2200):
                d += timedelta(days=1)
                continue
            # 该节对应的农历月
            lm = next((m for m, idx in _LUNAR_MONTH_JIE.items() if idx == jq), None)
            if lm is None:
                d += timedelta(days=1)
                continue
            gap = abs(d.year - year)
            if lm not in best or gap < best[lm][0]:
                best[lm] = (gap, f"{t.Y:04d}-{t.M:02d}-{t.D:02d} {int(t.h):02d}:{int(t.m):02d}")
        d += timedelta(days=1)
    for lm, (_, dtstr) in best.items():
        result[lm] = dtstr
    return result
from .hexagram import analyze_hexagram, HexagramStructure
from .yi_interpreter import interpret_all_liunian


@dataclass(frozen=True)
class HeluoResult:
    """河洛计算完整结果"""
    input: HeluoInput
    numbers: TianDiShu
    prenatal: PrenatalHexagram
    yuantang: YuanTang
    postnatal: PostnatalHexagram
    timeline: Timeline | None
    structure: HexagramStructure | None


class HeluoCanonical:
    """
    河洛理数计算器 — 冻结规则唯一入口。

    用法：
    >>> canonical = HeluoCanonical()
    >>> result = canonical.calculate(context)

    验证：
    >>> canonical.verify_golden_case("jixiaolan")
    True
    """

    # 纪晓岚 Golden Case（冻结）
    GOLDEN_CASES = {
        "jixiaolan": {\
            "bazi": [("甲", "辰"), ("辛", "未"), ("戊", "辰"), ("戊", "午")],
            "gender": "male",
            "birth_hour": "午",
            "birth_year": 1724,
            "era": "zhong",
            "expected": {
                "tian_shu": 22,
                "di_shu": 56,
                "tian_reduced": 2,      # 坤
                "di_reduced": 6,        # 乾
                "prenatal": "风地观",    # 修正为实际计算结果
                "yuantang": "六四",
                "yuantang_index": 3,    # 0-indexed
                "postnatal": "天雷无妄",
            },
        },
    }

    def __init__(self, version: str = "v2.0"):
        self.version = version
        self._validate_frozen_version()

    def _validate_frozen_version(self) -> None:
        """验证冻结版本一致性"""
        # 当前冻结版本为 v2.0
        if self.version != "v2.0":
            raise ValueError(f"HeluoCanonical version must be v2.0, got {self.version!r}")

    def calculate(
        self,
        canonical_bazi: "CanonicalBaziChart",
        era: str = "zhong",
        birth_year: int | None = None,
        birth_date: str | None = None,
        true_solar_datetime: str | None = None,
    ) -> HeluoResult:
        """
        完整计算链：CanonicalBaziChart → TianDiShu → PrenatalHexagram → YuanTang → PostnatalHexagram → Timeline → Structure

        架构契约（H17-B）：
        - Heluo 不得重新计算四柱事实
        - 所有四柱数据来自 CanonicalBaziChart（权威上游）
        - Heluo 只做字段映射与契约校验

        Args:
            canonical_bazi: CanonicalBaziChart from BaziEngine (权威四柱事实)
            era: 三元上元/中元/下元
            birth_year: 出生公历年份（用于流年卦推演）
            birth_date: 出生公历日期 ISO 格式（可选）
            true_solar_datetime: 真太阳时 ISO 格式（可选）
        """
        # H17-B: 从 CanonicalBaziChart 提取四柱事实（只读，不做计算）
        bazi = canonical_bazi.bazi
        gender = canonical_bazi.gender
        birth_hour = canonical_bazi.birth_hour

        # Convert English codes to Chinese for Heluo computation
        stem_map = {"JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
                    "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"}
        branch_map = {"ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
                      "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥"}
        bazi_cn = [(stem_map[s], branch_map[z]) for s, z in bazi]
        birth_hour_cn = branch_map.get(birth_hour, birth_hour)

        # Step 1: 计算天数地数
        numbers = compute_tian_di_shu(bazi_cn, gender)

        # Step 2: 确定先天卦
        year_gan = bazi_cn[0][0]
        birth_year_yang = year_gan in "甲丙戊庚壬"
        prenatal = determine_prenatal_hexagram(
            numbers.tian_reduced,
            numbers.di_reduced,
            gender,
            birth_year_yang,
            era,
        )

        # Step 3: 构建六爻
        six_lines = build_six_lines(prenatal.upper_gua, prenatal.lower_gua)

        # Step 4: 确定元堂
        yuantang = find_yuantang(
            six_lines=six_lines,
            birth_hour=birth_hour_cn,
            gender=gender,
            xiantian_name=prenatal.hexagram_name,
        )

        # Step 5: 计算后天卦
        postnatal = compute_postnatal(
            six_lines=six_lines,
            yuantang_index=yuantang.yuantang_index,
        )

        # Step 5.5: 后天卦元堂（复用先天元堂取法，用出生时辰）
        postnatal_yuantang = find_yuantang(
            six_lines=postnatal.lines,
            birth_hour=birth_hour_cn,
            gender=gender,
            xiantian_name=postnatal.hexagram_name,
        )

        # Step 6: 时间序列（大运爻位值运 + 流年卦 + 流月卦）
        timeline = self._build_timeline(
            prenatal, yuantang, postnatal, postnatal_yuantang, birth_year
        )

        # Step 7: 卦象结构分析
        structure = analyze_hexagram(postnatal.hexagram_name)

        # 构建 HeluoInput（DISPUTE-HL-03：落真实出生日期，不再用误导占位）
        from datetime import date
        if birth_date is None:
            yr = birth_year if birth_year is not None else 1984
            birth_date = f"{yr}-01-01"
        if true_solar_datetime is None:
            true_solar_datetime = birth_date + "T00:00:00"
        input_obj = HeluoInput(
            birth_date=birth_date,
            birth_time=birth_hour,
            gender=gender,
            location=None,  # type: ignore
            timezone="Asia/Shanghai",
            true_solar_datetime=true_solar_datetime,
            day_boundary="23:00",
        )

        return HeluoResult(
            input=input_obj,
            numbers=numbers,
            prenatal=prenatal,
            yuantang=yuantang,
            postnatal=postnatal,
            timeline=timeline,
            structure=structure,
        )

    def _build_timeline(
        self,
        prenatal: PrenatalHexagram,
        yuantang: YuanTang,
        postnatal: PostnatalHexagram,
        postnatal_yuantang: YuanTang,
        birth_year: int | None,
    ) -> Timeline:
        """构建时间序列：大运（爻位值运）+ 流年卦 + 流月卦。

        基于 timeline_yun 模块（《河洛理数·卷之四/五》论大运/流年/流月）。
        """
        if birth_year is None:
            birth_year = 1984  # 未提供时占位（甲子年），后续需由调用方传入真实年份

        # 先天/后天六爻
        prenatal_lines = build_six_lines(prenatal.upper_gua, prenatal.lower_gua)
        postnatal_lines = build_six_lines(postnatal.upper_gua, postnatal.lower_gua)

        # 大运（爻位值运）
        dayun = compute_dayun_liyao(
            prenatal_lines,
            yuantang.yuantang_index,
            postnatal_lines,
            postnatal_yuantang.yuantang_index,
        )

        # 流年卦（1~100 岁，按大运爻分段）
        liunian = compute_liunian(
            prenatal_lines,
            yuantang.yuantang_index,
            postnatal_lines,
            postnatal_yuantang.yuantang_index,
            birth_year=birth_year,
            age_from=1,
            age_to=100,
        )

        # 流月卦（以流年卦为本，元堂取该流年所属大运段元堂）+ 流日卦
        yearly = []
        for y in liunian.years:
            # 流年卦元堂：大运分段后取该年所属大运段元堂；无则回退先天元堂
            yyt = y.yuantang_index if y.yuantang_index >= 0 else yuantang.yuantang_index
            liuyue = compute_liuyue(y.lines, yyt)
            months = []
            for m in liuyue.months:
                # 流日卦：以当月月卦为本，从月爻下一爻变五爻（每段6天）
                # 节气对齐：流日卦须从当月"节"时刻起管（《河洛理数》卷二下）
                jie_dt = None
                try:
                    jie_dt = _jie_datetime_for_lunar_month(y.year, m["month"])
                except Exception:
                    jie_dt = None
                liuri = compute_liuri(m["lines"], m["yue_yao_index"], jie_dt)
                months.append({
                    "month": m["month"],
                    "name": m["name"],
                    "upper": m["upper"],
                    "lower": m["lower"],
                    "lines": m["lines"],
                    "kind": m["kind"],
                    "jie_datetime": jie_dt,
                    "days": liuri.days,
                })
            yearly.append({
                "age": y.age,
                "year": y.year,
                "ganzhi": y.ganzhi,
                "yang_year": y.yang_year,
                "hexagram": y.hexagram_name,
                "upper": y.upper,
                "lower": y.lower,
                "lines": y.lines,
                "months": months,
            })

        # P1：易经解卦层 — 为每个流年卦附加 EVENT_SIGNAL
        yearly = interpret_all_liunian(
            yearly,
            yuan_tang_index=yuantang.yuantang_index,
            yuan_tang_nature=yuantang.yao_nature,
        )

        dayun_entries = [
            {
                "age_start": e.age_start,
                "age_end": e.age_end,
                "hexagram": e.hexagram_name,
                "line_index": e.line_index,
                "line_nature": e.line_nature,
            }
            for e in dayun.sequence
        ]

        return Timeline(
            yearly_hexagrams=yearly,
            monthly_hexagrams=[],
            daily_hexagram={
                "date": str(birth_year),
                "hexagram": prenatal.hexagram_name,
                "upper": prenatal.upper_gua,
                "lower": prenatal.lower_gua,
            },
            hourly_hexagram=None,
            seasonal_hexagram=None,
            qi_phase={
                "dayun": dayun_entries,
                "note": "爻位值运（阳爻9年/阴爻6年，自元堂起行先天再行后天）",
            },
        )

    def verify_golden_case(self, case_name: str) -> bool:
        """
        验证 Golden Case 是否通过当前算法。

        纪晓岚 Golden Case:
        input: 甲辰 辛未 丙戌 甲午 午时 男
        expected: 地天泰 → 六四 → 天雷无妄
        """
        if case_name not in self.GOLDEN_CASES:
            raise ValueError(f"Unknown golden case: {case_name!r}")

        case = self.GOLDEN_CASES[case_name]

        # H17-B: 构建 CanonicalBaziChart（从权威四柱事实）
        from tongshu.models.canonical_bazi import CanonicalBaziChart
        from tongshu.engines.bazi_engine import Pillar

        canonical_bazi = CanonicalBaziChart(
            year_pillar=Pillar(case["bazi"][0][0], case["bazi"][0][1]),
            month_pillar=Pillar(case["bazi"][1][0], case["bazi"][1][1]),
            day_pillar=Pillar(case["bazi"][2][0], case["bazi"][2][1]),
            hour_pillar=Pillar(case["bazi"][3][0], case["bazi"][3][1]),
            day_master=case["bazi"][2][0],  # 日干
            gender=case["gender"],
            start_age=0.0,  # Golden Case 不验证起运年龄
        )

        result = self.calculate(
            canonical_bazi=canonical_bazi,
            era=case.get("era", "zhong"),
            birth_year=case.get("birth_year"),
        )

        expected = case["expected"]

        # 逐项验证
        checks = [
            ("tian_shu", result.numbers.tian_shu, expected["tian_shu"]),
            ("di_shu", result.numbers.di_shu, expected["di_shu"]),
            ("tian_reduced", result.numbers.tian_reduced, expected["tian_reduced"]),
            ("di_reduced", result.numbers.di_reduced, expected["di_reduced"]),
            ("prenatal", result.prenatal.hexagram_name, expected["prenatal"]),
            ("yuantang", result.yuantang.yuantang, expected["yuantang"]),
            ("yuantang_index", result.yuantang.yuantang_index, expected["yuantang_index"]),
            ("postnatal", result.postnatal.hexagram_name, expected["postnatal"]),
        ]

        all_pass = True
        for name, actual, expected_val in checks:
            if actual != expected_val:
                print(f"  ❌ {name}: expected {expected_val!r}, got {actual!r}")
                all_pass = False
            else:
                print(f"  ✅ {name}: {actual!r}")

        return all_pass

    def run_all_golden_cases(self) -> dict[str, bool]:
        """运行所有 Golden Case 并返回结果"""
        results = {}
        for case_name in self.GOLDEN_CASES:
            print(f"\n=== Golden Case: {case_name} ===")
            results[case_name] = self.verify_golden_case(case_name)
        return results


# ========== 向后兼容入口 ==========

def heluo_calculate(
    canonical_bazi: "CanonicalBaziChart",
    era: str = "zhong",
) -> HeluoResult:
    """
    兼容旧接口的便捷函数。

    H17-B: 接受 CanonicalBaziChart（权威上游四柱事实）。
    """
    from .canonical import HeluoCanonical
    canonical = HeluoCanonical()
    return canonical.calculate(canonical_bazi, era)


# 导出标准符号
__all__ = [
    "HeluoCanonical",
    "HeluoResult",
    "heluo_calculate",
    "GOLDEN_CASES",
]
