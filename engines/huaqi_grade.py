# -*- coding: utf-8 -*-
"""化气族L4分级"""
import sys
sys.path.insert(0, '.')
from spec.root_qi import STEM_WUXING, BENQI, shi
from engines.huaqi_gates import huaqi_f0, TIAN_GAN_HE


def _demote_count_hq(stems, branches, day_stem, hua_wx):
    """化气族减项计数"""
    n = 0
    month_branch = branches[1]

    # 克化神的五行
    ke_map = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
    ke_hua_wx = ke_map.get(hua_wx)

    # 减项①：克化神五行透干
    if ke_hua_wx:
        for i, s in enumerate(stems):
            if i == 2: continue
            if STEM_WUXING.get(s) == ke_hua_wx:
                n += 1
                break

    # 减项②：化神势不足（< 5.0）
    hua_shi = shi(branches, stems, hua_wx, month_branch)
    if hua_shi < 5.0:
        n += 1

    # 减项③：合神虚浮（无根）
    partner, _, _ = TIAN_GAN_HE[day_stem]
    partner_wx = STEM_WUXING[partner]
    partner_root = any(BENQI.get(b) == partner_wx for b in branches)
    if not partner_root:
        n += 1

    return n


def _grade_hq(demote):
    """化气族分级"""
    if demote == 0:
        return "CONFIRMED"
    elif demote == 1:
        return "MID_1"
    elif demote == 2:
        return "MID_2"
    else:
        return "REJECT"


def huaqi_pan(stems, branches, day_stem, root_qi_val):
    """化气族总入口"""
    # F0总闸
    ok, hua_wx, reason = huaqi_f0(stems, branches, day_stem)
    if not ok:
        return None

    # 减项计数
    demote = _demote_count_hq(stems, branches, day_stem, hua_wx)
    grade = _grade_hq(demote)

    return ("化气", grade, f"{reason.split('·')[0]}·减项{demote}")
