#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四轨并行大运喜忌原型验证
方向一：用神四轨→每轨独立判断大运喜忌→四轨输出并行→按优先级裁决
裁决规则：冬夏月调候轨优先，非冬夏月格局轨优先，格局破病药轨优先，从格/专旺格体用轨优先
"""
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
cases = mod.cases

WINTER = {'亥','子','丑'}
SUMMER = {'巳','午','未'}

def build_four_tracks(ye, f, p):
    """构造四轨独立的用神/avoid
    返回: {track_name: {'fav': set, 'av': set, 'activated': bool}}
    """
    dm = f['day_stem']
    dmw = WUXING[dm]
    mz = p['month'][1]
    spectrum = ye.get('spectrum_tier') or ''
    paths = ye.get('yongshen_paths') or []
    special = ye.get('special') or '正格'
    cands = ye.get('yongshen_candidates') or []
    
    # 十神映射
    SHENG_ME = {v:k for k,v in SHENG.items()}  # 生我者
    yin_wx = SHENG_ME.get(dmw)  # 印星五行
    bi_wx = dmw  # 比劫五行
    shi_wx = SHENG.get(dmw)  # 食伤五行
    cai_wx = KE.get(dmw)  # 财星五行
    guan_wx = KE.get(yin_wx) if yin_wx else None  # 官杀五行
    
    tracks = {}
    
    # ===== 轨1：调候轨（QIHOU）=====
    qihou_fav = set()
    qihou_av = set()
    qihou_activated = False
    for c in cands:
        if c.get('path') == 'QIHOU':
            qihou_fav.add(c.get('wuxing'))
            qihou_activated = True
    # 调候忌神：克调候用神的五行
    for fav in qihou_fav:
        ke_fav = KE.get(fav)
        if ke_fav: qihou_av.add(ke_fav)
    tracks['QIHOU'] = {'fav': qihou_fav, 'av': qihou_av, 'activated': qihou_activated}
    
    # ===== 轨2：格局轨（ZPZQ）=====
    # 正格：月令十神为用神（月令所藏透干之神）
    # 简化版：月令本气对应的十神为格局用神
    geju_fav = set()
    geju_av = set()
    geju_activated = False
    
    # 月令本气五行
    month_benqi = BRANCH_WX.get(mz)
    if month_benqi and special == '正格':
        # 月令本气对应的十神类型
        if month_benqi == yin_wx:  # 印格
            geju_fav.add(yin_wx)  # 用印
            geju_fav.add(bi_wx)  # 用比劫帮身
            geju_av.add(cai_wx) if cai_wx else None  # 忌财坏印
            geju_av.add(shi_wx) if shi_wx else None  # 忌食伤泄印
        elif month_benqi == bi_wx:  # 比劫格（建禄/羊刃）
            geju_fav.add(guan_wx) if guan_wx else None  # 用官杀制比劫
            geju_fav.add(shi_wx) if shi_wx else None  # 用食伤泄秀
            geju_av.add(yin_wx) if yin_wx else None  # 忌印生比劫
        elif month_benqi == shi_wx:  # 食伤格
            geju_fav.add(cai_wx) if cai_wx else None  # 用财（食伤生财）
            geju_fav.add(guan_wx) if guan_wx else None  # 用官杀（伤官佩印/食神制杀）
            geju_av.add(yin_wx) if yin_wx else None  # 忌印克食伤
        elif month_benqi == cai_wx:  # 财格
            geju_fav.add(guan_wx) if guan_wx else None  # 用官杀（财生官）
            geju_fav.add(shi_wx) if shi_wx else None  # 用食伤（食伤生财）
            geju_av.add(bi_wx)  # 忌比劫夺财
        elif month_benqi == guan_wx:  # 官杀格
            geju_fav.add(yin_wx) if yin_wx else None  # 用印（官杀生印）
            geju_fav.add(bi_wx)  # 用比劫帮身
            geju_av.add(cai_wx) if cai_wx else None  # 忌财生官杀
            geju_av.add(shi_wx) if shi_wx else None  # 忌食伤克官杀
        geju_activated = True
    
    # 从格/专旺格：格局轨不激活（用体用轨）
    if special != '正格':
        geju_activated = False
    
    tracks['ZPZQ'] = {'fav': geju_fav, 'av': geju_av, 'activated': geju_activated}
    
    # ===== 轨3：病药轨（SFTK）=====
    bingyao_fav = set()
    bingyao_av = set()
    bingyao_activated = False
    for c in cands:
        if c.get('path') == 'BINGYAO':
            bingyao_fav.add(c.get('wuxing'))
            bingyao_activated = True
    # 病药忌神：病神（克药神的五行，或原局过旺的五行）
    for fav in bingyao_fav:
        ke_fav = KE.get(fav)
        if ke_fav: bingyao_av.add(ke_fav)
    tracks['SFTK'] = {'fav': bingyao_fav, 'av': bingyao_av, 'activated': bingyao_activated}
    
    # ===== 轨4：体用轨（DTS）=====
    # 扶抑用神：身弱用印比，身旺用克泄耗
    tiyong_fav = set()
    tiyong_av = set()
    tiyong_activated = False
    
    if spectrum in ('衰','太衰','衰极'):  # 身弱
        tiyong_fav.add(yin_wx) if yin_wx else None  # 用印生身
        tiyong_fav.add(bi_wx)  # 用比劫帮身
        tiyong_av.add(guan_wx) if guan_wx else None  # 忌官杀克身
        tiyong_av.add(cai_wx) if cai_wx else None  # 忌财耗身
        tiyong_av.add(shi_wx) if shi_wx else None  # 忌食伤泄身
        tiyong_activated = True
    elif spectrum in ('旺','太旺','旺极'):  # 身旺
        tiyong_fav.add(guan_wx) if guan_wx else None  # 用官杀制身
        tiyong_fav.add(cai_wx) if cai_wx else None  # 用财耗身
        tiyong_fav.add(shi_wx) if shi_wx else None  # 用食伤泄身
        tiyong_av.add(yin_wx) if yin_wx else None  # 忌印生身
        tiyong_av.add(bi_wx)  # 忌比劫帮身
        tiyong_activated = True
    elif spectrum == '中和':  # 中和
        # 中和不激活体用轨（用调候或格局）
        tiyong_activated = False
    
    # 从格/专旺格：体用轨激活（顺势）
    if special != '正格':
        # 从格顺势：用从之神
        if 'CONG' in '/'.join(paths):
            # 从财格：用财食伤；从杀格：用官杀财；从儿格：用食伤财
            if special and '财' in special:
                tiyong_fav.add(cai_wx) if cai_wx else None
                tiyong_fav.add(shi_wx) if shi_wx else None
            elif special and ('杀' in special or '官' in special):
                tiyong_fav.add(guan_wx) if guan_wx else None
                tiyong_fav.add(cai_wx) if cai_wx else None
            elif special and ('儿' in special or '食' in special):
                tiyong_fav.add(shi_wx) if shi_wx else None
                tiyong_fav.add(cai_wx) if cai_wx else None
            tiyong_activated = True
        elif 'ZHUANWANG' in '/'.join(paths):
            # 专旺格：用比劫食伤（顺势）
            tiyong_fav.add(bi_wx)
            tiyong_fav.add(shi_wx) if shi_wx else None
            tiyong_activated = True
    
    tracks['DTS'] = {'fav': tiyong_fav, 'av': tiyong_av, 'activated': tiyong_activated}
    
    return tracks

def four_track_verdict(tracks, g_wx, z_wx, mz, special, paths):
    """四轨并行大运喜忌判断+优先级裁决
    返回: (final_result, track_results, priority_track)
    """
    # 每轨独立判断
    track_results = {}
    for name, track in tracks.items():
        if not track['activated']:
            track_results[name] = None
            continue
        gc = cls_w(g_wx, track['fav'], track['av'])
        zc = cls_w(z_wx, track['fav'], track['av'])
        ss = {gc, zc}
        if ss == {'xian'}:
            result = 'xian'
        elif 'av' in ss and 'fav' not in ss:
            result = 'av' if ss == {'av'} else 'av_l'
        elif 'fav' in ss and 'av' not in ss:
            result = 'fav' if 'xian' not in ss else 'fav_l'
        else:
            result = 'mix'
        track_results[name] = result
    
    # 优先级裁决（V2修正版）
    # 核心原则：正格案例不用体用轨兜底，体用轨只在从格/专旺格使用
    # 1. 从格/专旺格：体用轨优先（顺势）
    # 2. 冬夏月：调候轨优先
    # 3. 非冬夏月：格局轨优先
    # 4. 病药轨：有病时优先于格局轨
    # 5. 兜底：调候轨（正格案例不用体用轨兜底）
    
    priority_track = None
    
    # 从格/专旺格：体用轨优先（顺势）
    if special != '正格':
        if tracks['DTS']['activated'] and track_results['DTS'] not in (None, 'xian', 'mix'):
            priority_track = 'DTS'
    
    # 冬夏月：调候轨优先（正格案例）
    if priority_track is None and special == '正格' and mz in (WINTER | SUMMER):
        if tracks['QIHOU']['activated'] and track_results['QIHOU'] not in (None, 'xian', 'mix'):
            priority_track = 'QIHOU'
    
    # 病药轨：有病时优先于格局轨（正格案例）
    if priority_track is None and special == '正格' and tracks['SFTK']['activated'] and track_results['SFTK'] not in (None, 'xian', 'mix'):
        priority_track = 'SFTK'
    
    # 非冬夏月：格局轨优先（正格案例）
    if priority_track is None and special == '正格' and mz not in (WINTER | SUMMER):
        if tracks['ZPZQ']['activated'] and track_results['ZPZQ'] not in (None, 'xian', 'mix'):
            priority_track = 'ZPZQ'
    
    # 兜底：调候轨（正格案例不用体用轨兜底）
    if priority_track is None and special == '正格':
        if tracks['QIHOU']['activated'] and track_results['QIHOU'] not in (None, 'xian', 'mix'):
            priority_track = 'QIHOU'
        # 正格案例不用体用轨兜底，体用轨只在从格/专旺格使用
    
    # 最终结果
    if priority_track and track_results[priority_track]:
        final_result = track_results[priority_track]
    else:
        # 所有轨都无法判断，用中性
        final_result = 'xian'
    
    return final_result, track_results, priority_track

# 运行验证
st = {'judgable':0, 'agree':0, 'dis':0, 'neutral':0, 'four_track_changed':0}
track_usage = {'QIHOU':0, 'ZPZQ':0, 'SFTK':0, 'DTS':0, 'None':0}

for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    
    dm = f['day_stem']
    _spec = ye.get('spectrum_tier') or ''
    paths = ye.get('yongshen_paths') or []
    special = ye.get('special') or '正格'
    mz = p['month'][1]
    
    # 构造四轨
    tracks = build_four_tracks(ye, f, p)
    
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'): v = None
        if not v or v in ('hun', 'lao'): continue
        
        g_wx = GAN_WX[g]
        z_wx = BRANCH_WX[z]
        
        # 四轨并行判断
        final_result, track_results, priority_track = four_track_verdict(tracks, g_wx, z_wx, mz, special, paths)
        
        if priority_track:
            track_usage[priority_track] += 1
        else:
            track_usage['None'] += 1
        
        if final_result in ('mix', 'xian'):
            st['neutral'] += 1
            continue
        
        st['judgable'] += 1
        expect = 'ji' if final_result.startswith('fav') else 'xiong'
        
        if expect == v:
            st['agree'] += 1
        else:
            st['dis'] += 1
            # 检查四轨是否改变了原判断
            # 原判断（单一用神）
            prim = ye.get('yongshen_primary') or ''
            fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
            av = set(ye.get('yongshen_avoid') or [])
            gc_old = cls_w(g_wx, fav, av)
            zc_old = cls_w(z_wx, fav, av)
            ss_old = {gc_old, zc_old}
            if ss_old == {'xian'}: lc_old = 'xian'
            elif 'av' in ss_old and 'fav' not in ss_old: lc_old = 'av' if ss_old == {'av'} else 'av_l'
            elif 'fav' in ss_old and 'av' not in ss_old: lc_old = 'fav' if 'xian' not in ss_old else 'fav_l'
            else: lc_old = 'mix'
            
            if lc_old != final_result and lc_old not in ('mix', 'xian'):
                st['four_track_changed'] += 1

print("=" * 80)
print("【四轨并行大运喜忌原型验证结果】")
print("=" * 80)
if st['judgable']:
    print(f"可判: {st['judgable']}例")
    print(f"一致: {st['agree']}例 ({100*st['agree']/st['judgable']:.1f}%)")
    print(f"不一致: {st['dis']}例 ({100*st['dis']/st['judgable']:.1f}%)")
    print(f"中性: {st['neutral']}例")
    print(f"四轨改变原判断的案例数: {st['four_track_changed']}例")
print()
print("【优先级轨使用分布】")
for track, cnt in track_usage.items():
    print(f"  {track}: {cnt}例 ({100*cnt/sum(track_usage.values()):.1f}%)" if sum(track_usage.values()) else f"  {track}: {cnt}例")
print()
print("【与原单一用神判断对比】")
print(f"  原单一对齐率: 69.8% (196/281)")
if st['judgable']:
    print(f"  四轨并行对齐率: {100*st['agree']/st['judgable']:.1f}% ({st['agree']}/{st['judgable']})")
    diff = 100*st['agree']/st['judgable'] - 69.8
    print(f"  差异: {diff:+.1f}pp")
