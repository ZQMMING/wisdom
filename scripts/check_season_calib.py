# -*- coding: utf-8 -*-
"""校season: 任氏说当令/乘权/得时 vs IN_SEASON; 说失令/休囚 vs OUT_OF_SEASON."""
import csv, sys, re
sys.path.insert(0, '.')
path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

season_map = {'IN_SEASON':0, 'OUT_OF_SEASON':0, 'SUPPORTS':0}
for r in rows:
    season_map[r['season']] = season_map.get(r['season'],0)+1
print('season分布:', season_map)

# 找任氏说"当令/乘权/得时/得令/旺令"的盘, 应 IN_SEASON
# 找任氏说"失令/休囚/失时/囚令"的盘, 应 OUT_OF_SEASON
ok_dang = 0; bad_dang = []
ok_shi = 0; bad_shi = []
for i, r in enumerate(rows):
    li = int(r['line'])-1
    next_li = len(lines)
    for j in range(i+1, len(rows)):
        next_li = int(rows[j]['line'])-1; break
    seg = '\n'.join(lines[li:min(next_li, li+20)])
    if re.search(r'乘权当令|当令|得时|得令|旺令|乘旺|令旺', seg):
        if r['season'] in ('IN_SEASON','SUPPORTS'): ok_dang += 1
        else: bad_dang.append((r['line'],r['chart'],r['season'],seg[:80]))
    if re.search(r'失令|失时|休囚|囚令|失令', seg):
        if r['season']=='OUT_OF_SEASON': ok_shi += 1
        else: bad_shi.append((r['line'],r['chart'],r['season'],seg[:80]))

print(f'\n任氏说当令/乘权 -> IN/SAI: {ok_dang}, 不一致: {len(bad_dang)}')
for b in bad_dang[:10]: print('  ',b)
print(f'\n任氏说失令/休囚 -> OUT: {ok_shi}, 不一致: {len(bad_shi)}')
for b in bad_shi[:10]: print('  ',b)
