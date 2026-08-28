# -*- coding: utf-8 -*-
"""古籍引用注册表 (Classical Citations Registry).

借鉴 chinese-fortune 项目的八字解读纪律:
- 严格以《子平真诠》《滴天髓》《穷通宝鉴》《三命通会》《渊海子平》五书为准绳
- 凡古籍无据者不妄断
- 禁套话迎合
- 只出应象最强、可验证性最高的结论

用途: 为断言层提供古籍依据引用, 提升断言可信度.
"""
from __future__ import annotations

# 五大古籍简称
CLASSICS = {
    "ZIPING": "《子平真诠》",
    "DITIAN": "《滴天髓》",
    "QIONGTONG": "《穷通宝鉴》",
    "SANMING": "《三命通会》",
    "YUANHAI": "《渊海子平》",
}

# 旺衰判定古籍依据
STRENGTH_CITATIONS = {
    "de_ling": "《渊海子平·论日为主》: 月令为纲; 《滴天髓·衰旺》: 得令",
    "de_di": "《渊海子平》得地: 地支通根(藏干见比劫印星)",
    "de_shi": "《渊海子平》得势: 天干透比劫印星生扶",
    "month_command": "《子平真诠·论用神》: 月令乃提纲之所在",
    "verdict": "《滴天髓·通神论·衰旺》: 能知衰旺, 真机已达",
    "cong_ge_yinyang": "《滴天髓·顺局》: 五阳从气不从势, 五阴从势无情义",
    "climate": "《穷通宝鉴》调候框架",
}

# 调候用神古籍依据
TIAOHOU_CITATIONS = {
    "primary": "《穷通宝鉴》调候用神: 主用神",
    "secondary": "《穷通宝鉴》调候用神: 次用神(辅助)",
    "wu_xing_state": "《穷通宝鉴》五行状态描述",
}

# 十神判定古籍依据
TEN_GOD_CITATIONS = {
    "zhengguan": "《渊海子平·论正官》: 正官为贵气之星",
    "qisha": "《渊海子平·论七杀》: 七杀乃凶神, 需制化",
    "zhengyin": "《渊海子平·论正印》: 正印为生我之神",
    "pianyin": "《滴天髓》偏印为枭神, 生身不力反夺食",
    "bizijian": "《渊海子平·论比肩》: 比肩为同我之神",
    "jiecai": "《渊海子平·论劫财》: 劫财为夺财之神",
    "shishen": "《渊海子平·论食神》: 食神为我生之神",
    "shangguan": "《渊海子平·论伤官》: 伤官为我生之神, 需制化",
    "zhengcai": "《渊海子平·论正财》: 正财为我克之神",
    "piancai": "《渊海子平·论偏财》: 偏财为我克之神",
}

# 紫微斗数古籍依据
ZIWEI_CITATIONS = {
    "sanfang_sizheng": "倪海厦《天纪》: 看一个宫一定看三方四正与对面",
    "ming_gong": "《紫微斗数全书》: 命宫为一身之主",
    "sihua": "《紫微斗数全书》: 化禄化权化科化忌为四化",
    "dayun": "倪海厦《天纪》: 命好不如限好, 大限(大运)为主",
}

# 盲派命理古籍依据
BLIND_CITATIONS = {
    "binzhu": "盲派口诀: 宾主分明, 我宫他宫",
    "tiyong": "盲派口诀: 体用分明, 体为我用为他",
    "zuogong": "盲派口诀: 做功为用, 做功方式决定成就",
    "yingqi": "盲派应期: 冲穿合三刑墓库开闭为应期",
}

# 河洛理数古籍依据
HELUO_CITATIONS = {
    "xiantian": "《河洛理数》: 先天卦为本命",
    "houtian": "《河洛理数》: 后天卦为运势",
    "yuantang": "《河洛理数》: 元堂为动爻",
    "liunian": "《河洛理数》: 流年卦为当年运势",
}

# 易经古籍依据
YIJING_CITATIONS = {
    "guaci": "《周易》卦辞",
    "yaoci": "《周易》爻辞",
    "daxiang": "《周易·象传》大象",
    "xiaoxiang": "《周易·象传》小象",
    "wenyan": "《周易·文言传》",
}


def get_citation(category: str, key: str) -> str:
    """获取古籍引用.

    Args:
        category: 类别 (STRENGTH/TIAOHOU/TEN_GOD/ZIWEI/BLIND/HELUO/YIJING)
        key: 键名

    Returns:
        古籍引用字符串, 未找到返回空字符串.
    """
    tables = {
        "STRENGTH": STRENGTH_CITATIONS,
        "TIAOHOU": TIAOHOU_CITATIONS,
        "TEN_GOD": TEN_GOD_CITATIONS,
        "ZIWEI": ZIWEI_CITATIONS,
        "BLIND": BLIND_CITATIONS,
        "HELUO": HELUO_CITATIONS,
        "YIJING": YIJING_CITATIONS,
    }
    table = tables.get(category.upper(), {})
    return table.get(key, "")


def get_strength_citation(key: str) -> str:
    """获取旺衰判定古籍引用."""
    return get_citation("STRENGTH", key)


def get_tiaohou_citation(key: str) -> str:
    """获取调候用神古籍引用."""
    return get_citation("TIAOHOU", key)


def get_ten_god_citation(key: str) -> str:
    """获取十神判定古籍引用."""
    return get_citation("TEN_GOD", key)


def get_ziwei_citation(key: str) -> str:
    """获取紫微斗数古籍引用."""
    return get_citation("ZIWEI", key)


def get_blind_citation(key: str) -> str:
    """获取盲派命理古籍引用."""
    return get_citation("BLIND", key)


def get_heluo_citation(key: str) -> str:
    """获取河洛理数古籍引用."""
    return get_citation("HELUO", key)


def get_yijing_citation(key: str) -> str:
    """获取易经古籍引用."""
    return get_citation("YIJING", key)
