# -*- coding: utf-8 -*-
"""傅佩荣64卦多维度断言加载器.

数据来源: data/tiaohou/fupeirong_64gua_dimensions.json
源自: 傅佩荣《Book-of-Changes》64卦解读 (github.com/fortune-fun/Book-of-Changes)

8个维度:
- fortune(时运)
- wealth(财运)
- home(家宅)
- career(事业)
- marriage(婚恋)
- health(疾病)
- lawsuit(诉讼)
- travel(出行)

每条断言关联爻位(yao), 可按爻位查询.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

# 数据文件路径
_DATA_PATH = Path("data/tiaohou/fupeirong_64gua_dimensions.json")

# 维度中文名
DIMENSION_NAMES = {
    "fortune": "时运",
    "wealth": "财运",
    "home": "家宅",
    "career": "事业",
    "marriage": "婚恋",
    "health": "疾病",
    "lawsuit": "诉讼",
    "travel": "出行",
}


@lru_cache(maxsize=1)
def _load_all() -> dict:
    """加载全部傅佩荣64卦多维度断言(缓存)."""
    if not _DATA_PATH.exists():
        return {}
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 按卦名建索引
        gua_map = {}
        for g in data.get("gua", []):
            name = g.get("name", "")
            if name:
                gua_map[name] = g
                # 也支持"X为Y"格式
                if len(name) <= 2:
                    # 简单映射
                    full_names = {
                        "乾": "乾为天", "坤": "坤为地", "坎": "坎为水", "离": "离为火",
                        "震": "震为雷", "艮": "艮为山", "巽": "巽为风", "兑": "兑为泽",
                    }
                    full = full_names.get(name, f"{name}为{name}")
                    gua_map[full] = g
        return gua_map
    except Exception:
        return {}


def get_gua(hexagram_name: str) -> Optional[dict]:
    """获取单卦多维度断言数据.

    Args:
        hexagram_name: 卦名(支持"乾"/"乾为天"/"水雷屯"等格式)

    Returns:
        包含 name/number/symbol/gua_ci/dimensions 的字典,
        未找到返回 None.
    """
    data = _load_all()
    if not data:
        return None
    # 精确匹配
    if hexagram_name in data:
        return data[hexagram_name]
    # 去掉"为"字匹配
    simplified = hexagram_name.replace("为", "")
    for name, item in data.items():
        if name.replace("为", "") == simplified:
            return item
    return None


def get_dimension(hexagram_name: str, dimension: str) -> list[dict]:
    """获取指定卦的指定维度断言列表.

    Args:
        hexagram_name: 卦名
        dimension: 维度(fortune/wealth/home/career/marriage/health/lawsuit/travel)

    Returns:
        断言列表, 每项含 yao(爻位) 和 text(断言文本).
    """
    gua = get_gua(hexagram_name)
    if not gua:
        return []
    return gua.get("dimensions", {}).get(dimension, [])


def get_fortune(hexagram_name: str) -> list[dict]:
    """获取时运断言."""
    return get_dimension(hexagram_name, "fortune")


def get_wealth(hexagram_name: str) -> list[dict]:
    """获取财运断言."""
    return get_dimension(hexagram_name, "wealth")


def get_home(hexagram_name: str) -> list[dict]:
    """获取家宅断言."""
    return get_dimension(hexagram_name, "home")


def get_career(hexagram_name: str) -> list[dict]:
    """获取事业断言."""
    return get_dimension(hexagram_name, "career")


def get_marriage(hexagram_name: str) -> list[dict]:
    """获取婚恋断言."""
    return get_dimension(hexagram_name, "marriage")


def get_health(hexagram_name: str) -> list[dict]:
    """获取疾病断言."""
    return get_dimension(hexagram_name, "health")


def get_lawsuit(hexagram_name: str) -> list[dict]:
    """获取诉讼断言."""
    return get_dimension(hexagram_name, "lawsuit")


def get_all_dimensions_summary(hexagram_name: str, max_per_dim: int = 1) -> dict[str, str]:
    """获取指定卦的所有维度摘要(每维度取前N条).

    Args:
        hexagram_name: 卦名
        max_per_dim: 每维度最多取几条

    Returns:
        {维度名: 断言文本} 字典.
    """
    gua = get_gua(hexagram_name)
    if not gua:
        return {}
    result = {}
    for dim, items in gua.get("dimensions", {}).items():
        cn_name = DIMENSION_NAMES.get(dim, dim)
        texts = [item["text"] for item in items[:max_per_dim]]
        result[cn_name] = "；".join(texts)
    return result


def build_advice_from_gua(hexagram_name: str, topics: list[str] | None = None) -> str:
    """从卦象多维度断言构建建议文本.

    Args:
        hexagram_name: 卦名
        topics: 关注的主题列表(如["wealth", "career"]), None=全部

    Returns:
        建议文本.
    """
    gua = get_gua(hexagram_name)
    if not gua:
        return ""
    dims = gua.get("dimensions", {})
    if topics:
        dims = {k: v for k, v in dims.items() if k in topics}
    parts = []
    for dim, items in dims.items():
        cn_name = DIMENSION_NAMES.get(dim, dim)
        if items:
            # 取第一条(通常是总述)
            text = items[0]["text"]
            parts.append(f"{cn_name}: {text}")
    return "；".join(parts)


def is_available() -> bool:
    """检查傅佩荣64卦多维度断言数据是否可用."""
    return bool(_load_all())


def count_gua() -> int:
    """返回已加载卦数."""
    return len(_load_all())


def count_dimensions() -> dict[str, int]:
    """返回各维度断言总数."""
    data = _load_all()
    stats = {}
    for gua in data.values():
        for dim, items in gua.get("dimensions", {}).items():
            stats[dim] = stats.get(dim, 0) + len(items)
    return stats
