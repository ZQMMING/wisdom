import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine, cases
from collections import Counter

tier_diff = Counter()
tier2_dist = Counter()
tier_dist = Counter()
diff_cases = []

for c in cases:
    fp = c['fp']
    try:
        p, f, ye, tp0 = engine(fp)
        tier = ye.get('spectrum_tier')
        tier2 = ye.get('spectrum_tier2')
        tier_dist[tier] += 1
        tier2_dist[tier2] += 1
        if tier != tier2:
            tier_diff[(tier, tier2)] += 1
            if len(diff_cases) < 20:
                diff_cases.append((c.get('li'), c.get('bazi'), tier, tier2))
    except Exception as e:
        pass

print("=== tier分布 ===")
for k, v in sorted(tier_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print("\n=== tier2分布 ===")
for k, v in sorted(tier2_dist.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print(f"\n=== tier与tier2差异: {sum(tier_diff.values())}例 ===")
for (t1, t2), v in sorted(tier_diff.items(), key=lambda x: -x[1]):
    print(f"  {t1} -> {t2}: {v}例")

print("\n=== 差异案例(前20) ===")
for li, bazi, t1, t2 in diff_cases:
    print(f"  L{li} {bazi}: {t1} -> {t2}")
