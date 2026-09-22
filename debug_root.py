import sys
sys.path.insert(0, '.')
from spec.root_qi import BRANCH_CANGGAN, STEM_WUXING

# C2: 癸巳 乙卯 己亥 癸子
day_stem = "己"
day_wx = STEM_WUXING[day_stem]
print(f"日主: {day_stem}, 五行: {day_wx}")

branches = ["巳", "卯", "亥", "子"]
for i, branch in enumerate(branches):
    canggan = BRANCH_CANGGAN[branch]
    print(f"\n支{i}: {branch}, 藏干: {canggan}")
    for level_idx, stem in enumerate(canggan):
        if not stem:
            continue
        stem_wx = STEM_WUXING[stem]
        print(f"  藏干{level_idx}: {stem}({stem_wx}), 同五行? {stem_wx == day_wx}")
