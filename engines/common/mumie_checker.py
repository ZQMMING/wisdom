# -*- coding: utf-8 -*-
"""母灭判定(纯布尔枚举版)"""
import sys
sys.path.insert(0, '.')
from engines.common.root_grade_boundary import to_root_grade
from engines.common.dangzhong_counter import calc_dangzhong

WX_SHENG = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

def check_mumie(branches, stems, day_master):
    dz = calc_dangzhong(branches, stems)
    dm_wx = _stem_wx(day_master)
    yin_wx = WX_SHENG[dm_wx]
    dm_val = dz.get(dm_wx, 0)
    yin_val = dz.get(yin_wx, 0)
    dm_grade = to_root_grade(dm_val)
    yin_grade = to_root_grade(yin_val)
    yin_strong = yin_grade in ["禄刃", "长生"]
    dm_weak = dm_grade in ["无根", "受制"]
    if not (yin_strong and dm_weak):
        return {"status": "", "taishi": "", "state": ""}
    state = "CONFIRMED" if yin_grade == "禄刃" else "CANDIDATE"
    return {"status": "母灭", "taishi": yin_wx + "多" + dm_wx + "熄", "state": state}

def _stem_wx(stem):
    table = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
    return table.get(stem, "")

if __name__ == "__main__":
    r1 = check_mumie(["卯", "寅", "卯", "辰"], ["癸", "甲", "丁", "甲"], "丁")
    print("木多火熄:", r1)
