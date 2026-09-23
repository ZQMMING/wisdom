# -*- coding: utf-8 -*-
"""化气族F0总闸"""
import sys
sys.path.insert(0, '.')
from spec.root_qi import STEM_WUXING, BENQI, shi
from engines.cong_ge_gates import WUXING_OF, SHISHEN_CLASSES


# 天干五合
TIAN_GAN_HE = {
    "甲": ("己", "土", "甲己化土"),
    "己": ("甲", "土", "甲己化土"),
    "乙": ("庚", "金", "乙庚化金"),
    "庚": ("乙", "金", "乙庚化金"),
    "丙": ("辛", "水", "丙辛化水"),
    "辛": ("丙", "水", "丙辛化水"),
    "丁": ("壬", "木", "丁壬化木"),
    "壬": ("丁", "木", "丁壬化木"),
    "戊": ("癸", "火", "戊癸化火"),
    "癸": ("戊", "火", "戊癸化火"),
}

# 化神当令月份
HUA_MONTH = {
    "土": ["辰", "戌", "丑", "未"],
    "金": ["申", "酉", "戌"],
    "水": ["亥", "子", "丑"],
    "木": ["寅", "卯", "辰"],
    "火": ["巳", "午", "未"],
}


def huaqi_f0(stems, branches, day_stem):
    """
    化气族F0总闸

    返回：(是否化气, 化神五行, reason_tag)
    """
    # 硬闸①：日时天干五合
    if day_stem not in TIAN_GAN_HE:
        return False, None, "F0·日干无五合"
    
    partner, hua_wx, hua_name = TIAN_GAN_HE[day_stem]
    
    # 检查五合是否透干（年干/月干/时干）
    he_tou = False
    for i, s in enumerate(stems):
        if i == 2: continue  # 跳过日干
        if s == partner:
            he_tou = True
            break
    
    if not he_tou:
        return False, None, f"F0·{partner}不透干"
    
    # 硬闸②：化神当令
    month_branch = branches[1]
    if month_branch not in HUA_MONTH[hua_wx]:
        return False, hua_wx, f"F0·化神{hua_wx}不当令（月支{month_branch}）"
    
    # 硬闸③：化神成势——化神势>克化神势
    # 克化神的五行：克我者为官杀
    ke_hua_wx = None
    for wx, ke_wx in [("木", "金"), ("火", "水"), ("土", "木"), ("金", "火"), ("水", "土")]:
        if hua_wx == wx:
            ke_hua_wx = ke_wx
            break
    
    hua_shi = shi(branches, stems, hua_wx, month_branch)
    ke_shi = shi(branches, stems, ke_hua_wx, month_branch)
    
    if hua_shi <= ke_shi:
        return False, hua_wx, f"F0·化神势不足（{hua_wx}={hua_shi:.2f} vs 克{ke_hua_wx}={ke_shi:.2f}）"
    
    return True, hua_wx, f"{hua_name}·化神势{hua_shi:.2f}占优"
