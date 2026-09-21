import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine, cases
from collections import Counter

tier2_dist = Counter()
tier_dist = Counter()
diff_count = 0
total = 0

for c in cases[:500]:
    fp = c.get('fp')
    if not fp:
        continue
    try:
        p, f, ye, tp0 = engine(fp)
        tier = ye.get('spectrum_tier')
        tier2 = ye.get('spectrum_tier2')
        tier_dist[tier] += 1
        tier2_dist[tier2] += 1
        total += 1
        if tier != tier2:
            diff_count += 1
    except Exception as e:
        pass

print(f"总案例数: {total}")
print(f"tier与tier2差异: {diff_count}例 ({diff_count/total*100:.1f}%)")
print("\n=== tier分布 ===")
for k, v in sorted(tier_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v} ({v/total*100:.1f}%)")
print("\n=== tier2分布 ===")
for k, v in sorted(tier2_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v} ({v/total*100:.1f}%)")
