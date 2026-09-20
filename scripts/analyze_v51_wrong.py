#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V5.1误判案例深度分析: 身弱印比反为凶的共同机制
V5.1命中的案例中, 部分原典判凶(av->xiong), 找出这些案例的共同机制
"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location("dayun_align_mod", "scripts/dayun_align.py")
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

cases = mod.cases
engine = mod.engine
cls_w = mod.cls_w
GAN_WX = mod.GAN_WX
BRANCH_WX = mod.BRANCH_WX
WUXING = mod.WUXING
SHENG = mod.SHENG
KE = mod.KE
luck_verdict = mod.luck_verdict
transit_clash_verdicts = mod.transit_clash_verdicts
build_transit_power = mod.build_transit_power

from engines.common.branch_role_matrix import build_branch_role_matrix

v51_correct = []  # av->ji (V5.1正确)
v51_wrong = []    # av->xiong (V5.1误判)

for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except: continue
    prim = ye.get('yongshen_primary') or ''
    fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av = set(ye.get('yongshen_avoid') or [])
    dm = f['day_stem']
    tier = ye.get('spectrum_tier', 'N/A')
    paths = ye.get('yongshen_paths', [])
    _spec = ye.get('spectrum_tier') or ''
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'): v = None
        if not v or v in ('hun', 'lao'): continue
        gc = cls_w(GAN_WX[g], fav, av)
        zc = cls_w(BRANCH_WX[z], fav, av)
        
        # V5.1条件: 身弱+印比+非从格
        if _spec in ('衰极','太衰','衰'):
            _dmwW=WUXING[dm]; _SHENG_ME_W={v:k for k,v in SHENG.items()}
            _yinbi={_dmwW, _SHENG_ME_W.get(_dmwW)}
            _ppY='/'.join(paths)
            if not any(x in _ppY for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI')):
                _is_yinbi = (GAN_WX.get(g) in _yinbi) or (BRANCH_WX.get(z) in _yinbi)
                if _is_yinbi and (gc=='av' or zc=='av'):
                    # V5.1会把lc改为fav
                    # 判断原典是吉还是凶
                    tp = build_transit_power(p, [gz])
                    clash = [c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
                    matrix = build_branch_role_matrix(fp, ye, f)
                    
                    case_info = {
                        'case_id': f'L{li+1}',
                        'chart': ''.join(a+b for a,b in fp),
                        'daymaster': dm,
                        'tier': tier,
                        'paths': paths,
                        'dayun': gz,
                        'gc': gc,
                        'zc': zc,
                        'fav': sorted(fav),
                        'avoid': sorted(av),
                        'primary': prim,
                        'clash': clash,
                        'blob': blob[:80] if blob else '',
                        'matrix': matrix,
                        'tp': tp,
                    }
                    
                    if v == 'ji':
                        v51_correct.append(case_info)
                    else:
                        v51_wrong.append(case_info)

print(f"V5.1命中总数: {len(v51_correct) + len(v51_wrong)}")
print(f"  正确(av->ji, 原典吉): {len(v51_correct)}")
print(f"  误判(av->xiong, 原典凶): {len(v51_wrong)}")
print()

# 分析误判案例的共同机制
print("=" * 80)
print("【误判案例(身弱印比反为凶)逐例分析】")
print("=" * 80)

from collections import Counter
mechanism_counter = Counter()

for i, c in enumerate(v51_wrong, 1):
    print(f"\n{i}. {c['case_id']} {c['chart']} 日主{c['daymaster']} tier={c['tier']}")
    print(f"   大运{c['dayun']} gc={c['gc']} zc={c['zc']}")
    print(f"   primary={c['primary']} fav={c['fav']} avoid={c['avoid']}")
    print(f"   冲={c['clash']}")
    print(f"   原文={c['blob']}")
    
    # 分析机制
    mechanisms = []
    
    # 机制1: 大运与原局有冲
    if c['clash']:
        mechanisms.append('冲原局')
        mechanism_counter['冲原局'] += 1
    
    # 机制2: 大运五行克调候用神(加重寒湿/燥热)
    dm_wx = WUXING[c['daymaster']]
    dayun_wx = GAN_WX.get(c['dayun'][0])
    month_branch = c['chart'][3]  # 月支
    is_winter = month_branch in ('亥','子','丑')
    is_summer = month_branch in ('巳','午','未')
    
    # 机制3: 印比过重(印多埋子/比劫夺财)
    # 检查原局印比数量
    hidden_stems = c['matrix']
    yin_count = 0
    bi_count = 0
    for pos, info in hidden_stems.items():
        for h in info['hidden_roles']:
            if h['ten_god'] in ('正印','偏印'): yin_count += 1
            if h['ten_god'] in ('比肩','劫财'): bi_count += 1
    
    if yin_count >= 3:
        mechanisms.append(f'印重({yin_count}个)')
        mechanism_counter['印重'] += 1
    if bi_count >= 3:
        mechanisms.append(f'比劫重({bi_count}个)')
        mechanism_counter['比劫重'] += 1
    
    # 机制4: 大运合化改变五行
    combination_facts = c['tp'].get('combination_facts', {})
    if combination_facts:
        mechanisms.append('有合化')
        mechanism_counter['有合化'] += 1
    
    # 机制5: 调候矛盾(冬月水多加重寒湿)
    if is_winter and dayun_wx == '水':
        mechanisms.append('冬月添水(加重寒湿)')
        mechanism_counter['冬月添水'] += 1
    if is_summer and dayun_wx == '火':
        mechanisms.append('夏月添火(加重燥热)')
        mechanism_counter['夏月添火'] += 1
    
    # 机制6: 大运天干克用神
    if c['primary'] and KE.get(dayun_wx) == c['primary']:
        mechanisms.append(f'天干克用神({dayun_wx}克{c["primary"]})')
        mechanism_counter['天干克用神'] += 1
    
    print(f"   机制: {', '.join(mechanisms) if mechanisms else '无明显机制'}")
    
    # 地支角色矩阵简要
    for pos, info in c['matrix'].items():
        roles = []
        if info['is_heavy_root']: roles.append('重根')
        elif info['is_light_root']: roles.append('轻根')
        if info['has_primary_yongshen']: roles.append('用神根')
        if info['has_avoid']: roles.append('忌神根')
        if info['is_pattern_root']: roles.append('格局根')
        if roles:
            print(f"   [{info['palace']}{info['branch']}] {','.join(roles)}")

print("\n" + "=" * 80)
print("【误判案例机制统计】")
for mech, cnt in mechanism_counter.most_common():
    print(f"  {mech}: {cnt}例")

print("\n" + "=" * 80)
print("【正确案例(身弱印比为吉)简要对比】")
for i, c in enumerate(v51_correct[:5], 1):
    print(f"{i}. {c['case_id']} {c['chart']} 大运{c['dayun']} tier={c['tier']} 原文={c['blob'][:50]}")
