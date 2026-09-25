# -*- coding: utf-8 -*-
"""母灭判定(纯布尔枚举v3)"""
import sys
sys.path.insert(0, '.')
from engines.common.dangzhong_counter import calc_dangzhong, is_dangzhong_strong

WX_SHENG = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}

def check_mumie(branches, stems, day_master):
    dz = calc_dangzhong(branches, stems)
    dm_wx = _stem_wx(day_master)
    yin_wx = WX_SHENG[dm_wx]
    dm_data = dz.get(dm_wx, {})
    yin_data = dz.get(yin_wx, {})
    yin_strong = is_dangzhong_strong(yin_data)
    dm_rootless = dm_data.get("ben_qi_root", 0) == 0
    if not (yin_strong and dm_rootless):
        return {"status": "", "taishi": "", "state": ""}
    state = "CONFIRMED" if yin_data.get("has_sanhui", False) else "CANDIDATE"
    return {"status": "母灭", "taishi": yin_wx + "多" + dm_wx + "熄", "state": state}

def _stem_wx(stem):
    table = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
    return table.get(stem, "")

if __name__ == "__main__":
    r1 = check_mumie(["卯", "寅", "卯", "辰"], ["癸", "甲", "丁", "甲"], "丁")
    print("木多火熄:", r1)
