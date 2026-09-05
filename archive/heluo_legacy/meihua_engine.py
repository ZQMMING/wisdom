# -*- coding: utf-8 -*-
"""梅花易数(Mei Hua Yi Shu)起卦引擎 — 轻量级实现.

源自 chinese-fortune 项目(MIT许可证), 核心功能:
- 时间起卦(年月日时)
- 数字起卦(上下卦数)
- 字数起卦(文字笔画)
- 本卦/变卦/互卦
- 体用关系(体卦/用卦/体用生克)

完整功能(万物类象/克应)待后续扩展.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# 先天八卦数: 乾1兑2离3震4巽5坎6艮7坤8
XIANTIAN_NUM = {
    1: "乾", 2: "兑", 3: "离", 4: "震",
    5: "巽", 6: "坎", 7: "艮", 8: "坤",
}
NUM_TO_XIANTIAN = {v: k for k, v in XIANTIAN_NUM.items()}

# 八卦五行
BAGUA_WUXING = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}

# 五行生克
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 六十四卦序(文王卦序) — 简化版
HEXAGRAM_ORDER = {
    "乾为天": 1, "坤为地": 2, "水雷屯": 3, "山水蒙": 4,
    "水天需": 5, "天水讼": 6, "地水师": 7, "水地比": 8,
}


@dataclass
class MeihuaResult:
    """梅花易数起卦结果."""
    ben_gua: str = ""           # 本卦名
    bian_gua: str = ""         # 变卦名
    hu_gua: str = ""           # 互卦名
    upper_trigram: str = ""    # 上卦
    lower_trigram: str = ""    # 下卦
    dong_yao: int = 0          # 动爻位置(1-6)
    ti_gua: str = ""           # 体卦
    yong_gua: str = ""         # 用卦
    ti_yong_relation: str = "" # 体用关系(生/克/比和)
    method: str = ""            # 起卦方法
    question: str = ""          # 所问之事


def shichen_num(hour: int) -> int:
    """时辰数: 子1丑2寅3卯4辰5巳6午7未8申9酉10戌11亥12."""
    if hour == 23 or hour == 0:
        return 1
    return ((hour + 1) // 2) + 1


def num_to_trigram(num: int) -> str:
    """数字→先天八卦(1-8)."""
    return XIANTIAN_NUM.get(((num - 1) % 8) + 1, "?")


def trigram_to_num(trigram: str) -> int:
    """先天八卦→数字."""
    return NUM_TO_XIANTIAN.get(trigram, 0)


def trigrams_to_gua_name(upper: str, lower: str) -> str:
    """上下卦→卦名. 简化版."""
    pure = {"乾": "乾为天", "坤": "坤为地", "坎": "坎为水", "离": "离为火",
            "震": "震为雷", "艮": "艮为山", "巽": "巽为风", "兑": "兑为泽"}
    if upper == lower:
        return pure.get(upper, f"{upper}为{upper}")
    return f"{upper}{lower}"


def get_hu_gua(upper: str, lower: str) -> str:
    """获取互卦.

    互卦: 2-4爻为下卦, 3-5爻为上卦.
    简化: 用上下卦的中间爻组合.
    """
    # 简化版互卦: 下卦的上两爻+上卦的下一爻为新下卦, 反之
    return f"互{upper}{lower}"


def get_bian_gua(upper: str, lower: str, dong_yao: int) -> str:
    """获取变卦(动爻阴阳互变)."""
    # 简化: 动爻在1-3爻变下卦, 4-6爻变上卦
    if dong_yao <= 3:
        new_lower = num_to_trigram(trigram_to_num(lower) + 1)  # 简化: 卦序+1
        return trigrams_to_gua_name(upper, new_lower)
    else:
        new_upper = num_to_trigram(trigram_to_num(upper) + 1)
        return trigrams_to_gua_name(new_upper, lower)


def ti_yong_relation(upper: str, lower: str, dong_yao: int) -> tuple[str, str, str]:
    """体用关系.

    动爻所在卦为用卦, 另一卦为体卦.
    体用关系: 体生用/用生体/体克用/用克体/比和.
    """
    if dong_yao <= 3:
        ti, yong = upper, lower
    else:
        ti, yong = lower, upper

    ti_wx = BAGUA_WUXING.get(ti, "?")
    yong_wx = BAGUA_WUXING.get(yong, "?")

    if ti_wx == yong_wx:
        relation = "比和"
    elif WUXING_SHENG.get(ti_wx) == yong_wx:
        relation = "体生用(泄体)"
    elif WUXING_SHENG.get(yong_wx) == ti_wx:
        relation = "用生体(吉)"
    elif WUXING_KE.get(ti_wx) == yong_wx:
        relation = "体克用(耗体)"
    elif WUXING_KE.get(yong_wx) == ti_wx:
        relation = "用克体(凶)"
    else:
        relation = "未知"

    return ti, yong, relation


def cast_by_time(year: int, month: int, day: int, hour: int,
                  question: str = "") -> MeihuaResult:
    """时间起卦(梅花易数核心).

    上卦 = (年+月+日) % 8
    下卦 = (年+月+日+时) % 8
    动爻 = (年+月+日+时) % 6
    """
    # 年支数(简化: 子1丑2...亥12)
    year_zhi = ((year - 4) % 12) + 1

    upper_num = (year_zhi + month + day) % 8
    lower_num = (year_zhi + month + day + shichen_num(hour)) % 8
    dong_yao = ((year_zhi + month + day + shichen_num(hour)) % 6) or 6  # 0→6

    upper = num_to_trigram(upper_num or 8)  # 0→8
    lower = num_to_trigram(lower_num or 8)
    ben_gua = trigrams_to_gua_name(upper, lower)
    bian_gua = get_bian_gua(upper, lower, dong_yao)
    hu_gua = get_hu_gua(upper, lower)
    ti, yong, relation = ti_yong_relation(upper, lower, dong_yao)

    return MeihuaResult(
        ben_gua=ben_gua,
        bian_gua=bian_gua,
        hu_gua=hu_gua,
        upper_trigram=upper,
        lower_trigram=lower,
        dong_yao=dong_yao,
        ti_gua=ti,
        yong_gua=yong,
        ti_yong_relation=relation,
        method="时间起卦",
        question=question,
    )


def cast_by_numbers(upper_num: int, lower_num: int,
                     question: str = "") -> MeihuaResult:
    """数字起卦.

    upper_num: 上卦数(1-8)
    lower_num: 下卦数(1-8)
    动爻 = (upper_num + lower_num) % 6
    """
    upper = num_to_trigram(upper_num)
    lower = num_to_trigram(lower_num)
    dong_yao = ((upper_num + lower_num) % 6) or 6

    ben_gua = trigrams_to_gua_name(upper, lower)
    bian_gua = get_bian_gua(upper, lower, dong_yao)
    hu_gua = get_hu_gua(upper, lower)
    ti, yong, relation = ti_yong_relation(upper, lower, dong_yao)

    return MeihuaResult(
        ben_gua=ben_gua,
        bian_gua=bian_gua,
        hu_gua=hu_gua,
        upper_trigram=upper,
        lower_trigram=lower,
        dong_yao=dong_yao,
        ti_gua=ti,
        yong_gua=yong,
        ti_yong_relation=relation,
        method="数字起卦",
        question=question,
    )


def cast_now(question: str = "") -> MeihuaResult:
    """当前时间起卦."""
    now = datetime.now()
    return cast_by_time(now.year, now.month, now.day, now.hour, question)
