# -*- coding: utf-8 -*-
"""专旺族F0总闸"""
import sys
sys.path.insert(0, '.')
from spec.root_qi import STEM_WUXING, BENQI, shi
from engines.cong_ge_gates import WUXING_OF, SHISHEN_CLASSES


def zhuanwang_f0(stems, branches, day_stem, root_qi_val):
    """
    专旺族F0总闸：不依赖root_qi，直接判"日主当令+满盘印比+无破格"

    返回：(是否专旺, reason_tag)
    """
    day_wx = STEM_WUXING[day_stem]
    month_wx = BENQI[branches[1]]

    # 硬闸①：日主当令（月支本气=日主五行）
    if month_wx != day_wx:
        return False, f"F0·不当令（月支{month_wx}≠日主{day_wx}）"

    # 算印比势（比劫=日主同五行）
    yin_wx = WUXING_OF[day_wx]["印"]
    bi_wx = day_wx  # 比劫=日主同五行
    yin_shi = shi(branches, stems, yin_wx, branches[1])
    bi_shi = shi(branches, stems, bi_wx, branches[1])
    yin_bi_shi = yin_shi + bi_shi

    # 算官杀/财势
    guan_sha_wx = WUXING_OF[day_wx]["官杀"]
    cai_wx = WUXING_OF[day_wx]["财"]
    guan_sha_shi = shi(branches, stems, guan_sha_wx, branches[1])
    cai_shi = shi(branches, stems, cai_wx, branches[1])

    # 硬闸②：印比势必须最大
    if yin_bi_shi <= guan_sha_shi or yin_bi_shi <= cai_shi:
        return False, f"F0·印比势不占优（印比={yin_bi_shi:.2f} vs 官杀={guan_sha_shi:.2f} vs 财={cai_shi:.2f}）"

    # 硬闸③：官杀不透干
    guan_sha_cls = SHISHEN_CLASSES[day_wx]["官杀"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) in guan_sha_cls:
            return False, f"F0·官杀透干破格（{s}）"

    # 硬闸④：财不透干
    cai_cls = SHISHEN_CLASSES[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) in cai_cls:
            return False, f"F0·财透干破格（{s}）"

    return True, f"专旺·印比势{yin_bi_shi:.2f}占优"
