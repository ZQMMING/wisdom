# -*- coding: utf-8 -*-
"""河洛理数 + 易经 综合接入层 (V1.0)

将河洛理数流年卦与易经卦象吉凶接入紫微断事层的事件预测。

能力:
  - get_liunian_gua: 对某出生信息 + 目标年份, 计算河洛流年卦(名/上下卦/干支/年龄)
  - gua_direction:  由流年卦上下卦五行生克判定当年吉凶方向(易经体用)
  - heluo_yi_dir:   综合返回当年方向信号(吉/凶/平)供事件评分修正

依据:
  - 《河洛理数·卷之四/五》流年卦推演 (timeline_yun.compute_liunian)
  - 易经体用五行生克: 用生体吉/用克体凶/比和吉/体克用中平/体生用泄

河洛流年卦的"体用"取象: 下卦为体(命主自身), 上卦为用(当年外部环境).
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from lunar_python import Solar

from tongshu.engines.heluo import HeluoCanonical

# ── 八卦五行 ───────────────────────────────────────────────
TRIGRAM_ELEMENT = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}

# 五行生克关系: 生我(母) / 我生(子) / 克我(官) / 我克(财)
WOOD, FIRE, EARTH, METAL, WATER = "木", "火", "土", "金", "水"
SHENG = {WOOD: FIRE, FIRE: EARTH, EARTH: METAL, METAL: WATER, WATER: WOOD}   # 木生火...
KE = {WOOD: EARTH, EARTH: WATER, WATER: FIRE, FIRE: METAL, METAL: WOOD}      # 木克土...


def _year_gan(year: int) -> str:
    return "甲乙丙丁戊己庚辛壬癸"[(year - 4) % 10]


def get_bazi(solar_y: int, solar_m: int, solar_d: int, hour: int) -> list[tuple[str, str]]:
    """阳历生日+小时(0-23) -> 四柱干支 [年柱, 月柱, 日柱, 时柱]."""
    solar = Solar.fromYmdHms(solar_y, solar_m, solar_d, hour, 0, 0)
    lunar = solar.getLunar()
    gzs = [lunar.getYearInGanZhi(), lunar.getMonthInGanZhi(),
           lunar.getDayInGanZhi(), lunar.getTimeInGanZhi()]
    return [(g[0], g[1]) for g in gzs]


def get_liunian_gua(
    birth_y: int, birth_m: int, birth_d: int, hour: int,
    gender: str, target_year: int,
) -> Optional[dict]:
    """河洛流年卦: 对出生信息+目标年份返回该年流年卦信息.

    Returns:
        {"year", "ganzhi", "hexagram", "upper", "lower", "age"} | None
    """
    try:
        bazi = get_bazi(birth_y, birth_m, birth_d, hour)
        shi_zhi = bazi[3][1]
        canonical = HeluoCanonical()
        result = canonical.calculate(
            bazi=bazi,
            gender=gender,
            birth_hour=shi_zhi,
            birth_year=birth_y,
            birth_date=f"{birth_y}-{birth_m:02d}-{birth_d:02d}",
        )
        yearly = getattr(result.timeline, "yearly_hexagrams", []) or []
        for y in yearly:
            if y.get("year") == target_year:
                return {
                    "year": y.get("year"),
                    "ganzhi": y.get("ganzhi"),
                    "hexagram": y.get("hexagram"),
                    "upper": y.get("upper"),
                    "lower": y.get("lower"),
                    "age": y.get("age"),
                }
        return None
    except Exception:
        return None


def gua_direction(upper: str, lower: str, hexagram_name: str = "") -> float:
    """流年卦吉凶方向分 (易经体用五行生克 + 卦名意象). -1(凶) ~ +1(吉).

    下卦=体(命主), 上卦=用(当年外部):
      上生下(用生体) → +1.0 吉(得生助)
      比和(同五行)   → +0.5 吉(顺)
      下克上(体克用) →  0.0 中平(克出,耗而可控)
      下生上(体生用) → -0.3 平偏泄(付出)
      上克下(用克体) → -1.0 凶(克入,受制)

    V2: 叠加卦名意象(卦辞吉凶). 卦名主凶(蹇/困/明夷等)则下拉方向,
    主吉(泰/谦/大有等)则上拉方向. 权重各半.
    """
    # 五行生克方向
    e_upper = TRIGRAM_ELEMENT.get(upper)
    e_lower = TRIGRAM_ELEMENT.get(lower)
    wuxing_dir = 0.0
    if e_upper and e_lower:
        if e_upper == e_lower:
            wuxing_dir = 0.5
        elif SHENG.get(e_upper) == e_lower:
            wuxing_dir = 1.0
        elif SHENG.get(e_lower) == e_upper:
            wuxing_dir = -0.3
        elif KE.get(e_lower) == e_upper:
            wuxing_dir = 0.0
        elif KE.get(e_upper) == e_lower:
            wuxing_dir = -1.0

    # 卦名意象方向
    name_dir = 0.0
    if hexagram_name:
        from tongshu.engines.gua_jixiong import gua_name_direction
        name_dir = gua_name_direction(hexagram_name)

    # 综合: 五行与卦名各半, 卦名为0(未收录)时全用五行
    if name_dir == 0.0:
        return wuxing_dir
    return round((wuxing_dir + name_dir) / 2.0, 2)


def heluo_yi_dir(
    birth_y: int, birth_m: int, birth_d: int, hour: int,
    gender: str, target_year: int,
) -> dict:
    """综合返回河洛+易经当年方向信号."""
    gua = get_liunian_gua(birth_y, birth_m, birth_d, hour, gender, target_year)
    if gua is None:
        return {"available": False, "direction": 0.0, "label": "平", "gua": None}
    d = gua_direction(gua["upper"], gua["lower"], gua["hexagram"])
    label = "吉" if d >= 0.5 else ("凶" if d <= -0.5 else "平")
    return {
        "available": True,
        "direction": d,
        "label": label,
        "gua": gua,
    }


def direction_modifier(direction: float, sentiment: str, strength: float = 0.6) -> float:
    """事件评分修正: 用当年吉凶方向修正选项评分.

    sentiment: "positive"/"negative"/"neutral"
    吉年(方向>0) → 正面事件加分, 负面事件减分
    凶年(方向<0) → 负面事件加分, 正面事件减分
    """
    if direction == 0:
        return 0.0
    base = direction * strength
    if sentiment == "positive":
        return base       # 吉年正面加分 / 凶年正面减分
    if sentiment == "negative":
        return -base      # 吉年负面减分 / 凶年负面加分
    return 0.0
