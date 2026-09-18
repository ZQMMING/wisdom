# -*- coding: utf-8 -*-
"""统计引擎对513命例输出完整信息."""
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

# 统计输出完整度
has_root = 0
has_season = 0
has_queries = 0
has_ge = 0
has_yongshen = 0
has_jixiong = 0
has_dayun = 0
has_liunian = 0

for r in records:
    f, net, qs = run(r['pillars'])
    if f['root_weight_class_facts']: has_root += 1
    if f['month_supports_daymaster'] is not None: has_season += 1
    if qs: has_queries += 1
    if any(q['query_id'].endswith('GE-QING') and q['state'] == 'SUPPORTED' for q in qs): has_ge += 1
    if any(q['query_id'].endswith('YONGSHEN-STRUCTURE') and q['state'] == 'SUPPORTED' for q in qs): has_yongshen += 1
    if any(q['query_id'].endswith('JIXIONG-STRUCTURE') and q['state'] == 'SUPPORTED' for q in qs): has_jixiong += 1

total = len(records)
print(f'DTS {total}命例引擎输出完整度:')
print(f'有根信息: {has_root} ({has_root/total*100:.1f}%)')
print(f'有月令信息: {has_season} ({has_season/total*100:.1f}%)')
print(f'有query: {has_queries} ({has_queries/total*100:.1f}%)')
print(f'有格清: {has_ge} ({has_ge/total*100:.1f}%)')
print(f'有用神结构: {has_yongshen} ({has_yongshen/total*100:.1f}%)')
print(f'有吉凶结构: {has_jixiong} ({has_jixiong/total*100:.1f}%)')
