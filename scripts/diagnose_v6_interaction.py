#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V6.x 互动级判断诊断脚本
导出fav->xiong中冲原局且被冲地支是fav的8例完整数据，按机制分类。
"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from dayun_align import cases, engine, cls_w, GAN_WX, BRANCH_WX, WUXING, SHENG, KE, luck_verdict, transit_clash_verdicts

LIU_CHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅',
             '卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}

HIDDEN_STEMS = {
    '子':['癸'], '丑':['己','癸','辛'], '寅':['甲','丙','戊'], '卯':['乙'],
    '辰':['戊','乙','癸'], '巳':['丙','戊','庚'], '午':['丁','己'], '未':['己','丁','乙'],
    '申':['庚','壬','戊'], '酉':['辛'], '戌':['戊','辛','丁'], '亥':['壬','甲'],
}

MU_KU = {'辰','戌','丑','未'}  # 墓库

def get_stem_role(stem, pillars, daymaster):
    """判断天干的角色：透干位置"""
    roles = []
    for pos, (g, z) in pillars.items():
        if g == stem:
            roles.append(pos + '干')
    return roles

def diagnose():
    from dayun_align import cases as _cases, engine as _engine, cls_w as _cls_w, GAN_WX as _GAN_WX, BRANCH_WX as _BRANCH_WX, WUXING as _WUXING, SHENG as _SHENG, KE as _KE, luck_verdict as _luck_verdict, transit_clash_verdicts as _transit_clash_verdicts
    results = []
    for li, fp, dy, txt in _cases:
        if len(dy) < 4: continue
        try: p, f, ye, tp0 = _engine(fp)
        except: continue
        prim = ye.get('yongshen_primary') or ''
        fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
        av = set(ye.get('yongshen_avoid') or [])
        dm = f['day_stem']
        dmw = _WUXING[dm]
        pillars = {'年':fp[0], '月':fp[1], '日':fp[2], '时':fp[3]}
        yuan_branches = {'年':fp[0][1], '月':fp[1][1], '日':fp[2][1], '时':fp[3][1]}
        
        for gz in dy:
            g, z = gz[0], gz[1]
            v, blob = _luck_verdict(txt, g, z)
            if blob and blob.lstrip().startswith('【原注】'): v = None
            if not v or v in ('hun', 'lao'): continue
            gc = _cls_w(_GAN_WX[g], fav, av)
            zc = _cls_w(_BRANCH_WX[z], fav, av)
            ss = {gc, zc}
            if not (ss == {'fav'} or ('fav' in ss and 'av' not in ss)): continue
            if v != 'xiong': continue
            
            # 检查大运地支是否冲原局某支
            for pos, bz in yuan_branches.items():
                if LIU_CHONG.get(z) == bz:
                    bz_wx = _BRANCH_WX[bz]
                    # 只关注被冲地支五行在fav中的案例
                    if bz_wx not in fav:
                        break
                    
                    # 获取冲支结果
                    clash_results = [c for c in _transit_clash_verdicts(tp0) if z in c['pair']]
                    clash_verdicts = [c['verdict'] for c in clash_results]
                    
                    # 被冲地支藏干
                    hidden = HIDDEN_STEMS.get(bz, [])
                    hidden_wx = [_WUXING[s] for s in hidden]
                    
                    # 被冲地支的结构角色
                    roles = []
                    if pos == '月': roles.append('月令')
                    if pos == '日': roles.append('日支')
                    if bz in MU_KU: roles.append('墓库')
                    # 日主根判断
                    if hidden and hidden_wx[0] == dmw:
                        roles.append('日主重根(本气)')
                    elif dmw in hidden_wx[1:]:
                        roles.append('日主轻根(中气/余气)')
                    # 透干之根判断
                    for h_stem in hidden:
                        stem_roles = get_stem_role(h_stem, pillars, dm)
                        if stem_roles:
                            roles.append(f'{h_stem}透干({"/".join(stem_roles)})')
                    
                    # 用神四轨信息
                    multi_track = ye.get('yongshen_multi_track', {})
                    track_info = {}
                    if isinstance(multi_track, dict):
                        for track_id, track_data in multi_track.items():
                            if isinstance(track_data, dict):
                                activated = track_data.get('activated', 'N/A')
                                candidates = track_data.get('candidates', [])
                                track_info[track_id] = f'激活={activated}, 候选={candidates}'
                    
                    result = {
                        'case_id': f'L{li+1}',
                        'chart': ''.join(a+b for a,b in fp),
                        'daymaster': dm,
                        'daymaster_wx': dmw,
                        'dayun': gz,
                        'chong_pos': pos,
                        'chonged_branch': bz,
                        'chonged_branch_wx': bz_wx,
                        'chonged_hidden': hidden,
                        'chonged_hidden_wx': hidden_wx,
                        'structure_roles': roles,
                        'clash_verdicts': clash_verdicts,
                        'fav': sorted(fav),
                        'avoid': sorted(av),
                        'primary': prim,
                        'engine_judgment': f'gc={gc}, zc={zc}, lc=fav→expect=ji',
                        'original_judgment': f'xiong({blob[:50]})',
                        'multi_track': track_info,
                    }
                    results.append(result)
                    break
    
    # 打印诊断结果
    print(f'共导出 {len(results)} 例\n')
    print('=' * 80)
    for i, r in enumerate(results, 1):
        print(f'\n【案例 {i}】{r["case_id"]} {r["chart"]} 日主{r["daymaster"]}({r["daymaster_wx"]})')
        print(f'  大运: {r["dayun"]}')
        print(f'  冲: {r["dayun"][1]}冲{r["chong_pos"]}支{r["chonged_branch"]}({r["chonged_branch_wx"]})')
        print(f'  被冲地支藏干: {r["chonged_hidden"]} (五行: {r["chonged_hidden_wx"]})')
        print(f'  结构角色: {", ".join(r["structure_roles"])}')
        print(f'  冲支结果: {r["clash_verdicts"]}')
        print(f'  fav集合: {r["fav"]}')
        print(f'  avoid集合: {r["avoid"]}')
        print(f'  primary: {r["primary"]}')
        print(f'  引擎判断: {r["engine_judgment"]}')
        print(f'  原典判断: {r["original_judgment"]}')
        if r['multi_track']:
            print(f'  用神四轨:')
            for tid, tinfo in r['multi_track'].items():
                print(f'    {tid}: {tinfo}')
        
        # 机制分类推测
        print(f'  机制推测: ', end='')
        roles = r['structure_roles']
        if '日主重根(本气)' in roles or '日主轻根(中气/余气)' in roles:
            print('冲拔日主根')
        elif '月令' in roles:
            print('冲月令(格局之根)')
        elif '墓库' in roles:
            print('冲开墓库')
        elif any('透干' in role for role in roles):
            print('冲拔透干之根(用神根?)')
        else:
            print('待分析')
    print('\n' + '=' * 80)
    
    # 按机制分类统计
    print('\n【机制分类统计】')
    mechanisms = {}
    for r in results:
        roles = r['structure_roles']
        if '日主重根(本气)' in roles or '日主轻根(中气/余气)' in roles:
            mech = '冲拔日主根'
        elif '月令' in roles:
            mech = '冲月令'
        elif '墓库' in roles:
            mech = '冲开墓库'
        elif any('透干' in role for role in roles):
            mech = '冲拔透干之根'
        else:
            mech = '其他'
        mechanisms.setdefault(mech, []).append(r['case_id'])
    for mech, cases in mechanisms.items():
        print(f'  {mech}: {len(cases)}例 - {cases}')

if __name__ == '__main__':
    diagnose()
