import sys
sys.path.insert(0, '.')
from spec.root_qi import shi, _canggan_wuxing_count, _get_hehua_branch

# C1: 癸巳 乙卯 己亥 癸酉
branches = ["巳", "卯", "亥", "酉"]
stems = ["癸", "乙", "己", "癸"]

print("=== 金势逐支计算 ===")
for b in branches:
    count = _canggan_wuxing_count(b, "金", branches, is_month=(b=="卯"), stems=stems)
    print(f"  {b}: {count}")

print(f"\n巳酉半会金局？")
print(f"  巳参与的合化: {_get_hehua_branch('巳', branches, stems)}")
print(f"  酉参与的合化: {_get_hehua_branch('酉', branches, stems)}")

jin_shi = shi(branches, stems, "金", "卯")
print(f"\n金势总计: {jin_shi}")
