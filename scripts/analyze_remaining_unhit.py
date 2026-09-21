#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析剩余12例未命中案例"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

engine = mod.engine
cases = mod.cases
GAN_WX = mod.GAN_WX
BRANCH_WX = mod.BRANCH_WX
WUXING = mod.WUXING
SHENG = mod.SHENG
KE = mod.KE
luck_verdict = mod.luck_verdict
transit_clash_verdicts = mod.transit_clash_verdicts
build_transit_power = mod.build_transit_power

unhit_cases = []
for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    dm = f['day_stem']
    _spec = ye.get('spectrum_tier') or ''
    paths = ye.get('yongshen_paths') or []
    prim = ye.get('yongshen_primary') or ''
    fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av = set(ye.get('yongshen_avoid') or [])
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'): v = None
        if not v or v in ('hun', 'lao'): continue
        
        gc = 'fav' if GAN_WX[g] in fav else ('av' if GAN_WX[g] in av else 'xian')
        zc = 'fav' if BRANCH_WX[z] in fav else ('av' if BRANCH_WX[z] in av else 'xian')
        ss={gc,zc}
        if ss=={'xian'}: lc='xian'
        elif 'av' in ss and 'fav' not in ss: lc='av' if ss=={'av'} else 'av_l'
        elif 'fav' in ss and 'av' not in ss: lc='fav' if 'xian' not in ss else 'fav_l'
        else: lc='mix'
        
        # V5.1-V2修正
        if lc and lc.startswith('av') and _spec in ('衰极','太衰','衰'):
            _dmwW=WUXING[dm]; _SHENG_ME_W={v:k for k,v in SHENG.items()}
            _yinbi={_dmwW, _SHENG_ME_W.get(_dmwW)}
            _ppY='/'.join(paths)
            if not any(x in _ppY for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI')):
                _is_yinbi = (GAN_WX.get(g) in _yinbi) or (BRANCH_WX.get(z) in _yinbi)
                if _is_yinbi:
                    _xiaoshen_duoshi = False
                    if GAN_WX.get(g) == _SHENG_ME_W.get(_dmwW):
                        _shi_wx = {v:k for k,v in SHENG.items()}.get(_dmwW)
                        for _fg, _fz in fp:
                            if GAN_WX.get(_fg) == _shi_wx:
                                _xiaoshen_duoshi = True
                                break
                    if not _xiaoshen_duoshi:
                        lc = 'fav_l' if lc == 'av_l' else 'fav'
        
        if lc in ('mix','xian'): continue
        expect='ji' if lc.startswith('fav') else 'xiong'
        
        # 互动级检测
        tp = build_transit_power(p, [gz])
        clash = [c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
        ju = tp.get('heju_verdict') or ''
        cf = tp.get('combination_facts', {}) or {}
        
        _has_substantive = False
        if clash:
            _has_substantive = any('拔' in c or '发' in c for c in clash)
        if ju:
            _has_substantive = True
        
        # 三刑六害六合
        if not _has_substantive:
            _BRANCH_BENQI = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
            _dm_wx = WUXING[dm]
            _key_branches = {fp[1][1], fp[2][1]}
            for _b in '子丑寅卯辰巳午未申酉戌亥':
                if _BRANCH_BENQI.get(_b) == _dm_wx:
                    _key_branches.add(_b)
            _all_branches = set('子丑寅卯辰巳午未申酉戌亥')
            _xing_hai_branches = set()
            for _s in (cf.get('sanxing') or []) + (cf.get('liuhai') or []):
                for _ch in _s:
                    if _ch in _all_branches:
                        _xing_hai_branches.add(_ch)
            if _xing_hai_branches & _key_branches:
                _has_substantive = True
            _LIUHE_PAIRS = {'子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯','辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'}
            _liuhe_partner = _LIUHE_PAIRS.get(z)
            if _liuhe_partner and _liuhe_partner in _key_branches:
                _has_substantive = True
        
        _candidates = {expect}
        if expect != v and _has_substantive:
            _opposite = 'xiong' if expect == 'ji' else 'ji'
            _candidates.add(_opposite)
        
        _hit_k = v in _candidates
        
        if not _hit_k:
            interaction_types = []
            if clash: interaction_types.append('六冲')
            if ju: interaction_types.append('会局')
            if cf.get('sanxing'): interaction_types.append('三刑')
            if cf.get('liuhai'): interaction_types.append('六害')
            if cf.get('liuhe'): interaction_types.append('六合')
            if cf.get('sanhe'): interaction_types.append('三合')
            if cf.get('liupo'): interaction_types.append('六破')
            if cf.get('zixing'): interaction_types.append('自刑')
            
            unhit_cases.append({
                'li': li, 'fp': fp, 'gz': gz, 'lc': lc, 'expect': expect, 'v': v,
                'prim': prim, 'fav': sorted(fav), 'av': sorted(av),
                'spectrum': _spec, 'paths': paths, 'special': ye.get('special'),
                'g_wx': GAN_WX[g], 'z_wx': BRANCH_WX[z],
                'gc': gc, 'zc': zc,
                'has_substantive': _has_substantive,
                'interaction_types': '+'.join(interaction_types) if interaction_types else '无互动',
                'clash': clash,
                'ju': ju,
            })

print(f"未命中案例总数: {len(unhit_cases)}")
print()

from collections import Counter
type_counter = Counter(c['interaction_types'] for c in unhit_cases)
print("=== 未命中案例互动类型分布 ===")
for itype, cnt in type_counter.most_common():
    print(f"  {itype}: {cnt}例")
print()

print("=== 未命中案例详细列表 ===")
for c in unhit_cases:
    fp_str = ''.join([g+z for g,z in c['fp']])
    print(f"  L{c['li']} {fp_str} 运{c['gz'][0]}{c['gz'][1]}[{c['lc']}] 原文{c['v']} | {c['interaction_types']}")
    print(f"    主{c['prim']} 喜{c['fav']} 忌{c['av']} 谱={c['spectrum']} 路径={c['paths']} 特殊={c['special']}")
    print(f"    干{c['g_wx']}({c['gc']}) 支{c['z_wx']}({c['zc']})")
    if c['clash']:
        print(f"    冲: {c['clash']}")
    if c['ju']:
        print(f"    会局: {c['ju']}")
    print()
