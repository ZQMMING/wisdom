# -*- coding: utf-8 -*-
"""根气残量表——三族共用单点真相源

专旺型b8：日主有根→加分
化气型b8：日主有根→减项
从格族F0：日主有根→破格
同一张表，三个方向。
"""

# 地支藏干：(本气, 中气, 余气)
BRANCH_CANGGAN = {
    "子": ("癸", "", ""),
    "丑": ("己", "癸", "辛"),
    "寅": ("甲", "丙", "戊"),
    "卯": ("乙", "", ""),
    "辰": ("戊", "乙", "癸"),
    "巳": ("丙", "庚", "戊"),
    "午": ("丁", "己", ""),
    "未": ("己", "丁", "乙"),
    "申": ("庚", "壬", "戊"),
    "酉": ("辛", "", ""),
    "戌": ("戊", "辛", "丁"),
    "亥": ("壬", "甲", ""),
}

# 藏干五行
STEM_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 六冲
LIU_CHONG = [
    ("子", "午"),
    ("丑", "未"),
    ("寅", "申"),
    ("卯", "酉"),
    ("辰", "戌"),
    ("巳", "亥"),
]

# 六合化神
LIUHE_HUA = {
    ("子", "丑"): "土",
    ("寅", "亥"): "木",
    ("卯", "戌"): "火",
    ("辰", "酉"): "金",
    ("巳", "申"): "水",
    ("午", "未"): "火",  # 午未合，一说太阳太阴，此处简化为火土
}

# 三合局
SANHE = [
    (("申", "子", "辰"), "水"),
    (("亥", "卯", "未"), "木"),
    (("寅", "午", "戌"), "火"),
    (("巳", "酉", "丑"), "金"),
]


def _is_chong(b1: str, b2: str) -> bool:
    """判断两支是否相冲"""
    for c1, c2 in LIU_CHONG:
        if (b1 == c1 and b2 == c2) or (b1 == c2 and b2 == c1):
            return True
    return False


def _get_hehua_branch(branch: str, all_branches: list, stems: list) -> str:
    """
    判断该支参与的合化局，返回化神五行（若合而不化返回""）
    合化成立门槛：化神透干（比化气型宽松，只要求透干，不要求当令局全）
    """
    # 先看六合
    for (b1, b2), hua_wx in LIUHE_HUA.items():
        if branch == b1 and b2 in all_branches:
            # 检查化神是否透干
            for stem in stems:
                if STEM_WUXING.get(stem, "") == hua_wx:
                    return hua_wx
            return ""  # 合而不化
        if branch == b2 and b1 in all_branches:
            for stem in stems:
                if STEM_WUXING.get(stem, "") == hua_wx:
                    return hua_wx
            return ""

    # 再三合
    for members, hua_wx in SANHE:
        if branch in members:
            other_two = [b for b in members if b != branch]
            if all(b in all_branches for b in other_two):
                # 三合局全
                for stem in stems:
                    if STEM_WUXING.get(stem, "") == hua_wx:
                        return hua_wx
                return ""  # 合而不化

    return ""  # 无合


def calc_root_qi(day_stem: str, branches: list, stems: list) -> float:
    """
    计算日主根气残量总和

    参数：
        day_stem: 日干（如"己"）
        branches: 四支列表（如["巳","卯","亥","酉"]）
        stems: 四天干列表（如["癸","乙","己","癸"]）

    返回：
        根气残量总和（0~4之间）
        0 = 完全无根 → F0总闸通过（从格可成）
        >0 = 有根 → F0总闸不通过（不从）
    """
    day_wx = STEM_WUXING[day_stem]
    total = 0.0

    for i, branch in enumerate(branches):
        # 1. 基础残量：本气=1，中气=0.5，余气=0.5
        canggan = BRANCH_CANGGAN[branch]
        for level_idx, stem in enumerate(canggan):
            if not stem:
                continue
            stem_wx = STEM_WUXING[stem]
            if stem_wx != day_wx:
                continue  # 不是日主同五行，不计根

            if level_idx == 0:
                base = 1.0
            else:
                base = 0.5

            # 2. 冲修正：该支与任何一支相冲 → 残量归零
            chong = False
            for j, other in enumerate(branches):
                if i != j and _is_chong(branch, other):
                    chong = True
                    break
            if chong:
                continue  # 归零

            # 3. 合化修正
            hua_wx = _get_hehua_branch(branch, branches, stems)
            if hua_wx:
                # 合化成立
                if hua_wx == day_wx:
                    # 化神=日主五行 → 反得助，×1.5
                    total += base * 1.5
                else:
                    # 化神≠日主五行 → 根被夺，归零
                    continue
            else:
                # 无合化或合而不化 → 保留残量
                total += base

    return total


def test():
    """测试用例"""
    # C1: 癸巳 乙卯 己亥 癸酉
    # 己土日主，巳中戊余气0.5，巳亥冲→归零
    qi = calc_root_qi("己", ["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"])
    print(f"C1根气: {qi} (预期≈0，巳被亥冲归零)")

    # C2: 癸巳 乙卯 己子 癸酉
    # 己土日主，巳中戊余气0.5，子不冲巳→保留
    qi = calc_root_qi("己", ["巳", "卯", "子", "酉"], ["癸", "乙", "己", "癸"])
    print(f"C2根气: {qi} (预期≈0.5，巳中戊土保留)")

    # C3': 庚申 辛酉 甲子 辛未
    # 甲木日主，未中乙余气0.5，无冲
    qi = calc_root_qi("甲", ["申", "酉", "子", "未"], ["庚", "辛", "甲", "辛"])
    print(f"C3'根气: {qi} (预期≈0.5，未中乙木余气)")

    # C4: 庚申 辛酉 甲子 辛丑
    # 甲木日主，丑中无木→0
    qi = calc_root_qi("甲", ["申", "酉", "子", "丑"], ["庚", "辛", "甲", "辛"])
    print(f"C4根气: {qi} (预期≈0，丑中无木)")


if __name__ == "__main__":
    test()
