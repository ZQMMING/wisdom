# -*- coding: utf-8 -*-
"""对照V2.22架构审计."""
import re, sys
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

records = []
for i, ln in enumerate(lines):
    s = ln.strip()
    if s.startswith('八字'):
        body = s.split('：', 1)[-1].split(':', 1)[-1].strip()
        pairs = GZ.findall(body)
        if len(pairs) == 4:
            records.append({'src_line': i+1, 'pillars': pairs})
        continue
    pairs = GZ.findall(s)
    if len(pairs) == 4 and len(s) < 60:
        cleaned = GZ.sub('', s).replace(' ', '').replace('\u3000', '')
        if cleaned == '':
            records.append({'src_line': i+1, 'pillars': pairs})

from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_power_queries import run_queries

def run(pillars):
    p = {k: list(v) for k, v in zip(('year','month','day','hour'), pillars)}
    f = build(p)
    pa = build_power_structure(p)
    hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc = build_root_classes(p, hst)
    tc = build_tou_cang(f)
    wx = build_wang_xiang(f, f['day_stem'])
    rr = build_root_relations(rc, f['combination_facts'])
    ts = build_two_side(rc, tc, rr)
    bt = build_branch_tiers(p, f)
    th = build_tian_he(p, f)
    net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)
    qs = run_queries(net)
    return f, net, qs

# 看第一个命例的完整输出结构
r = records[0]
f, net, qs = run(r['pillars'])

print('=== V2.22架构对照 ===')
print()
print('【算层 - 八字排盘】')
print(f'  四柱: {r["pillars"]}')
print(f'  日主: {f["day_stem"]}')
print(f'  月令: {f["month_branch"]}')
print(f'  藏干: {f["hidden_stems"]}')
print(f'  十神: {f["ten_god_members"]}')
print()
print('【辩层 - 结构判断】')
print(f'  根: {f["root_weight_class_facts"]}')
print(f'  月令: {f["month_supports_daymaster"]}')
print(f'  网络节点: {list(net.keys())[:5]}...')
print(f'  query: {len(qs)}个')
print()
print('【断言层 - 输出】')
for q in qs[:5]:
    print(f'  {q["query_id"]}: {q["state"]}')
