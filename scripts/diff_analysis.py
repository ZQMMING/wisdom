# -*- coding: utf-8 -*-
"""分析不匹配差异点."""
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
            duanyu = ''
            for j in range(i+2, min(i+6, len(lines))):
                if lines[j].strip():
                    duanyu = lines[j].strip()[:200]
                    break
            records.append({'src_line': i+1, 'pillars': pairs, 'duanyu': duanyu})
        continue
    pairs = GZ.findall(s)
    if len(pairs) == 4 and len(s) < 60:
        cleaned = GZ.sub('', s).replace(' ', '').replace('\u3000', '')
        if cleaned == '':
            duanyu = ''
            for j in range(i+2, min(i+6, len(lines))):
                if lines[j].strip():
                    duanyu = lines[j].strip()[:200]
                    break
            records.append({'src_line': i+1, 'pillars': pairs, 'duanyu': duanyu})

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
    return [q['query_id'].split('QUERY-')[-1] for q in qs if q['state'] == 'SUPPORTED']

kw_map = {
    '身旺': ['HEAVY-ROOT', 'REN-CAIGUAN', 'ZHONGGUA-2SIDE'],
    '身弱': ['LIGHT-ROOT', 'JIRUO-WUGEN'],
    '得地': ['HEAVY-ROOT', 'LIGHT-ROOT'],
    '得时': ['DESHI-BUWANG', 'SHISHI-BURUO'],
    '得势': ['YIN-PARTY', 'BIJIE-PARTY'],
    '根重': ['HEAVY-ROOT'],
    '无根': ['JIRUO-WUGEN', 'LIGHT-ROOT'],
    '泄': ['XIEQI-TAIZHONG'],
    '财多': ['CAIDUO-SHENRUAN'],
    '杀重': ['SHAZHONG-SHENQING'],
    '根轻': ['LIGHT-ROOT'],
}

diff = {}
for r in records:
    qids = run(r['pillars'])
    dy = r['duanyu']
    for kw, expected in kw_map.items():
        if kw in dy:
            hit = any(e in qids for e in expected)
            if not hit:
                diff[kw] = diff.get(kw, 0) + 1

print('不匹配差异点:')
for k, v in sorted(diff.items(), key=lambda x: -x[1]):
    print(f'  {k:10s} {v:4d}')
