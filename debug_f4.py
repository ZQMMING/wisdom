import sys
sys.path.insert(0, '.')
from spec.root_qi import shi, STEM_WUXING
from engines.cong_ge_gates import WUXING_OF

# F4+: 戊寅 戊午 庚辰 己未
branches = ["寅", "午", "辰", "未"]
stems = ["戊", "戊", "庚", "己"]
day_stem = "庚"
day_wx = STEM_WUXING[day_stem]
cong_wx = WUXING_OF[day_wx]

print("=== F4+势字典 ===")
shi_dict = {}
for family, wx in cong_wx.items():
    s = shi(branches, stems, wx, branches[1])
    shi_dict[family] = s
    print(f"  {family}({wx}): {s:.2f}")

shi_dict["印比"] = shi_dict.get("印", 0) + shi_dict.get("比", 0)
print(f"  印比(合并): {shi_dict['印比']:.2f}")

print(f"\n主势: {max(shi_dict.items(), key=lambda kv: kv[1])}")
