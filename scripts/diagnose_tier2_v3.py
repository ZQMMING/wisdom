import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine, cases
from collections import Counter

tier2_dist = Counter()
tier_dist = Counter()
diff_count = 0
total = 0
diff_detail = Counter()

for c in cases:
    # cases结构: (编号, fp, 大运列表, 原文)
    fp = c[1]
    if not fp or len(fp) != 4:
        continue
    try:
        p, f, ye, tp0 = engine(fp)
        tier = ye.get('spectrum_tier')
        tier2 = ye.get('spectrum_tier2')
        if tier is None or tier2 is None:
            continue
        tier_dist[tier] += 1
        tier2_dist[tier2] += 1
        total += 1
        if tier != tier2:
            diff_count += 1
            diff_detail[(tier, tier2)] += 1
    except Exception:
        continue

print(f"有效案例数: {total}")
print(f"tier与tier2差异: {diff_count}例 ({diff_count/total*100:.1f}%)")
print(f"tier==tier2: {total-diff_count}例 ({(total-diff_count)/total*100:.1f}%)")

print("\n=== tier分布(旧) ===")
for k, v in sorted(tier_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v} ({v/total*100:.1f}%)")

print("\n=== tier2分布(新) ===")
for k, v in sorted(tier2_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v} ({v/total*100:.1f}%)")

print("\n=== 差异明细(tier -> tier2) ===")
for (t1, t2), v in sorted(diff_detail.items(), key=lambda x: -x[1]):
    print(f"  {t1} -> {t2}: {v}例")
