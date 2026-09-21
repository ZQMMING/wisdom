#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""45例未命中案例分类诊断
A类: 元素级错判(无任何互动级影响, 元素级判断根本反了)
B类: 互动级未覆盖(有互动级影响但类型不在当前覆盖范围: 刑/害/破/三合三会/合化等)
C类: 原典模糊(原典标准本身不确定或前后矛盾)
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

unhit_cases = []

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
        
        # 计算lc (简化版, 与对齐脚本一致)
        lc = None
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
        
        # 检测实质性互动(当前覆盖范围: 冲非两停/会局主导)
        tp = build_transit_power(p, [gz])
        clash = [c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
        ju = tp.get('heju_verdict') or ''
        
        _has_substantive = False
        if clash:
            _has_substantive = any('拔' in c or '发' in c for c in clash)
        if ju:
            _has_substantive = True
        
        # 未命中: 元素级与原典不一致且无实质性互动
        if expect != v and not _has_substantive:
            # 检测其他互动级影响(B类候选)
            combination_facts = tp.get('combination_facts', {})
            _has_hehua = bool(combination_facts)
            _has_sanhe = any('三合' in str(combination_facts.get(k,'')) for k in combination_facts) if combination_facts else False
            _has_sanhui = any('三会' in str(combination_facts.get(k,'')) for k in combination_facts) if combination_facts else False
            _has_liuhe = any('六合' in str(combination_facts.get(k,'')) for k in combination_facts) if combination_facts else False
            
            # 检测刑/害/破(需要从其他地方获取, 暂时标记为待检测)
            _has_xing = False  # 待实现
            _has_hai = False   # 待实现
            _has_po = False    # 待实现
            
            _other_interaction = _has_hehua or _has_sanhe or _has_sanhui or _has_liuhe or _has_xing or _has_hai or _has_po
            
            # 分类
            if _other_interaction:
                category = 'B'  # 互动级未覆盖
            else:
                category = 'A'  # 元素级错判(无任何互动级影响)
            
            # C类检测: 原典模糊(原文中同时提到吉和凶, 或表述不确定)
            blob_text = blob or ''
            _has_both_ji_xiong = ('吉' in blob_text and '凶' in blob_text) or ('发' in blob_text and '败' in blob_text)
            _has_uncertain = any(w in blob_text for w in ['可能','似乎','大概','未必','难说'])
            if _has_both_ji_xiong or _has_uncertain:
                category = 'C'  # 原典模糊
            
            matrix = build_branch_role_matrix(fp, ye, f)
            
            unhit_cases.append({
                'case_id': f'L{li+1}',
                'chart': ''.join(a+b for a,b in fp),
                'daymaster': dm,
                'tier': tier,
                'paths': paths,
                'dayun': gz,
                'gc': gc,
                'zc': zc,
                'lc': lc,
                'expect': expect,
                'original': v,
                'fav': sorted(fav),
                'avoid': sorted(av),
                'primary': prim,
                'clash': clash,
                'ju': ju,
                'combination_facts': combination_facts,
                'has_hehua': _has_hehua,
                'has_sanhe': _has_sanhe,
                'has_sanhui': _has_sanhui,
                'has_liuhe': _has_liuhe,
                'category': category,
                'blob': blob[:100] if blob else '',
                'matrix': matrix,
            })

print(f"未命中案例总数: {len(unhit_cases)}")
print()

from collections import Counter
category_counter = Counter(c['category'] for c in unhit_cases)
print("【分类统计】")
for cat, cnt in category_counter.most_common():
    cat_name = {'A': 'A类-元素级错判', 'B': 'B类-互动级未覆盖', 'C': 'C类-原典模糊'}[cat]
    print(f"  {cat_name}: {cnt}例 ({100*cnt/len(unhit_cases):.1f}%)")

print()
print("=" * 80)
print("【B类-互动级未覆盖 详细】")
print("=" * 80)
b_cases = [c for c in unhit_cases if c['category'] == 'B']
for i, c in enumerate(b_cases, 1):
    print(f"\n{i}. {c['case_id']} {c['chart']} 日主{c['daymaster']} tier={c['tier']}")
    print(f"   大运{c['dayun']} lc={c['lc']} expect={c['expect']} 原典={c['original']}")
    print(f"   合化={c['has_hehua']} 三合={c['has_sanhe']} 三会={c['has_sanhui']} 六合={c['has_liuhe']}")
    print(f"   combination_facts={c['combination_facts']}")
    print(f"   原文={c['blob']}")

print()
print("=" * 80)
print("【A类-元素级错判 详细】")
print("=" * 80)
a_cases = [c for c in unhit_cases if c['category'] == 'A']
for i, c in enumerate(a_cases[:15], 1):
    print(f"\n{i}. {c['case_id']} {c['chart']} 日主{c['daymaster']} tier={c['tier']} paths={c['paths']}")
    print(f"   大运{c['dayun']} gc={c['gc']} zc={c['zc']} lc={c['lc']} expect={c['expect']} 原典={c['original']}")
    print(f"   primary={c['primary']} fav={c['fav']} avoid={c['avoid']}")
    print(f"   原文={c['blob']}")

print()
print("=" * 80)
print("【C类-原典模糊 详细】")
print("=" * 80)
c_cases = [c for c in unhit_cases if c['category'] == 'C']
for i, c in enumerate(c_cases, 1):
    print(f"\n{i}. {c['case_id']} {c['chart']} 大运{c['dayun']} 原典={c['original']}")
    print(f"   原文={c['blob']}")
