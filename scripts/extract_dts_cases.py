# -*- coding: utf-8 -*-
"""从 DTS 全文认真提取命例: 四柱行(一行4干支对, 空格分隔) + 大运行(下一行多干支对)."""
import re, sys, json
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

# 四柱行: 一行内恰好4个干支对(独立成对, 不是叙述里的零散词)
# 大运行: 下一行含 "大运" 或 >=6个干支对
records = []
for i, ln in enumerate(lines):
    s = ln.strip()
    # 跳过 "八字：" 前缀行(已单独处理)
    if s.startswith('八字'):
        body = s.split('：', 1)[-1].split(':', 1)[-1].strip()
        pairs = GZ.findall(body)
        if len(pairs) == 4:
            # 下一行是大运
            dy = ''
            if i+1 < len(lines): dy = lines[i+1]
            records.append({'src_line': i+1, 'pillars': pairs, 'dayun_line': dy[:80], 'duanyu_start': ''})
        continue
    # 直接四柱行: 整行恰好4个干支对, 且不含标点叙述词
    pairs = GZ.findall(s)
    if len(pairs) == 4 and len(s) < 60:
        # 必须是纯干支+空格
        cleaned = GZ.sub('', s).replace(' ', '').replace('\u3000', '')
        if cleaned == '':
            dy = ''
            duanyu = ''
            if i+1 < len(lines): dy = lines[i+1]
            if i+2 < len(lines): duanyu = lines[i+2][:80]
            records.append({'src_line': i+1, 'pillars': pairs, 'dayun_line': dy[:80], 'duanyu_start': duanyu})

print(f'提取命例: {len(records)}')
for r in records[:8]:
    s = ' '.join(''.join(p) for p in r['pillars'])
    print(f"  L{r['src_line']}: {s}  大运: {r['dayun_line'][:40]}")

# 跑引擎
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
from collections import Counter

root_dist = Counter()
errors = []
ok = 0
for r in records:
    four = r['pillars']
    p = {'year': list(four[0]), 'month': list(four[1]), 'day': list(four[2]), 'hour': list(four[3])}
    try:
        f = build(p); pa = build_power_structure(p)
        hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
        rc = build_root_classes(p, hst); tc = build_tou_cang(f); wx = build_wang_xiang(f, f['day_stem'])
        rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
        root_dist[net['dimensions']['ROOT']['root_weight_class']] += 1
        ok += 1
    except Exception as e:
        errors.append((r['src_line'], repr(e)[:80]))

print(f'\n跑通: {ok}/{len(records)}, 崩溃: {len(errors)}')
for e in errors[:5]: print('  ERR', e)
print('\nroot分布:')
for k,v in root_dist.most_common(): print(f'  {str(k):10s} {v}')

# 保存
out = [{'src_line': r['src_line'], 'pillars': [list(x) for x in r['pillars']]} for r in records]
json.dump(out, open('scripts/dts_cases_extracted.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n保存: scripts/dts_cases_extracted.json')
