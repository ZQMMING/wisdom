# -*- coding: utf-8 -*-
"""应期复合七档方向一致性审计(内部逻辑自检, 不涉吉凶):
对正格(非从/专旺/化气/母灭CONFIRMED)命例逐柱大运:
  纯帮身运(干支皆印比) -> 复合七档序位不应低于原局
  纯耗身运(干支皆财官食伤) -> 复合七档序位不应高于原局
带冲根/合化反转单独标注; 一帮一耗为中性跳过。"""
import re, sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build, WUXING, HIDDEN
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, BRANCH_WX, SHENG, KE
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure
from engines.common.transit_power import build_transit_power, transit_clash_verdicts
from engines.common.l0_fact_builder import ten_god

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')
cases = []
for i, ln in enumerate(lines):
    s = ln.strip(); fp = None
    if s.startswith('八字'):
        b = s.split('：', 1)[-1].split(':', 1)[-1].strip()
        if len(GZ.findall(b)) == 4: fp = GZ.findall(b)
    elif len(GZ.findall(s)) == 4 and len(s) < 60:
        c = GZ.sub('', s).replace(' ', '').replace('\u3000', '')
        if c == '': fp = GZ.findall(s)
    if not fp: continue
    dy = []
    for off in (1, 2):
        if i + off >= len(lines): continue
        nl = lines[i+off]
        gz = GZ.findall(nl)
        c = GZ.sub('', nl).replace(' ', '').replace('\u3000', '').replace('大运', '') \
            .replace('：', '').replace(':', '').strip()
        if len(gz) >= 5 and c == '':
            dy = [a+b for a, b in gz]; break
    cases.append((i, fp, dy))

ORDER = ['衰极','太衰','衰','中和','旺','太旺','旺极']
print('cases=',len(cases),'有大运=',sum(1 for _,_,dy in cases if len(dy)>=5))
def oi(x):
    return ORDER.index(x) if x in ORDER else 3

def gan_role(dm, g):
    t = ten_god(dm, g)
    if '印' in t: return 'help'
    if '比' in t or '劫' in t: return 'help'
    return 'drain'  # 财/官杀/食伤

def zhi_role(dm_wx, z):
    w = BRANCH_WX[z]
    if w == dm_wx: return 'help'
    if SHENG.get(w) == dm_wx: return 'help'   # 支生我=印
    return 'drain'

stats = {'steps':0,'judgable':0,'agree':0,'suspect':0,'neutral':0,'special':0,'withclash':0}
suspects = []
for li, fp, dy in cases:
    if len(dy) < 4: continue
    p = {'year': list(fp[0]), 'month': list(fp[1]), 'day': list(fp[2]), 'hour': list(fp[3])}
    f = l0build(p); pa = build_power_structure(p)
    hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc = build_root_classes(p, hst); tc = build_tou_cang(f); wxo = build_wang_xiang(f, f['day_stem'])
    rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
    bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
    net = build_power_network(pa, rc, tc, wxo, rr, ts, branch_tier=bt, tian_he=th, facts=f)
    net.setdefault('facts', {})['daymaster_element'] = WUXING[f['day_stem']]
    wpo = build_wuxing_power(p, f, th)
    cl = build_climate_structure(p, f, th)
    spc = build_special_patterns(p, f, wpo, th, cl)
    special = bool(spc.get('cong_type')) or bool(spc.get('zhuanwang')) or bool(spc.get('hua_qi')) \
        or spc.get('mu_mie_state') == 'CONFIRMED'
    if special:
        stats['special'] += 1; continue
    s0 = build_spectrum_topology(net, wpo)['spectrum']
    _tp0 = build_transit_power(p, []); wpw0 = _tp0['wuxing_power']['wuxing_power']
    dm = f['day_stem']; dm_wx = WUXING[dm]
    for gz in dy:
        stats['steps'] += 1
        gr, zr = gan_role(dm, gz[0]), zhi_role(dm_wx, gz[1])
        if gr != zr:
            stats['neutral'] += 1; continue
        want = gr  # help / drain
        tp = build_transit_power(p, [gz])
        s1 = tp['spectrum']['spectrum']
        clash = transit_clash_verdicts(tp)
        stats['judgable'] += 1
        d = oi(s1) - oi(s0)
        ok = (d >= 0) if want == 'help' else (d <= 0)
        if clash: stats['withclash'] += 1
        if ok:
            stats['agree'] += 1
        else:
            stats['suspect'] += 1
            # --- 用复合 wp 判引擎是否有结构理由(合化/墓库余气中气根/合化印/冲拔发/顺泄) ---
            wpw = tp['wuxing_power']['wuxing_power']
            dm_pw = wpw[dm_wx]
            z = gz[1]
            t0lab = str((dm_pw.get('root_detail') or {}).get(z, ''))
            yin_wx = [w for w in ('木','火','土','金','水') if SHENG.get(w) == dm_wx]
            ss_wx = SHENG.get(dm_wx)
            cai_wx = KE.get(dm_wx)
            gs_wx = [w for w in ('木','火','土','金','水') if KE.get(w) == dm_wx]
            def _lab(w):
                return str((wpw.get(w) or {}).get('root_detail', {}).get(z, ''))
            yin_he = any(('BEN_HE' in _lab(w) or 'BEN_JU' in _lab(w)) for w in yin_wx)       # 岁运支合化成印
            yin_support = yin_he or any(_lab(w) for w in yin_wx)                            # 岁运支藏印(本/中/余气)生身
            drain_he = any(('BEN_JU' in _lab(w) or 'BEN_HE' in _lab(w))
                           for w in [ss_wx, cai_wx] + gs_wx)                                  # 岁运支被合化成耗神
            # 岁运支与原局半合/三合助食伤财官(耗神)局反损(如子辰半合水助泄, 辰为水库)
            def _jb(w):
                e = wpw.get(w) or {}; e0 = wpw0.get(w) or {}
                return (int(e.get('ju_n',0))+int(e.get('banhe_n',0))) > (int(e0.get('ju_n',0))+int(e0.get('banhe_n',0)))
            banhe_drain = any(_jb(w) for w in [ss_wx, cai_wx] + gs_wx)
            tg = ten_god(dm, gz[0])
            shunxie = ('食' in tg or '伤' in tg)                                              # 食伤顺泄不否令(封板设计)
            reason = ''
            clash = transit_clash_verdicts(tp)
            for cv in clash:
                v = cv['verdict']
                if want == 'help' and (z + '衰者拔' in v):
                    reason = '帮身支被冲拔'; break
            if not reason and want == 'drain':
                if t0lab:
                    reason = '岁运支实给日主根(本/中/余气/墓库/合化)'
                elif yin_support:
                    reason = '岁运支藏印/合化成印生身(中余气微生)'
                elif _jb(ss_wx) or (shunxie and (wpw0.get(dm_wx) or {}).get('ling_state')=='旺'):
                    reason = '当令重根逢食伤顺泄/成局不否(封板非对称设计)'
                elif shunxie and s0 in ('太旺','旺极'):
                    reason = '当令重根食伤顺泄不否(封板非对称设计)'
                elif s0 in ('太旺','旺极') and d == 1:
                    reason = '极旺盘顺局1档边界(非反转)'
                else:
                    for cv in clash:
                        v = cv['verdict']
                        head = v.split('衰:')[0] if '衰:' in v else v
                        if '旺神发' in v and ('(' + dm_wx) in head:
                            reason = '衰神冲旺 日主方旺神发'; break
            if not reason and want == 'help':
                if drain_he and not t0lab:
                    reason = '帮身支被三合三会/六合化走成耗神'
                elif banhe_drain:
                    reason = '岁运支半合/三合助耗神局反损(如水库助泄)'
                elif s0 in ('太旺','旺极') and d == -1:
                    reason = '极旺盘引入杂气掉出纯粹最高档(1档边界)'
            if reason:
                stats.setdefault('explained', 0); stats['explained'] += 1
            else:
                stats.setdefault('real', 0); stats['real'] += 1
            suspects.append((li+1, ''.join(a+b for a,b in fp), gz, want, s0, s1,
                             tg, t0lab, reason, [c['verdict'] for c in clash]))

print('正格命例(非特殊):', 513 - stats['special'] if False else '')
print(stats)
if stats['judgable']:
    print('可判步 %d, 一致 %d (%.1f%%), 疑似反向 %d (%.1f%%), 其中带冲 %d' % (
        stats['judgable'], stats['agree'], 100*stats['agree']/stats['judgable'],
        stats['suspect'], 100*stats['suspect']/stats['judgable'], stats['withclash']))
    print('疑似中: 引擎结构可解释 %d, 真疑点 %d' % (stats.get('explained',0), stats.get('real',0)))
print('\n=== 真疑点(无合化/墓库根/冲拔发理由) ===')
for x in suspects:
    if not x[8]:
        print(' line%d %s 运%s[%s] %s->%s 干%s t0根[%s] 冲%s' % (x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[9]))
print('\n=== 引擎可解释疑似(抽样10) ===')
n=0
for x in suspects:
    if x[8] and n<10:
        print(' line%d %s 运%s %s->%s [%s] t0[%s]' % (x[0],x[1],x[2],x[4],x[5],x[8],x[7])); n+=1
