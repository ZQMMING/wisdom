#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盲测验证V2: 用神案例JSONL大运层案例(非DTS)验证单一对齐率和命中率@K
数据来源: D:\顺天系统资料\用神案例JSONL\大运层\all.jsonl (215例, 非DTS 84例)
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

import json

# 读取大运层案例
all_cases = []
with open(r'D:\顺天系统资料\用神案例JSONL\大运层\all.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            d = json.loads(line)
            all_cases.append(d)
        except: pass

print(f"大运层总案例数: {len(all_cases)}")

# 按书分类
from collections import Counter
book_counter = Counter(d.get('book','') for d in all_cases)
print("\n【按书分类】")
for book, cnt in book_counter.most_common():
    print(f"  {book}: {cnt}例")

# 筛选非DTS案例
non_dts_cases = [d for d in all_cases if 'DTS' not in d.get('book','')]
print(f"\n非DTS案例数: {len(non_dts_cases)}")

# 解析八字
def parse_chart(chart_str):
    if not chart_str: return None
    parts = chart_str.replace(' ', '').replace('\n', '')
    if len(parts) < 8: return None
    stems = parts[0::2][:4]
    branches = parts[1::2][:4]
    if len(stems) < 4 or len(branches) < 4: return None
    return list(zip(stems, branches))

# 运行盲测
st = {'judgable':0, 'agree':0, 'dis':0, 'neutral':0, 'hit_k_agree':0, 'hit_k_dis':0, 'hit_k_interaction':0}
book_stats = {}

for ci, case in enumerate(non_dts_cases):
    book = case.get('book','')
    chart = case.get('bazi','')
    dayun_list = case.get('dayun', [])
    raw = case.get('raw','')
    # 如果dayun字段为空, 从raw第二行提取大运
    if not dayun_list:
        raw_lines = raw.strip().split('\n')
        if len(raw_lines) >= 2:
            dayun_line = raw_lines[1].strip()
            dayun_list = dayun_line.split()
    
    fp = parse_chart(chart)
    if not fp: continue
    if not dayun_list or len(dayun_list) < 2: continue
    
    # 解析大运
    dy = []
    for dy_str in dayun_list:
        dy_str = dy_str.replace(' ', '')
        if len(dy_str) >= 2:
            g, z = dy_str[0], dy_str[1]
            if g in '甲乙丙丁戊己庚辛壬癸' and z in '子丑寅卯辰巳午未申酉戌亥':
                dy.append((g, z))
    
    if len(dy) < 2: continue
    
    try:
        p, f, ye, tp0 = engine(fp)
    except: continue
    
    prim = ye.get('yongshen_primary') or ''
    fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av = set(ye.get('yongshen_avoid') or [])
    dm = f['day_stem']
    _spec = ye.get('spectrum_tier') or ''
    paths = ye.get('yongshen_paths', [])
    
    if book not in book_stats:
        book_stats[book] = {'judgable':0, 'agree':0, 'dis':0, 'hit_k_agree':0, 'hit_k_dis':0}
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(raw, g, z)
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
        
        if lc in ('mix','xian'):
            st['neutral']+=1
            book_stats[book]['neutral'] = book_stats[book].get('neutral',0) + 1
            continue
        
        st['judgable']+=1
        book_stats[book]['judgable']+=1
        expect='ji' if lc.startswith('fav') else 'xiong'
        
        # 命中率@K (与对齐脚本一致的实质性互动检测)
        tp = build_transit_power(p, [gz])
        clash = [c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
        ju = tp.get('heju_verdict') or ''
        
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
        
        _candidates = {expect}
        if expect != v and _has_substantive:
            _opposite = 'xiong' if expect == 'ji' else 'ji'
            _candidates.add(_opposite)
            st['hit_k_interaction'] += 1
        
        _hit_k = v in _candidates
        if _hit_k:
            st['hit_k_agree'] += 1
            book_stats[book]['hit_k_agree'] += 1
        else:
            st['hit_k_dis'] += 1
            book_stats[book]['hit_k_dis'] += 1
        
        if expect==v:
            st['agree']+=1
            book_stats[book]['agree']+=1
        else:
            st['dis']+=1
            book_stats[book]['dis']+=1

print("\n" + "=" * 80)
print("【盲测结果 - 非DTS大运层案例】")
print("=" * 80)
if st['judgable']:
    print(f"可判: {st['judgable']}例")
    print(f"单一对齐率: {st['agree']}/{st['judgable']} = {100*st['agree']/st['judgable']:.1f}%")
    print(f"命中率@K: {st['hit_k_agree']}/{st['judgable']} = {100*st['hit_k_agree']/st['judgable']:.1f}%")
    print(f"中性: {st['neutral']}例")
    print(f"互动级影响: {st['hit_k_interaction']}例")

print("\n【按书分类盲测结果】")
for book, bs in sorted(book_stats.items()):
    if bs['judgable'] > 0:
        print(f"  {book}: 可判{bs['judgable']}例, 单一对齐{100*bs['agree']/bs['judgable']:.1f}%, 命中率@K {100*bs['hit_k_agree']/bs['judgable']:.1f}%")

print("\n【与DTS对比】")
print(f"  DTS单一对齐率: 69.4%")
print(f"  DTS命中率@K: 96.2%")
if st['judgable']:
    print(f"  非DTS单一对齐率: {100*st['agree']/st['judgable']:.1f}%")
    print(f"  非DTS命中率@K: {100*st['hit_k_agree']/st['judgable']:.1f}%")
    _diff_single = 100*st['agree']/st['judgable'] - 69.4
    _diff_hitk = 100*st['hit_k_agree']/st['judgable'] - 96.2
    print(f"  单一对齐率差异: {_diff_single:+.1f}pp")
    print(f"  命中率@K差异: {_diff_hitk:+.1f}pp")
    if abs(_diff_single) < 15:
        print("  结论: 单一对齐率差异<15pp, 无显著过拟合, 69.4%是架构真实能力")
    else:
        print("  结论: 单一对齐率差异>=15pp, 可能存在过拟合")
