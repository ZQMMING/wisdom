# -*- coding: utf-8 -*-
"""盲派 Blind Feature Calculator V1
从 CanonicalBaziChart 自动计算 BlindFeatureSet
四层：L1原子事实 / L2关系特征 / L3结构特征 / L4高阶特征
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════════
# 基础字典
# ═══════════════════════════════════════════════════════════

# 六冲
CHONG_PAIRS = {
    frozenset({'子', '午'}), frozenset({'丑', '未'}),
    frozenset({'寅', '申'}), frozenset({'卯', '酉'}),
    frozenset({'辰', '戌'}), frozenset({'巳', '亥'}),
}

# 六合
HE_PAIRS = {
    frozenset({'子', '丑'}), frozenset({'寅', '亥'}),
    frozenset({'卯', '戌'}), frozenset({'辰', '酉'}),
    frozenset({'巳', '申'}), frozenset({'午', '未'}),
}

# 三刑
XING_GROUPS = [
    {'寅', '巳', '申'},  # 无恩刑
    {'丑', '戌', '未'},  # 恃势刑
    {'辰', '午', '酉', '亥'},  # 自刑
]

# 六穿
CHUAN_PAIRS = {
    frozenset({'子', '未'}), frozenset({'丑', '午'}),
    frozenset({'寅', '巳'}), frozenset({'卯', '辰'}),
    frozenset({'申', '亥'}), frozenset({'酉', '戌'}),
}

# 三合
SANHE_GROUPS = {
    frozenset({'申', '子', '辰'}): '水',
    frozenset({'亥', '卯', '未'}): '木',
    frozenset({'寅', '午', '戌'}): '火',
    frozenset({'巳', '酉', '丑'}): '金',
}

# 三会
SANHUI_GROUPS = {
    frozenset({'寅', '卯', '辰'}): '木',
    frozenset({'巳', '午', '未'}): '火',
    frozenset({'申', '酉', '戌'}): '金',
    frozenset({'亥', '子', '丑'}): '水',
}

# 墓库
MUKU_BRANCHES = {'辰', '戌', '丑', '未'}

# 藏干
BRANCH_HIDDEN = {
    '子': ['癸'], '丑': ['己', '癸', '辛'],
    '寅': ['甲', '丙', '戊'], '卯': ['乙'],
    '辰': ['戊', '乙', '癸'], '巳': ['丙', '庚', '戊'],
    '午': ['丁', '己'], '未': ['己', '丁', '乙'],
    '申': ['庚', '壬', '戊'], '酉': ['辛'],
    '戌': ['戊', '辛', '丁'], '亥': ['壬', '甲'],
}

# 五行
STEM_ELEMENT = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火',
    '戊': '土', '己': '土', '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}
BRANCH_ELEMENT = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# 阴阳
STEM_YINYANG = {
    '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴',
    '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴',
    '壬': '阳', '癸': '阴',
}

# 十神
TEN_GODS = {
    ('木', '木'): '比肩', ('木', '火'): '伤官', ('木', '土'): '正财',
    ('木', '金'): '正官', ('木', '水'): '正印',
    ('火', '火'): '比肩', ('火', '土'): '食神', ('火', '金'): '偏财',
    ('火', '水'): '正官', ('火', '木'): '正印',
    ('土', '土'): '比肩', ('土', '金'): '食神', ('土', '水'): '正财',
    ('土', '木'): '正官', ('土', '火'): '正印',
    ('金', '金'): '比肩', ('金', '水'): '伤官', ('金', '木'): '正财',
    ('金', '火'): '正官', ('金', '土'): '正印',
    ('水', '水'): '比肩', ('水', '木'): '食神', ('水', '火'): '偏财',
    ('水', '土'): '正官', ('水', '金'): '正印',
}

# 五行生克
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}


@dataclass
class BlindFeatureSet:
    """盲派特征集"""
    # L1 原子事实
    year_gz: str = ""
    month_gz: str = ""
    day_gz: str = ""
    hour_gz: str = ""
    day_master: str = ""
    
    # L1 十神
    year_tg: str = ""
    month_tg: str = ""
    hour_tg: str = ""
    
    # L2 关系特征
    chong_pairs: Set[frozenset] = field(default_factory=set)
    he_pairs: Set[frozenset] = field(default_factory=set)
    xing_pairs: Set[frozenset] = field(default_factory=set)
    chuan_pairs: Set[frozenset] = field(default_factory=set)
    sanhe_groups: Set[frozenset] = field(default_factory=set)
    
    # L3 宾主体用
    main_branches: Set[str] = field(default_factory=set)
    guest_branches: Set[str] = field(default_factory=set)
    ti_branches: Set[str] = field(default_factory=set)
    yong_branches: Set[str] = field(default_factory=set)
    
    # L3 墓库
    muku_branches: Set[str] = field(default_factory=set)
    muku_opened: Set[str] = field(default_factory=set)
    
    # L3 做功
    working_branches: Set[str] = field(default_factory=set)
    work_targets: Set[str] = field(default_factory=set)
    work_methods: Set[str] = field(default_factory=set)
    
    # L4 高阶
    zheng_fan_ju: str = "UNDETERMINED"
    zei_bu: str = "UNDETERMINED"
    
    # 原始干支
    all_branches: List[str] = field(default_factory=list)
    all_stems: List[str] = field(default_factory=list)


def calc_features(year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> BlindFeatureSet:
    """从四柱计算BlindFeatureSet"""
    f = BlindFeatureSet()
    f.year_gz = year_gz
    f.month_gz = month_gz
    f.day_gz = day_gz
    f.hour_gz = hour_gz
    
    # 拆干支
    y_gan, y_zhi = year_gz[0], year_gz[1]
    m_gan, m_zhi = month_gz[0], month_gz[1]
    d_gan, d_zhi = day_gz[0], day_gz[1]
    h_gan, h_zhi = hour_gz[0], hour_gz[1]
    
    f.day_master = d_gan
    f.all_stems = [y_gan, m_gan, d_gan, h_gan]
    f.all_branches = [y_zhi, m_zhi, d_zhi, h_zhi]
    
    # L1 十神
    dm_elem = STEM_ELEMENT[d_gan]
    f.year_tg = TEN_GODS.get((dm_elem, STEM_ELEMENT[y_gan]), '')
    f.month_tg = TEN_GODS.get((dm_elem, STEM_ELEMENT[m_gan]), '')
    f.hour_tg = TEN_GODS.get((dm_elem, STEM_ELEMENT[h_gan]), '')
    
    # L2 关系特征
    for i in range(4):
        for j in range(i+1, 4):
            b1, b2 = f.all_branches[i], f.all_branches[j]
            pair = frozenset({b1, b2})
            if pair in CHONG_PAIRS:
                f.chong_pairs.add(pair)
            if pair in HE_PAIRS:
                f.he_pairs.add(pair)
            if pair in CHUAN_PAIRS:
                f.chuan_pairs.add(pair)
    
    # 三刑
    branch_set = set(f.all_branches)
    for group in XING_GROUPS:
        if len(branch_set & group) >= 2:
            for b1 in branch_set & group:
                for b2 in branch_set & group:
                    if b1 != b2:
                        f.xing_pairs.add(frozenset({b1, b2}))
    
    # 三合
    for group, elem in SANHE_GROUPS.items():
        if len(branch_set & group) >= 2:
            f.sanhe_groups.add(group)
    
    # L3 宾主
    f.main_branches = {d_zhi, h_zhi}
    f.guest_branches = {y_zhi, m_zhi}
    
    # L3 体用
    ti_gods = {'比肩', '劫财', '正印', '偏印', '食神', '伤官'}
    yong_gods = {'正财', '偏财', '正官', '七杀'}
    
    # 从藏干算体用
    for b in f.all_branches:
        for hidden in BRANCH_HIDDEN.get(b, []):
            tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hidden, '')), '')
            if tg in ti_gods:
                f.ti_branches.add(b)
            if tg in yong_gods:
                f.yong_branches.add(b)
    
    # L3 墓库
    f.muku_branches = branch_set & MUKU_BRANCHES
    
    # 墓库是否被冲（开库）
    for muku in f.muku_branches:
        for pair in f.chong_pairs:
            if muku in pair:
                f.muku_opened.add(muku)
    
    # L3 做功（简化版：有冲/合/穿的支都算参与做功）
    for pair in f.chong_pairs | f.he_pairs | f.chuan_pairs:
        for b in pair:
            f.working_branches.add(b)
    
    # 做功目标：宾位的字
    f.work_targets = f.guest_branches & f.working_branches
    
    # 做功方式
    if f.chong_pairs:
        f.work_methods.add('冲')
    if f.he_pairs:
        f.work_methods.add('合')
    if f.chuan_pairs:
        f.work_methods.add('穿')
    if f.xing_pairs:
        f.work_methods.add('刑')
    
    # L4 正局反局（简化：有冲合就先记着，后面再精确）
    if len(f.work_methods) > 0:
        f.zheng_fan_ju = "UNKNOWN"
    else:
        f.zheng_fan_ju = "NO_WORK"
    
    # L4 贼捕（简化：主位有力量制宾位）
    if len(f.main_branches) >= 2 and len(f.guest_branches & f.working_branches) > 0:
        f.zei_bu = "POSSIBLE"
    
    return f


if __name__ == "__main__":
    # 测试案例5：丁亥 癸丑 己未 癸酉
    print("=== 案例5：丁亥 癸丑 己未 癸酉 ===")
    f = calc_features("丁亥", "癸丑", "己未", "癸酉")
    print(f"日主: {f.day_master}")
    print(f"十神: 年={f.year_tg} 月={f.month_tg} 时={f.hour_tg}")
    print(f"冲对: {f.chong_pairs}")
    print(f"合对: {f.he_pairs}")
    print(f"穿对: {f.chuan_pairs}")
    print(f"刑对: {f.xing_pairs}")
    print(f"宾主: 主={f.main_branches} 宾={f.guest_branches}")
    print(f"体用: 体={f.ti_branches} 用={f.yong_branches}")
    print(f"墓库: {f.muku_branches}")
    print(f"开库: {f.muku_opened}")
    print(f"做功支: {f.working_branches}")
    print(f"做功目标: {f.work_targets}")
    print(f"做功方式: {f.work_methods}")
    print(f"局型: {f.zheng_fan_ju}")
    print(f"贼捕: {f.zei_bu}")
