# -*- coding: utf-8 -*-
"""专旺族L4分级——对称从格族"""
import sys
sys.path.insert(0, '.')
from spec.root_qi import STEM_WUXING, BENQI, shi
from engines.cong_ge_gates import WUXING_OF, SHISHEN_CLASSES


def _demote_count_zw(stems, branches, day_stem, shi_dict):
    """专旺族减项计数"""
    n = 0
    day_wx = STEM_WUXING[day_stem]
    month_wx = BENQI[branches[1]]

    # 减项①：印星过重（母慈灭子）——印势>比劫势
    yin_wx = WUXING_OF[day_wx]["印"]
    yin_shi = shi(branches, stems, yin_wx, branches[1])
    bi_shi = shi(branches, stems, day_wx, branches[1])
    if yin_shi > bi_shi * 1.5:
        n += 1

    # 减项②：食伤泄秀过重——食伤势>印比势的30%
    shi_wx = WUXING_OF[day_wx]["食伤"]
    shi_shi = shi(branches, stems, shi_wx, branches[1])
    yin_bi_shi = yin_shi + bi_shi
    if yin_bi_shi > 0 and shi_shi / yin_bi_shi > 0.3:
        n += 1

    # 减项③：财星虚透（无根但被克）——已在F0放行，算减项
    cai_cls = SHISHEN_CLASSES[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) in cai_cls:
            # 检查是否无根
            cai_wx = WUXING_OF[day_wx]["财"]
            cai_root = any(BENQI.get(b) == cai_wx for b in branches)
            if not cai_root:
                n += 1
                break

    # 减项④：官杀虚透（无根但被克）
    guan_sha_cls = SHISHEN_CLASSES[day_wx]["官杀"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) in guan_sha_cls:
            guan_sha_wx = WUXING_OF[day_wx]["官杀"]
            guan_sha_root = any(BENQI.get(b) == guan_sha_wx for b in branches)
            if not guan_sha_root:
                n += 1
                break

    return n


def _grade_zw(demote):
    """专旺族分级"""
    if demote == 0:
        return "CONFIRMED"
    elif demote == 1:
        return "MID_1"
    elif demote == 2:
        return "MID_2"
    else:
        return "REJECT"


def zhuanwang_pan(stems, branches, day_stem, root_qi_val):
    """专旺族总入口"""
    from engines.zhuanwang_gates import zhuanwang_f0

    # F0总闸
    ok, reason = zhuanwang_f0(stems, branches, day_stem, root_qi_val)
    if not ok:
        return None

    # 算势字典
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    shi_dict = {}
    for family, wx in cong_wx.items():
        shi_dict[family] = shi(branches, stems, wx, branches[1])

    # 减项计数
    demote = _demote_count_zw(stems, branches, day_stem, shi_dict)
    grade = _grade_zw(demote)

    return ("专旺", grade, f"专旺·减项{demote}")
