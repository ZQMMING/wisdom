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


# ========== 势()函数：某五行在全局的势力（F1-F4用） ==========

BENQI = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
         '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'}

DANG_LING = 1.5  # 当令加权超参，固定不调
TOU_GAN = 0.5    # 天干每透一干加权


def _canggan_wuxing_count(branch: str, target_wx: str, all_branches: list = None, is_month: bool = False, stems: list = None) -> float:
    """某支中某五行的残量（复用藏干表）
    若all_branches提供，则检查冲归零（与root_qi同口径）
    is_month=True时不做冲归零（月令为提纲，即使被冲仍当令）
    合会优先级高于冲：若该支参与合化且化神=target_wx，则不归零
    """
    # 先检查合会：若该支参与合化且化神=目标五行，则不归零
    if all_branches and stems:
        hua_wx = _get_hehua_branch(branch, all_branches, stems)
        if hua_wx == target_wx:
            # 合化成立且化神=目标五行→该支不被冲归零
            pass
        else:
            # 无合化或化神不对，正常做冲归零检查
            if not is_month:
                for other in all_branches:
                    if _is_chong(branch, other):
                        return 0.0  # 被冲→归零
    else:
        # 冲归零检查（与root_qi同口径；月支除外）
        if all_branches and not is_month:
            for other in all_branches:
                if _is_chong(branch, other):
                    return 0.0  # 被冲→归零

    canggan = BRANCH_CANGGAN[branch]
    total = 0.0
    for level_idx, stem in enumerate(canggan):
        if not stem:
            continue
        if STEM_WUXING[stem] == target_wx:
            if level_idx == 0:
                total += 1.0
            else:
                total += 0.5
    return total


def shi(branches: list, stems: list, target_wx: str, month_branch: str) -> float:
    """
    某五行在全局的势力（用于判「往哪边从」）
    与root_qi共用同一张藏干表+冲归零口径
    月支例外：月令为提纲，不做冲归零
    合会优先级高于冲：合化成立且化神=目标五行时不归零
    """
    s = 0.0
    for i, b in enumerate(branches):
        is_m = (b == month_branch)  # 标记是否月支
        s += _canggan_wuxing_count(b, target_wx, branches, is_month=is_m, stems=stems)

    # 当令加权
    if BENQI.get(month_branch, "") == target_wx:
        s *= DANG_LING

    # 透干加权
    tou_count = sum(1 for stem in stems if STEM_WUXING.get(stem, "") == target_wx)
    s += TOU_GAN * tou_count

    return s


def test_shi():
    """测试势函数"""
    # C1: 癸巳 乙卯 己亥 癸酉
    # 木势：卯本气1.0 + 亥中甲余气0.5 = 1.5；卯月当令×1.5=2.25；透乙+0.5=2.75
    mu_shi = shi(["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"], "木", "卯")
    print(f"C1木势: {mu_shi:.2f}")

    # 水势：子？不对，是亥子...巳中无，卯中无，亥中壬本气1.0，酉中无
    # 透癸×2 +1.0 = 2.0
    shui_shi = shi(["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"], "水", "卯")
    print(f"C1水势: {shui_shi:.2f}")

    # 金势：酉本气1.0，巳中庚余气0.5 = 1.5；不透金
    jin_shi = shi(["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"], "金", "卯")
    print(f"C1金势: {jin_shi:.2f}")

    print(f"\nC1最大势: 木={mu_shi:.2f} / 水={shui_shi:.2f} / 金={jin_shi:.2f}")
    print("预期：木（官杀）势最大→从杀")


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
    print("\n--- 势函数测试 ---")
    test_shi()
