# -*- coding: utf-8 -*-
"""深度分析泄和无根不匹配原因."""
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
    return f, net, [q['query_id'].split('QUERY-')[-1] for q in qs if q['state'] == 'SUPPORTED']

# 泄不匹配例子
print('=== 泄不匹配例子 ===')
count = 0
for r in records:
    if '泄' in r['duanyu']:
        f, net, qids = run(r['pillars'])
        if 'XIEQI-TAIZHONG' not in qids:
            count += 1
            if count <= 5:
                s = ' '.join(''.join(p) for p in r['pillars'])
                print(f'L{r["src_line"]}: {s}')
                print(f'  断语: {r["duanyu"][:80]}')
                print(f'  引擎root: {"HEAVY" if any(v["class"]=="HEAVY" for v in f["root_weight_class_facts"].values()) else ("LIGHT" if f["root_weight_class_facts"] else "NONE")}')
                print(f'  引擎season: {f["month_supports_daymaster"]}')
                print(f'  query: {qids}')
                print()

print('=== 无根不匹配例子 ===')
count = 0
for r in records:
    if '无根' in r['duanyu']:
        f, net, qids = run(r['pillars'])
        if not any(q in qids for q in ['JIRUO-WUGEN', 'LIGHT-ROOT']):
            count += 1
            if count <= 5:
                s = ' '.join(''.join(p) for p in r['pillars'])
                print(f'L{r["src_line"]}: {s}')
                print(f'  断语: {r["duanyu"][:80]}')
                print(f'  引擎root: {"HEAVY" if any(v["class"]=="HEAVY" for v in f["root_weight_class_facts"].values()) else ("LIGHT" if f["root_weight_class_facts"] else "NONE")}')
                print(f'  引擎season: {f["month_supports_daymaster"]}')
                print(f'  query: {qids}')
                print()
