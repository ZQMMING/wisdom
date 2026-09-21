#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""方向二：十干级大运喜忌判断原型验证
核心思路：大运天干 == 调候候选天干 → 喜/忌（十干级），而非大运五行 ∈ fav/avoid（五行级）
依据：五行是"类"，十干是"质"，同一类下不同质作用机制完全不同（壬水冲奔泛滥vs癸水渗透滋润）
"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
sys.path.insert(0, 'engines/common')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

engine = mod.engine
GAN_WX = mod.GAN_WX
BRANCH_WX = mod.BRANCH_WX
WUXING = mod.WUXING
KE = mod.KE
luck_verdict = mod.luck_verdict
cases = mod.cases

from qtbj_climate_candidates import build_climate_candidates

# 天干克关系：甲克戊，乙克己，丙克庚，丁克辛，戊克壬，己克癸，庚克甲，辛克乙，壬克丙，癸克丁
GAN_KE = {
    '甲': '戊', '乙': '己', '丙': '庚', '丁': '辛', '戊': '壬',
    '己': '癸', '庚': '甲', '辛': '乙', '壬': '丙', '癸': '丁',
}
# 天干生关系：甲生丙，乙生丁，丙生戊，丁生己，戊生庚，己生辛，庚生壬，辛生癸，壬生甲，癸生乙
GAN_SHENG = {
    '甲': '丙', '乙': '丁', '丙': '戊', '丁': '己', '戊': '庚',
    '己': '辛', '庚': '壬', '辛': '癸', '壬': '甲', '癸': '乙',
}

def stem_level_verdict(g, z, climate_stems, dm, mz):
    """十干级大运喜忌判断
    g: 大运天干, z: 大运地支
    climate_stems: 调候候选天干列表（按次序排列）
    返回: 'fav' / 'av' / 'xian' / 'fav_l' / 'av_l'
    """
    if not climate_stems:
        return 'xian'
    
    primary_stem = climate_stems[0]  # 第一调候用神
    secondary_stems = climate_stems[1:]  # 次要调候用神
    
    # 大运天干判断
    if g == primary_stem:
        g_result = 'fav'  # 第一调候用神到位，大喜
    elif g in secondary_stems:
        g_result = 'fav_l'  # 次要调候用神到位，小喜
    elif g == GAN_KE.get(primary_stem):
        g_result = 'av'  # 克第一调候用神，大忌
    elif any(g == GAN_KE.get(s) for s in secondary_stems):
        g_result = 'av_l'  # 克次要调候用神，小忌
    else:
        g_result = 'xian'  # 中性
    
    # 大运地支判断（五行级，因为地支没有天干级调候候选）
    # 地支五行 == 调候用神五行 → fav
    # 地支五行 == 克调候用神五行 → av
    primary_wx = WUXING.get(primary_stem)
    z_wx = BRANCH_WX.get(z)
    if primary_wx and z_wx:
        if z_wx == primary_wx:
            z_result = 'fav_l'
        elif z_wx == KE.get(primary_wx):
            z_result = 'av_l'
        else:
            z_result = 'xian'
    else:
        z_result = 'xian'
    
    # 综合天干地支判断
    results = {g_result, z_result}
    if results == {'xian'}:
        return 'xian'
    elif 'av' in results and 'fav' not in results:
        return 'av' if results == {'av'} else 'av_l'
    elif 'fav' in results and 'av' not in results:
        return 'fav' if 'xian' not in results else 'fav_l'
    else:
        return 'mix'

# 运行验证
st = {'judgable':0, 'agree':0, 'dis':0, 'neutral':0, 'stem_level_changed':0}
climate_registered = 0
climate_not_registered = 0

for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    
    dm = f['day_stem']
    mz = p['month'][1]
    
    # 获取天干级调候候选
    clc = build_climate_candidates(f)
    if clc.get('state') == 'REGISTERED':
        climate_registered += 1
        climate_stems = [c['stem'] for c in clc.get('climate_candidates', [])]
    else:
        climate_not_registered += 1
        climate_stems = []
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'): v = None
        if not v or v in ('hun', 'lao'): continue
        
        # 十干级判断
        stem_result = stem_level_verdict(g, z, climate_stems, dm, mz)
        
        # 原五行级判断（用于对比）
        prim = ye.get('yongshen_primary') or ''
        fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
        av = set(ye.get('yongshen_avoid') or [])
        gc_old = 'fav' if GAN_WX[g] in fav else ('av' if GAN_WX[g] in av else 'xian')
        zc_old = 'fav' if BRANCH_WX[z] in fav else ('av' if BRANCH_WX[z] in av else 'xian')
        ss_old = {gc_old, zc_old}
        if ss_old == {'xian'}: lc_old = 'xian'
        elif 'av' in ss_old and 'fav' not in ss_old: lc_old = 'av' if ss_old == {'av'} else 'av_l'
        elif 'fav' in ss_old and 'av' not in ss_old: lc_old = 'fav' if 'xian' not in ss_old else 'fav_l'
        else: lc_old = 'mix'
        
        if stem_result in ('mix', 'xian'):
            st['neutral'] += 1
            continue
        
        st['judgable'] += 1
        expect = 'ji' if stem_result.startswith('fav') else 'xiong'
        
        if expect == v:
            st['agree'] += 1
        else:
            st['dis'] += 1
        
        # 检查十干级是否改变了原判断
        if lc_old != stem_result and lc_old not in ('mix', 'xian'):
            st['stem_level_changed'] += 1

print("=" * 80)
print("【方向二：十干级大运喜忌判断原型验证结果】")
print("=" * 80)
print(f"调候候选已注册: {climate_registered}例")
print(f"调候候选未注册: {climate_not_registered}例")
print()
if st['judgable']:
    print(f"可判: {st['judgable']}例")
    print(f"一致: {st['agree']}例 ({100*st['agree']/st['judgable']:.1f}%)")
    print(f"不一致: {st['dis']}例 ({100*st['dis']/st['judgable']:.1f}%)")
    print(f"中性: {st['neutral']}例")
    print(f"十干级改变原判断的案例数: {st['stem_level_changed']}例")
print()
print("【与原五行级判断对比】")
print(f"  原五行级单一对齐率: 69.8% (196/281)")
if st['judgable']:
    print(f"  十干级单一对齐率: {100*st['agree']/st['judgable']:.1f}% ({st['agree']}/{st['judgable']})")
    diff = 100*st['agree']/st['judgable'] - 69.8
    print(f"  差异: {diff:+.1f}pp")
