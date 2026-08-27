"""河洛后天卦计算模块（Module 5）

负责：后天卦计算（两步法：元堂爻变 + 内外卦互换）
冻结规则依据：Architecture Freeze V1.0 §2.3 模块5

六爻表示：与原典参考实现一致
  - 1 = 阳爻
  - -1 = 阴爻
  - 变爻：1→-1, -1→1
"""

from __future__ import annotations

from dataclasses import dataclass

from .numbers import SIXTY_FOUR_HEXAGRAMS, TRIGRAM_LINES


@dataclass(frozen=True)
class PostnatalHexagram:
    """后天卦结果"""
    hexagram_name: str       # 后天卦名
    upper_gua: str           # 后天卦上卦
    lower_gua: str           # 后天卦下卦
    lines: list[int]         # 变爻后的六爻
    step1_hexagram: str      # 第一步结果（元堂爻变后）
    step2_hexagram: str      # 第二步结果（内外卦互换后）


def compute_postnatal(
    six_lines: list[int],
    yuantang_index: int,
) -> PostnatalHexagram:
    """
    计算后天卦（C-08，两步法，冻结于 Canonical V2.0）

    算法：
    1. 取元堂爻位（0-5），翻转该爻的阴阳（1→-1, -1→1）
    2. 上下卦互换（外卦入内，内卦出外）

    纪晓岚 Golden Case 验证：
    地天泰 → 元堂六四 → 第一步：雷天大壮 → 第二步：天雷无妄
    """
    if len(six_lines) != 6:
        raise ValueError(f"six_lines must have 6 elements, got {len(six_lines)}")
    if not (0 <= yuantang_index <= 5):
        raise ValueError(f"yuantang_index must be 0-5, got {yuantang_index}")

    # 第一步：元堂爻变（1↔-1）
    step1_lines = six_lines.copy()
    step1_lines[yuantang_index] = -step1_lines[yuantang_index]

    # 提取上下卦（自下而上）
    step1_lower = step1_lines[:3]  # 初、二、三爻
    step1_upper = step1_lines[3:]  # 四、五、上爻

    # 转换为卦名
    step1_lower_name = _lines_to_trigram(step1_lower)
    step1_upper_name = _lines_to_trigram(step1_upper)
    step1_name = SIXTY_FOUR_HEXAGRAMS.get((step1_upper_name, step1_lower_name), "?")

    # 第二步：内外卦互换
    # 原内卦（下卦）变外卦，原外卦（上卦）变内卦
    final_lower = step1_upper   # 原上卦变下卦
    final_upper = step1_lower   # 原下卦变上卦

    final_lower_name = _lines_to_trigram(final_lower)
    final_upper_name = _lines_to_trigram(final_upper)
    final_name = SIXTY_FOUR_HEXAGRAMS.get((final_upper_name, final_lower_name), "?")

    return PostnatalHexagram(
        hexagram_name=final_name,
        upper_gua=final_upper_name,
        lower_gua=final_lower_name,
        lines=step1_lines,
        step1_hexagram=step1_name,
        step2_hexagram=final_name,
    )


def _lines_to_trigram(lines: list[int]) -> str:
    """三爻数组 → 八卦名"""
    key = tuple(lines)
    for name, triline in TRIGRAM_LINES.items():
        if triline == key:
            return name
    return "?"


# 向后兼容
resolve_yuantang = None  # alias in yuan_tang module
