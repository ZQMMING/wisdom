# -*- coding: utf-8 -*-
"""从格族F0总闸"""
import sys
sys.path.insert(0, '.')
from spec.root_qi import calc_root_qi, STEM_WUXING

# 十神：比劫、印星
BI_JIE = {
    "甲": ["甲", "乙"], "乙": ["甲", "乙"],
    "丙": ["丙", "丁"], "丁": ["丙", "丁"],
    "戊": ["戊", "己"], "己": ["戊", "己"],
    "庚": ["庚", "辛"], "辛": ["庚", "辛"],
    "壬": ["壬", "癸"], "癸": ["壬", "癸"],
}

YIN_XING = {
    "甲": ["壬", "癸"], "乙": ["壬", "癸"],
    "丙": ["甲", "乙"], "丁": ["甲", "乙"],
    "戊": ["丙", "丁"], "己": ["丙", "丁"],
    "庚": ["戊", "己"], "辛": ["戊", "己"],
    "壬": ["庚", "辛"], "癸": ["庚", "辛"],
}

# 克我者（官杀，用来克比劫）
GUAN_SHA = {
    "甲": ["庚", "辛"], "乙": ["庚", "辛"],
    "丙": ["壬", "癸"], "丁": ["壬", "癸"],
    "戊": ["甲", "乙"], "己": ["甲", "乙"],
    "庚": ["丙", "丁"], "辛": ["丙", "丁"],
    "壬": ["戊", "己"], "癸": ["戊", "己"],
}

# 我克者（财星，用来克印星）
CAI_XING = {
    "甲": ["戊", "己"], "乙": ["戊", "己"],
    "丙": ["庚", "辛"], "丁": ["庚", "辛"],
    "戊": ["壬", "癸"], "己": ["壬", "癸"],
    "庚": ["甲", "乙"], "辛": ["甲", "乙"],
    "壬": ["丙", "丁"], "癸": ["丙", "丁"],
}


def _is_bi_jie(day_stem: str, stem: str) -> bool:
    return stem in BI_JIE[day_stem]


def _is_yin_xing(day_stem: str, stem: str) -> bool:
    return stem in YIN_XING[day_stem]


def 无气(stems: list, day_stem: str) -> bool:
    """
    天干无比印，或比印被尽除
    stems: [年干, 月干, 日干, 时干]
    """
    # 找所有比劫和印星（除日干外）
    bi_yin_stems = []
    for i, stem in enumerate(stems):
        if i == 2:  # 日干不算
            continue
        if _is_bi_jie(day_stem, stem) or _is_yin_xing(day_stem, stem):
            bi_yin_stems.append((i, stem))

    if not bi_yin_stems:
        return True  # 无比印，无气成立

    # 检查每个比印是否被尽除
    for i, stem in bi_yin_stems:
        # 找邻干（前一个、后一个）
        neighbors = []
        if i > 0:
            neighbors.append(stems[i-1])
        if i < 3:
            neighbors.append(stems[i+1])

        # 比劫：被官杀紧贴克破 → 算尽除
        if _is_bi_jie(day_stem, stem):
            broken = False
            for n in neighbors:
                if n in GUAN_SHA[day_stem]:
                    broken = True
                    break
            if not broken:
                return False  # 有比劫未被克破，有气

        # 印星：被财星紧贴克破 → 算尽除
        if _is_yin_xing(day_stem, stem):
            broken = False
            for n in neighbors:
                if n in CAI_XING[day_stem]:
                    broken = True
                    break
            if not broken:
                return False  # 有印未被财克，有气

    return True  # 所有比印都被尽除


def F0_pass(day_stem: str, branches: list, stems: list) -> bool:
    """
    F0总闸：日主无根无气
    返回 True=通过（可入从格族），False=不通过（退回正格）
    """
    root_qi = calc_root_qi(day_stem, branches, stems)
    wu_qi = 无气(stems, day_stem)
    return (root_qi == 0) and wu_qi


def test():
    """测试用例"""
    # C1: 癸巳 乙卯 己亥 癸酉 → F0=True
    f0 = F0_pass("己", ["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"])
    print(f"C1 F0: {f0} (预期True)")

    # C2: 癸巳 乙卯 己子 癸酉 → F0=False（巳中戊根未被冲）
    f0 = F0_pass("己", ["巳", "卯", "子", "酉"], ["癸", "乙", "己", "癸"])
    print(f"C2 F0: {f0} (预期False)")

    # C3': 庚申 辛酉 甲子 辛未 → F0=False（未中乙余气根）
    f0 = F0_pass("甲", ["申", "酉", "子", "未"], ["庚", "辛", "甲", "辛"])
    print(f"C3' F0: {f0} (预期False)")

    # C4: 庚申 辛酉 甲子 辛丑 → F0=True（丑中无木）
    f0 = F0_pass("甲", ["申", "酉", "子", "丑"], ["庚", "辛", "甲", "辛"])
    print(f"C4 F0: {f0} (预期True)")

    # C5: 庚申 甲申 甲子 乙丑 → F0=False（月干甲比肩帮身）
    f0 = F0_pass("甲", ["申", "申", "子", "丑"], ["庚", "甲", "甲", "乙"])
    print(f"C5 F0: {f0} (预期False，月干甲比肩帮身)")

    # C6: 庚申 甲申 甲子 庚午 → F0=True
    # 月干甲比肩，被年干庚七杀紧贴克破→视为尽除；地支无木根
    f0 = F0_pass("甲", ["申", "申", "子", "午"], ["庚", "甲", "甲", "庚"])
    print(f"C6 F0: {f0} (预期True，月干甲比肩被年干庚紧贴克破)")


if __name__ == "__main__":
    test()
