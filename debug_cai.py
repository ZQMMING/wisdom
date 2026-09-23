import sys
sys.path.insert(0, '.')
from spec.root_qi import shi, STEM_WUXING

# C财+: 戊戌 己巳 甲午 己丑
branches = ["戌", "巳", "午", "丑"]
stems = ["戊", "己", "甲", "己"]
day_wx = "木"

from engines.cong_ge_gates import WUXING_OF
cong_wx = WUXING_OF[day_wx]

print("=== C财+势计算 ===")
for family, wx in cong_wx.items():
    s = shi(branches, stems, wx, "巳")
    print(f"  {family}({wx}): {s:.2f}")
