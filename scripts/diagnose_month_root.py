import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine, cases
from collections import Counter

# 统计月令本气被算作根的案例
month_root_count = 0
total = 0
examples = []

for c in cases:
    fp = c[1]
    if not fp or len(fp) != 4:
        continue
    try:
        p, f, ye, tp0 = engine(fp)
        qr = ye.get('qiang_ruo') or {}
        root_detail = qr.get('root_detail') or {}
        ben_n = root_detail.get('ben_n', 0)
        
        # 检查月令是否为本气根
        month_branch = fp[1][1]
        day_stem = fp[2][0]
        WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
        BRANCH_WX = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
        dm_wx = WUXING[day_stem]
        month_is_ben = BRANCH_WX[month_branch] == dm_wx
        
        total += 1
        if month_is_ben and ben_n >= 1:
            month_root_count += 1
            if len(examples) < 10:
                examples.append((c[0], ''.join([g+z for g,z in fp]), dm_wx, month_branch, ben_n, qr.get('root_class'), qr.get('effective')))
    except Exception:
        continue

print(f"总案例数: {total}")
print(f"月令本气被算作根的案例数: {month_root_count} ({month_root_count/total*100:.1f}%)")
print(f"\n=== 前10例 ===")
for li, bazi, dm_wx, mz, ben_n, rc, eff in examples:
    print(f"  L{li} {bazi}: 日主{dm_wx}, 月令{mz}(本气), ben_n={ben_n}, root_class={rc}, effective={eff}")
