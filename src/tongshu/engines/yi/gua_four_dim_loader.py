# -*- coding: utf-8 -*-
"""64卦四维验证数据加载器.

数据来源: data/research/64gua_4dim_validation.json
四维结构:
  dim1_gua_ci   — 卦辞(经典原文)
  dim1_daxiang  — 大象传(经典原文)
  dim2_baihua   — 白话解读(现代解读)
  dim3_renjian  — 人间道(倪海厦人间道指引)
  dim3_bushi    — 占卜道(倪海厦占卜道指引)

用途: 为河洛/易经断言层提供深度卦象解读依据,
      避免只输出卦名而无实质内容.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional


# 数据文件路径(相对于backend根目录)
_DATA_PATH = Path("data/research/64gua_4dim_validation.json")
_64HEX_PATH = Path("data/tiaohou/64hex.json")  # 64卦完整数据(6爻辞/用九/二进制)


@lru_cache(maxsize=1)
def _load_all() -> dict[str, dict]:
    """加载全部64卦四维数据(缓存)."""
    if not _DATA_PATH.exists():
        return {}
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {item["name"]: item for item in data}
    except Exception:
        return {}


def get_gua_data(hexagram_name: str) -> Optional[dict]:
    """获取单卦四维数据.

    Args:
        hexagram_name: 卦名, 如 "乾为天" / "坤为地"

    Returns:
        包含 dim1_gua_ci/dim1_daxiang/dim2_baihua/dim3_renjian/dim3_bushi 的字典,
        未找到返回 None.
    """
    data = _load_all()
    # 精确匹配
    if hexagram_name in data:
        return data[hexagram_name]
    # 模糊匹配: 去掉"为"字, 如 "乾为天" → "乾天"
    simplified = hexagram_name.replace("为", "")
    for name, item in data.items():
        if name.replace("为", "") == simplified:
            return item
    return None


def get_gua_ci(hexagram_name: str) -> str:
    """获取卦辞(dim1)."""
    item = get_gua_data(hexagram_name)
    return item["dim1_gua_ci"] if item else ""


def get_daxiang(hexagram_name: str) -> str:
    """获取大象传(dim1)."""
    item = get_gua_data(hexagram_name)
    return item["dim1_daxiang"] if item else ""


def get_baihua(hexagram_name: str, max_len: int = 200) -> str:
    """获取白话解读(dim2), 可截断."""
    item = get_gua_data(hexagram_name)
    if not item:
        return ""
    text = item["dim2_baihua"]
    return text[:max_len] + "…" if len(text) > max_len else text


def get_renjian(hexagram_name: str, max_len: int = 150) -> str:
    """获取人间道指引(dim3), 可截断."""
    item = get_gua_data(hexagram_name)
    if not item:
        return ""
    text = item["dim3_renjian"]
    return text[:max_len] + "…" if len(text) > max_len else text


def get_bushi(hexagram_name: str, max_len: int = 150) -> str:
    """获取占卜道指引(dim3), 可截断."""
    item = get_gua_data(hexagram_name)
    if not item:
        return ""
    text = item["dim3_bushi"]
    return text[:max_len] + "…" if len(text) > max_len else text


def build_gua_summary(hexagram_name: str, include_renjian: bool = False) -> str:
    """构建卦象摘要(用于断言mechanism字段).

    格式: 卦名: 卦辞 | 大象传 | 白话解读
    若 include_renjian=True, 追加人间道指引.
    """
    item = get_gua_data(hexagram_name)
    if not item:
        return f"{hexagram_name}(无四维数据)"
    parts = [
        f"{hexagram_name}",
        f"卦辞: {item['dim1_gua_ci']}",
        f"大象: {item['dim1_daxiang']}",
    ]
    baihua = item["dim2_baihua"]
    if len(baihua) > 100:
        baihua = baihua[:100] + "…"
    parts.append(f"解读: {baihua}")
    if include_renjian:
        renjian = item["dim3_renjian"]
        if len(renjian) > 80:
            renjian = renjian[:80] + "…"
        parts.append(f"人间道: {renjian}")
    return " | ".join(parts)


def is_available() -> bool:
    """检查四维数据是否可用."""
    return bool(_load_all())


def count() -> int:
    """返回已加载卦数."""
    return len(_load_all())


# ═══════════════════════════════════════════════════════════════════
# 64卦完整数据(6爻辞/用九/二进制) — 源自 chinese-fortune MIT
# ═══════════════════════════════════════════════════════════════════

@lru_cache(maxsize=1)
def _load_64hex() -> dict[str, dict]:
    """加载64卦完整数据(缓存)."""
    if not _64HEX_PATH.exists():
        return {}
    try:
        with open(_64HEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        hexagrams = data.get("hexagrams", [])
        # 按卦名建索引(支持单字"乾"和双字"乾为天")
        result = {}
        for h in hexagrams:
            name = h.get("name_zh", "")
            if name:
                result[name] = h
                # 也支持"X为Y"格式
                if len(name) == 1:
                    # 简单映射: 乾→乾为天, 坤→坤为地, 等等
                    full_names = {
                        "乾": "乾为天", "坤": "坤为地", "屯": "水雷屯", "蒙": "山水蒙",
                        "需": "水天需", "讼": "天水讼", "师": "地水师", "比": "水地比",
                        "小畜": "风天小畜", "履": "天泽履", "泰": "地天泰", "否": "天地否",
                        "同人": "天火同人", "大有": "火天大有", "谦": "地山谦", "豫": "雷地豫",
                        "随": "泽雷随", "蛊": "山风蛊", "临": "地泽临", "观": "风地观",
                        "噬嗑": "火雷噬嗑", "贲": "山火贲", "剥": "山地剥", "复": "地雷复",
                        "无妄": "天雷无妄", "大畜": "山天大畜", "颐": "山雷颐", "大过": "泽风大过",
                        "坎": "坎为水", "离": "离为火", "咸": "泽山咸", "恒": "雷风恒",
                        "遁": "天山遁", "大壮": "雷天大壮", "晋": "火地晋", "明夷": "地火明夷",
                        "家人": "风火家人", "睽": "火泽睽", "蹇": "水山蹇", "解": "雷水解",
                        "损": "山泽损", "益": "风雷益", "夬": "泽天夬", "姤": "天风姤",
                        "萃": "泽地萃", "升": "地风升", "困": "泽水困", "井": "水风井",
                        "革": "泽火革", "鼎": "火风鼎", "震": "震为雷", "艮": "艮为山",
                        "渐": "风山渐", "归妹": "雷泽归妹", "丰": "雷火丰", "旅": "火山旅",
                        "巽": "巽为风", "兑": "兑为泽", "涣": "风水涣", "节": "水泽节",
                        "中孚": "风泽中孚", "小过": "雷山小过", "既济": "水火既济", "未济": "火水未济",
                    }
                    full = full_names.get(name, f"{name}为{name}")
                    result[full] = h
        return result
    except Exception:
        return {}


def get_64hex(hexagram_name: str) -> Optional[dict]:
    """获取64卦完整数据(含6爻辞/用九/二进制).

    Args:
        hexagram_name: 卦名(支持"乾"/"乾为天"/"水雷屯"等格式)

    Returns:
        包含 number/name_zh/pinyin/name_en/upper_trigram/lower_trigram/
        binary/judgment/image/lines/use_nine/summary_zh 的字典,
        未找到返回 None.
    """
    data = _load_64hex()
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


def get_yaoci(hexagram_name: str, position: int) -> str:
    """获取指定爻辞(1-6).

    Args:
        hexagram_name: 卦名
        position: 爻位(1=初爻, 6=上爻)

    Returns:
        爻辞文本, 未找到返回空字符串.
    """
    item = get_64hex(hexagram_name)
    if not item:
        return ""
    lines = item.get("lines", [])
    for line in lines:
        if line.get("position") == position:
            return line.get("text", "")
    return ""


def get_all_yaoci(hexagram_name: str) -> list[dict]:
    """获取全部6爻辞列表."""
    item = get_64hex(hexagram_name)
    return item.get("lines", []) if item else []


def get_use_jiu(hexagram_name: str) -> str:
    """获取用九/用六(仅乾坤两卦有)."""
    item = get_64hex(hexagram_name)
    return item.get("use_nine", "") if item else ""


def get_binary(hexagram_name: str) -> str:
    """获取卦象二进制(1=阳爻, 0=阴爻, 从上到下)."""
    item = get_64hex(hexagram_name)
    return item.get("binary", "") if item else ""


def get_64hex_summary(hexagram_name: str) -> str:
    """获取64卦中文摘要."""
    item = get_64hex(hexagram_name)
    return item.get("summary_zh", "") if item else ""


def is_64hex_available() -> bool:
    """检查64卦完整数据是否可用."""
    return bool(_load_64hex())


def count_64hex() -> int:
    """返回已加载64卦完整数据卦数."""
    return len(_load_64hex())
