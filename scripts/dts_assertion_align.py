# -*- coding: utf-8 -*-
"""DTS 513命例 全量断言对齐评估: 身旺衰/根/格局/用神 逐条命中率+差异清单."""
import re, sys, json, collections
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

# 1. 提取命例(四柱行+断语段)
pillars_lines = []
for i, ln in enumerate(lines):
    s = ln.strip()
    if s.startswith('八字'):
        b = s.split('：',1)[-1].split(':',1)[-1].strip()
        pp = GZ.findall(b)
        if len(pp)==4: pillars_lines.append((i, pp))
    else:
        pp = GZ.findall(s)
        if len(pp)==4 and len(s)<60:
            c = GZ.sub('',s).replace(' ','').replace('\u3000','')
            if c=='': pillars_lines.append((i, pp))

# 2. 每个命例断语段 = 四柱行后30行(到下一四柱行)
KW_WANG = ['身旺','日主旺','身强','强旺','旺极','太旺','旺相']
KW_RUO = ['身弱','日主弱','身衰','衰弱','弱极','太弱','衰极']
KW_YOUGEN = ['有根','通根','根重','根深','得地']
KW_WUGEN = ['无根','根轻','根浅','根拔']
KW_GEJU = ['正官格','七杀格','正印格','偏印格','正财格','偏财格','食神格','伤官格','建禄格','羊刃格','从格','化气格','专旺格']
KW_YONGSHEN = ['喜','用','宜','忌']

cases = []
for idx, (li, fp) in enumerate(pillars_lines):
    end = pillars_lines[idx+1][0] if idx+1 < len(pillars_lines) else min(li+40, len(lines))
    segment = '\n'.join(lines[li:end])
    wang = [k for k in KW_WANG if k in segment]
    ruo = [k for k in KW_RUO if k in segment]
    yougen = [k for k in KW_YOUGEN if k in segment]
    wugen = [k for k in KW_WUGEN if k in segment]
    geju = [k for k in KW_GEJU if k in segment]
    cases.append({'line':li+1, 'pillars':fp, 'wang':wang, 'ruo':ruo,
                  'yougen':yougen, 'wugen':wugen, 'geju':geju, 'segment':segment[:200]})

print(f'命例总数: {len(cases)}')
print(f'  含旺断语: {sum(1 for c in cases if c["wang"])}')
print(f'  含弱断语: {sum(1 for c in cases if c["ruo"])}')
print(f'  含有根断语: {sum(1 for c in cases if c["yougen"])}')
print(f'  含无根断语: {sum(1 for c in cases if c["wugen"])}')
print(f'  含格局断语: {sum(1 for c in cases if c["geju"])}')

# 3. 跑引擎
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

results = []
wang_hit = wang_total = 0
ruo_hit = ruo_total = 0
yougen_hit = yougen_total = 0
wugen_hit = wugen_total = 0
wang_mismatch = []
ruo_mismatch = []
yougen_mismatch = []
wugen_mismatch = []

for c in cases:
    p = {'year':list(c['pillars'][0]),'month':list(c['pillars'][1]),
         'day':list(c['pillars'][2]),'hour':list(c['pillars'][3])}
    try:
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
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
        qs = {q['query_id'].split('QUERY-')[-1]: q for q in run_queries(net)}
        rw = net['dimensions']['ROOT'].get('root_weight_class', '')
        has_root = net['dimensions']['ROOT'].get('has_root', False)
        # 身旺衰: 引擎用root_class近似(HEAVY=旺, LIGHT/NONE=弱)
        engine_wang = rw == 'HEAVY'
        engine_ruo = rw in ('LIGHT', 'NONE')
        # 根
        engine_yougen = has_root or rw in ('HEAVY', 'LIGHT')
        engine_wugen = (not has_root) and rw == 'NONE'
        # 对齐评估
        if c['wang']:
            wang_total += 1
            if engine_wang: wang_hit += 1
            else: wang_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['wang'],'engine':rw,'segment':c['segment'][:100]})
        if c['ruo']:
            ruo_total += 1
            if engine_ruo: ruo_hit += 1
            else: ruo_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['ruo'],'engine':rw,'segment':c['segment'][:100]})
        if c['yougen']:
            yougen_total += 1
            if engine_yougen: yougen_hit += 1
            else: yougen_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['yougen'],'engine':f'has_root={has_root},rw={rw}'})
        if c['wugen']:
            wugen_total += 1
            if engine_wugen: wugen_hit += 1
            else: wugen_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['wugen'],'engine':f'has_root={has_root},rw={rw}'})
        results.append({'line':c['line'],'root_class':rw,'has_root':has_root})
    except Exception as e:
        results.append({'line':c['line'],'error':str(e)})

print(f'\n=== 身旺衰断言对齐 ===')
print(f'  旺: {wang_hit}/{wang_total} = {wang_hit/wang_total*100:.1f}%' if wang_total else '  旺: 0例')
print(f'  弱: {ruo_hit}/{ruo_total} = {ruo_hit/ruo_total*100:.1f}%' if ruo_total else '  弱: 0例')
print(f'\n=== 根断言对齐 ===')
print(f'  有根: {yougen_hit}/{yougen_total} = {yougen_hit/yougen_total*100:.1f}%' if yougen_total else '  有根: 0例')
print(f'  无根: {wugen_hit}/{wugen_total} = {wugen_hit/wugen_total*100:.1f}%' if wugen_total else '  无根: 0例')

print(f'\n=== 差异清单(前10) ===')
if wang_mismatch:
    print(f'\n旺不匹配({len(wang_mismatch)}例):')
    for m in wang_mismatch[:10]:
        print(f"  L{m['line']}: {''.join(m['pillars'][0])}{''.join(m['pillars'][1])}{''.join(m['pillars'][2])}{''.join(m['pillars'][3])} 任氏={m['ren']} 引擎={m['engine']}")
if ruo_mismatch:
    print(f'\n弱不匹配({len(ruo_mismatch)}例):')
    for m in ruo_mismatch[:10]:
        print(f"  L{m['line']}: {''.join(m['pillars'][0])}{''.join(m['pillars'][1])}{''.join(m['pillars'][2])}{''.join(m['pillars'][3])} 任氏={m['ren']} 引擎={m['engine']}")

# 保存
with open('scripts/dts_assertion_align_results.json', 'w', encoding='utf-8') as f:
    json.dump({'wang_hit':wang_hit,'wang_total':wang_total,'wang_mismatch':wang_mismatch,
               'ruo_hit':ruo_hit,'ruo_total':ruo_total,'ruo_mismatch':ruo_mismatch,
               'yougen_hit':yougen_hit,'yougen_total':yougen_total,'yougen_mismatch':yougen_mismatch,
               'wugen_hit':wugen_hit,'wugen_total':wugen_total,'wugen_mismatch':wugen_mismatch,
               'results':results}, f, ensure_ascii=False, indent=2)
print(f'\n保存: scripts/dts_assertion_align_results.json')
