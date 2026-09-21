#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深入分析12个未命中案例，特别是3个"无互动"案例"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

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
cases = mod.cases

# 收集未命中案例
unhit_cases = []
for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    prim = ye.get('yongshen_primary') or ''
    fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av = set(ye.get('yongshen_avoid') or [])
    dm = f['day_stem']
    _spec = ye.get('spectrum_tier') or ''
    paths = ye.get('yongshen_paths') or []
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'): v = None
        if not v or v in ('hun', 'lao'): continue
        
        gc = cls_w(GAN_WX[g], fav, av)
        zc = cls_w(BRANCH_WX[z], fav, av)
        
        # V5.1修正版
        if _spec in ('衰极','太衰','衰'):
            _dmwW=WUXING[dm]; _SHENG_ME_W={v:k for k,v in SHENG.items()}
            _yinbi={_dmwW, _SHENG_ME_W.get(_dmwW)}
            _ppY='/'.join(paths)
            if not any(x in _ppY for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI')):
                _is_yinbi = (GAN_WX.get(g) in _yinbi) or (BRANCH_WX.get(z) in _yinbi)
                if _is_yinbi and (gc=='av' or zc=='av'):
                    gc = 'fav' if gc=='av' else gc
                    zc = 'fav' if zc=='av' else zc
        
        ss={gc,zc}
        if ss=={'xian'}: lc='xian'
        elif 'av' in ss and 'fav' not in ss: lc='av' if ss=={'av'} else 'av_l'
        elif 'fav' in ss and 'av' not in ss: lc='fav' if 'xian' not in ss else 'fav_l'
        else: lc='mix'
        
        if lc in ('mix','xian'): continue
        
        expect='ji' if lc.startswith('fav') else 'xiong'
        
        # 检查互动级
        tp = build_transit_power(p, [gz])
        clash = [c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
        ju = tp.get('heju_verdict') or ''
        
        # 实质性互动检测
        _has_substantive = False
        if clash:
            _has_substantive = any('拔' in c or '发' in c for c in clash)
        if ju:
            _has_substantive = True
        
        # 三刑+六害
        if not _has_substantive:
            _BRANCH_BENQI = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}
            _dm_wx = WUXING[dm]
            _month_branch = fp[1][1]
            _day_branch = fp[2][1]
            _key_branches = {_month_branch, _day_branch}
            for _b in '子丑寅卯辰巳午未申酉戌亥':
                if _BRANCH_BENQI.get(_b) == _dm_wx:
                    _key_branches.add(_b)
            _sanxing = tp.get('combination_facts', {}).get('sanxing', [])
            _liuhai = tp.get('combination_facts', {}).get('liuhai', [])
            _all_branches = set('子丑寅卯辰巳午未申酉戌亥')
            _xing_hai_branches = set()
            for _s in _sanxing + _liuhai:
                for _ch in _s:
                    if _ch in _all_branches:
                        _xing_hai_branches.add(_ch)
            if _xing_hai_branches & _key_branches:
                _has_substantive = True
        
        # 六合
        if not _has_substantive:
            _LIUHE_PAIRS = {'子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯','辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'}
            _dayun_branch = z
            _liuhe_partner = _LIUHE_PAIRS.get(_dayun_branch)
            if _liuhe_partner and _liuhe_partner in _key_branches:
                _has_substantive = True
        
        # 候选集
        _candidates = {expect}
        if expect != v and _has_substantive:
            _opposite = 'xiong' if expect == 'ji' else 'ji'
            _candidates.add(_opposite)
        
        _hit_k = v in _candidates
        
        if not _hit_k:
            # 收集所有互动类型
            interaction_types = []
            if clash: interaction_types.append('六冲')
            if ju: interaction_types.append('会局')
            cf = tp.get('combination_facts', {}) or {}
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

# 按互动类型分类
from collections import Counter
type_counter = Counter(c['interaction_types'] for c in unhit_cases)
print("=== 未命中案例互动类型分布 ===")
for itype, cnt in type_counter.most_common():
    print(f"  {itype}: {cnt}例")
print()

# 详细分析"无互动"案例
print("=== 无互动案例详细分析 ===")
no_interaction = [c for c in unhit_cases if c['interaction_types'] == '无互动']
for c in no_interaction:
    fp_str = ''.join([g+z for g,z in c['fp']])
    print(f"  L{c['li']} {fp_str} 运{c['gz'][0]}{c['gz'][1]}[{c['lc']}] 原文{c['v']}")
    print(f"    主{c['prim']} 喜{c['fav']} 忌{c['av']}")
    print(f"    干{c['g_wx']}({c['gc']}) 支{c['z_wx']}({c['zc']})")
    print(f"    谱={c['spectrum']} 路径={c['paths']} 特殊={c['special']}")
    print()
