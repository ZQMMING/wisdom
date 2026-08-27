# -*- coding: utf-8 -*-
"""调候用神加载器.

数据来源: data/tiaohou/tiaohou.json (源自 chinese-fortune 项目, MIT许可证)
依据: 《穷通宝鉴》调候用神体系, 经现代术数家整理.

120条数据: 10天干 × 12地支 = 120组合.
每条包含: primary_yongshen(主用神) / secondary_yongshen(次用神) /
         wuxing_state(五行状态) / season(季节) / notes(注解) /
         score_modifier_hot_cold(寒热修正系数).

用途: 为旺衰引擎提供调候用神参考, 提升用神精准度.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

# 数据文件路径(相对于backend根目录)
_DATA_PATH = Path("data/tiaohou/tiaohou.json")

# 天干英文→中文映射
_STEM_CN = {
    "JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
    "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸",
}
# 地支英文→中文映射
_BRANCH_CN = {
    "ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
    "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥",
}


@lru_cache(maxsize=1)
def _load_all() -> dict:
    """加载全部调候用神数据(缓存)."""
    if not _DATA_PATH.exists():
        return {}
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tiaohou", {})
    except Exception:
        return {}


def get_tiaohou(day_stem: str, month_branch: str) -> Optional[dict]:
    """获取调候用神数据.

    Args:
        day_stem: 天干(支持英文JIA或中文甲)
        month_branch: 地支(支持英文ZI或中文子)

    Returns:
        包含 day_stem/month_branch/season/wuxing_state/
        primary_yongshen/secondary_yongshen/notes/score_modifier_hot_cold 的字典,
        未找到返回 None.
    """
    data = _load_all()
    if not data:
        return None
    # 统一转为中文
    stem_cn = _STEM_CN.get(day_stem, day_stem)
    branch_cn = _BRANCH_CN.get(month_branch, month_branch)
    key = f"{stem_cn}|{branch_cn}"
    return data.get(key)


def get_primary_yongshen(day_stem: str, month_branch: str) -> list[str]:
    """获取主用神列表."""
    item = get_tiaohou(day_stem, month_branch)
    return item["primary_yongshen"] if item else []


def get_secondary_yongshen(day_stem: str, month_branch: str) -> list[str]:
    """获取次用神列表."""
    item = get_tiaohou(day_stem, month_branch)
    return item["secondary_yongshen"] if item else []


def get_all_yongshen(day_stem: str, month_branch: str) -> list[str]:
    """获取全部用神(主+次)."""
    primary = get_primary_yongshen(day_stem, month_branch)
    secondary = get_secondary_yongshen(day_stem, month_branch)
    return primary + secondary


def get_wuxing_state(day_stem: str, month_branch: str) -> str:
    """获取五行状态描述."""
    item = get_tiaohou(day_stem, month_branch)
    return item["wuxing_state"] if item else ""


def get_notes(day_stem: str, month_branch: str) -> str:
    """获取调候注解."""
    item = get_tiaohou(day_stem, month_branch)
    return item["notes"] if item else ""


def get_season(day_stem: str, month_branch: str) -> str:
    """获取季节描述."""
    item = get_tiaohou(day_stem, month_branch)
    return item["season"] if item else ""


def is_available() -> bool:
    """检查调候用神数据是否可用."""
    return bool(_load_all())


def count() -> int:
    """返回已加载调候组合数."""
    return len(_load_all())
