# -*- coding: utf-8 -*-
"""查11条special为空的原因"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
import json

# 读基线
with open('baseline_special_20260922.json', 'r', encoding='utf-8') as f:
    baseline = json.load(f)

# 找special为空的案例
print('=== 11条special为空的案例 ===')
empty_cases = []
for b in baseline:
    if not b.get('special'):
        empty_cases.append(b['li'])
        print('  li=%d: fp=%s' % (b['li'], b['fp']))

print()
print('总数: %d' % len(empty_cases))

# 交集检查1: 11条 ∩ 20条种子用例
sample_li = [1897, 471, 190, 2035, 902, 849, 726, 491, 461, 1986, 1606, 396, 1839, 1363, 244, 656, 729, 1520, 1865, 1811]
overlap1 = set(empty_cases) & set(sample_li)
print()
print('交集1: 11条 ∩ 20条种子用例:', overlap1 if overlap1 else '无交集 ✅')

# 交集检查2: 11条 ∩ 专旺幻觉
zhuanwang_types = ['曲直格', '炎上格', '稼穑格', '从革格', '润下格']
hallucination_zhuanwang = []
for b in baseline:
    if any(t in b.get('special', '') for t in zhuanwang_types):
        hallucination_zhuanwang.append(b['li'])

overlap2 = set(empty_cases) & set(hallucination_zhuanwang)
print('交集2: 11条 ∩ 专旺幻觉(共%d条):' % len(hallucination_zhuanwang), overlap2 if overlap2 else '无交集 ✅')

# 查这11条的具体报错
print()
print('=== 逐条查报错 ===')
from scripts.dayun_align import engine
from scripts.dayun_align import cases

cases_dict = {c[0]: c for c in cases if len(c[2]) >= 4}

for li in empty_cases:
    if li not in cases_dict:
        print('  li=%d: 不在cases中!' % li)
        continue
    fp = cases_dict[li][1]
    try:
        p, f, ye, tp0, wp, th = engine(fp)
        special = ye.get('special') or ''
        print('  li=%d: special="%s" (无报错)' % (li, special))
    except Exception as e:
        print('  li=%d: 报错=%s' % (li, str(e)[:100]))
