import sys
sys.path.insert(0, 'scripts')
from dayun_align import engine, cases
from collections import Counter

# 统计tier2=中和的案例中，旧tier的分布
zhonghe_old_tier = Counter()
zhonghe_cases = []
total = 0

for c in cases:
    fp = c[1]
    if not fp or len(fp) != 4:
        continue
    try:
        p, f, ye, tp0 = engine(fp)
        tier = ye.get('spectrum_tier')
        tier2 = ye.get('spectrum_tier2')
        if tier is None or tier2 is None:
            continue
        total += 1
        if tier2 == '中和':
            zhonghe_old_tier[tier] += 1
            if len(zhonghe_cases) < 30:
                zhonghe_cases.append((c[0], ''.join([g+z for g,z in fp]), tier, tier2))
    except Exception:
        continue

print(f"总案例数: {total}")
print(f"tier2=中和案例数: {sum(zhonghe_old_tier.values())} ({sum(zhonghe_old_tier.values())/total*100:.1f}%)")

print("\n=== 中和案例的旧tier分布 ===")
for k, v in sorted(zhonghe_old_tier.items(), key=lambda x: -x[1]):
    print(f"  旧tier={k}: {v}例 ({v/sum(zhonghe_old_tier.values())*100:.1f}%)")

# 统计旧tier=旺/衰但tier2=中和的案例
wang_to_zhonghe = sum(v for k, v in zhonghe_old_tier.items() if k in ('旺极', '太旺', '旺'))
shuai_to_zhonghe = sum(v for k, v in zhonghe_old_tier.items() if k in ('衰极', '太衰', '衰'))
zhonghe_to_zhonghe = zhonghe_old_tier.get('中和', 0)

print(f"\n=== 关键统计 ===")
print(f"旧tier=旺但tier2=中和: {wang_to_zhonghe}例 ({wang_to_zhonghe/sum(zhonghe_old_tier.values())*100:.1f}%)")
print(f"旧tier=衰但tier2=中和: {shuai_to_zhonghe}例 ({shuai_to_zhonghe/sum(zhonghe_old_tier.values())*100:.1f}%)")
print(f"旧tier=中和且tier2=中和: {zhonghe_to_zhonghe}例 ({zhonghe_to_zhonghe/sum(zhonghe_old_tier.values())*100:.1f}%)")

print("\n=== 旧旺新中和案例(前15) ===")
for li, bazi, t1, t2 in zhonghe_cases:
    if t1 in ('旺极', '太旺', '旺'):
        print(f"  L{li} {bazi}: 旧tier={t1}, tier2={t2}")
