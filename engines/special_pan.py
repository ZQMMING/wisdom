# -*- coding: utf-8 -*-
"""特殊格局+正格 统一主入口"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import STEM_WUXING, shi, calc_root_qi
from engines.cong_ge_gates import cong_ge_pan, WUXING_OF
from engines.zhuanwang_grade import zhuanwang_pan
from engines.huaqi_grade import huaqi_pan


def special_pan(stems, branches, day_stem, root_qi_val=None):
    """
    统一格局判定主入口
    优先级：化气 → 专旺 → 从格 → 正格

    返回：(family, grade, reason_tag)
    """
    if root_qi_val is None:
        root_qi_val = calc_root_qi(day_stem, branches, stems)

    # 第一步：化气族（优先级最高）
    huaqi_result = huaqi_pan(stems, branches, day_stem, root_qi_val)
    if huaqi_result is not None:
        return huaqi_result

    # 第二步：专旺族
    zw_result = zhuanwang_pan(stems, branches, day_stem, root_qi_val)
    if zw_result is not None:
        return zw_result

    # 第三步：从格族
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    shi_dict = {}
    for family, wx in cong_wx.items():
        shi_dict[family] = shi(branches, stems, wx, branches[1])
    
    cong_result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)
    if cong_result is not None:
        return cong_result

    # 第四步：正格族（兜底）
    return ("正格", "UNKNOWN", "正格族待接入")
