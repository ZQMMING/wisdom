# -*- coding: utf-8 -*-
"""导出513命例完整辩层+断言输出到csv(29列):
七档旺衰+根+透藏+特殊格局+气候+全局中和+母灭+query + 用神V3.3(主/喜/忌/路径) + 大运应期(逐柱复合七档/新冲verdict)。"""
import re, sys, csv
sys.path.insert(0, '.')
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
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure
from engines.common.zhonghe_structure import build_zhonghe_structure
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine
from engines.common.transit_power import build_transit_power, transit_clash_verdicts

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')
pl = []
for i, ln in enumerate(lines):
    s = ln.strip(); fp = None
    if s.startswith('八字'):
        b = s.split('：', 1)[-1].split(':', 1)[-1].strip(); pp = GZ.findall(b)
        if len(pp) == 4: fp = pp
    else:
        pp = GZ.findall(s)
        if len(pp) == 4 and len(s) < 60:
            c = GZ.sub('', s).replace(' ', '').replace('　', '')
            if c == '': fp = pp
    if fp: pl.append((i, fp))

def parse_dayun(i):
    for off in (1, 2):
        if i + off >= len(lines): continue
        nl = lines[i+off]; gz = GZ.findall(nl)
        c = GZ.sub('', nl).replace(' ', '').replace('　', '').replace('大运', '') \
             .replace('：', '').replace(':', '').strip()
        if len(gz) >= 5 and c == '':
            return [a+b for a, b in gz]
    return []

rows = []
for li, fp in pl:
    p = {'year': list(fp[0]), 'month': list(fp[1]), 'day': list(fp[2]), 'hour': list(fp[3])}
    s = ''.join(fp[0] + fp[1] + fp[2] + fp[3])
    try:
        f = build(p); pa = build_power_structure(p)
        hst = {p[k][1]: f['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
        rc = build_root_classes(p, hst); tc = build_tou_cang(f); wx = build_wang_xiang(f, f['day_stem'])
        rr = build_root_relations(rc, f['combination_facts']); ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(p, f); th = build_tian_he(p, f)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)
        wpo = build_wuxing_power(p, f, th)
        spt = build_spectrum_topology(net, wpo)
        spectrum = spt['spectrum']; ratio = spt['daymaster_ratio']
        rw = net['dimensions']['ROOT']['root_weight_class']
        seas = net['dimensions']['SEASONAL'].get('state', '')
        cl = build_climate_structure(p, f, th)
        spc = build_special_patterns(p, f, wpo, th, cl)
        zh = build_zhonghe_structure(p, f, wpo, spc)
        dm = f['day_stem']
        month_god = f.get('month_qi_ten_god', '')
        root_detail = '|'.join(f"{k}:{v}" for k, v in net['dimensions']['ROOT']['root_class_detail'].items() if v != 'NONE')
        sup = net['dimensions']['SUPPORT']
        sup_info = '|'.join(f"{k}:{v['stem_count']}透" for k, v in sup.items() if v['stem_count'] > 0)
        drn = net['dimensions']['DRAIN']
        drn_info = '|'.join(f"{k}:{v['stem_count']}透" for k, v in drn.items() if v['stem_count'] > 0)
        ctrl = net['dimensions']['CONTROL']
        ctrl_info = '|'.join(f"{k}:{v['stem_count']}透" for k, v in ctrl.items() if v['stem_count'] > 0)
        two_side = net.get('two_side_structure', {})
        two_side_str = two_side.get('note', '')[:30] if isinstance(two_side, dict) else str(two_side)[:30]
        th_info = net['dimensions']['TIAN_HE']
        he_pairs = th_info.get('he_pairs', []) if isinstance(th_info, dict) else []
        he_str = '|'.join(f"{hp['stems'][0]}{hp['stems'][1]}化{hp['huashen_wuxing']}" for hp in he_pairs if isinstance(hp, dict))
        qs = [q['query_id'].split('QUERY-')[-1] for q in run_queries(net) if q['state'] == 'SUPPORTED']
        cong = (spc.get('cong_type') or '') + ('/' + spc['cong_state'] if spc.get('cong_state') else '')
        # —— 用神 V3.3 ——
        clc = build_climate_candidates(f)
        ye = build_yongshen_engine(p, f, wpo, spt, spc, clc)
        ys_primary = ye.get('yongshen_primary') or ''
        ys_secondary = '|'.join(ye.get('yongshen_secondary') or [])
        ys_avoid = '|'.join(ye.get('yongshen_avoid') or [])
        ys_path = '|'.join(ye.get('yongshen_paths') or [])
        # —— 大运应期: 逐柱复合七档 + 岁运支引入的新冲 ——
        dy = parse_dayun(li)
        dy_spec, dy_clash = [], []
        for gzstr in dy:
            g, z = gzstr[0], gzstr[1]
            tp = build_transit_power(p, extra_pillars=[[g, z]])
            tspec = tp['spectrum']
            tspec = tspec['spectrum'] if isinstance(tspec, dict) else tspec
            dy_spec.append(f'{gzstr}:{tspec}')
            for v in transit_clash_verdicts(tp):
                if z in v.get('pair', []):
                    dy_clash.append(f'{gzstr}|{v["verdict"]}')
        rows.append({'line': li + 1, 'chart': s, 'daymaster': dm, 'month_god': month_god,
                     'spectrum': spectrum, 'ratio': ratio,
                     'root': rw, 'root_detail': root_detail, 'season': seas,
                     'support': sup_info, 'drain': drn_info, 'control': ctrl_info,
                     'two_side': two_side_str, 'tian_he': he_str,
                     'cong': cong, 'zhuanwang': spc.get('zhuanwang') or '',
                     'hua_qi': spc.get('hua_qi') or '', 'mu_mie': spc.get('mu_mie') or '',
                     'mu_mie_state': spc.get('mu_mie_state') or '',
                     'climate': '|'.join(cl.get('structure_flags', [])),
                     'zhonghe': zh.get('zhonghe_state') or '',
                     'queries': '|'.join(qs),
                     'ys_primary': ys_primary, 'ys_secondary': ys_secondary,
                     'ys_avoid': ys_avoid, 'ys_path': ys_path,
                     'dayun': '|'.join(dy), 'dayun_spectrum': '|'.join(dy_spec),
                     'dayun_clash': '|'.join(dy_clash)})
    except Exception as e:
        rows.append({'line': li + 1, 'chart': s, 'spectrum': 'ERR', 'root': 'ERR', 'season': '', 'queries': repr(e)[:60]})

FIELDS = ['line', 'chart', 'daymaster', 'month_god',
          'spectrum', 'ratio', 'root', 'root_detail', 'season', 'support', 'drain', 'control',
          'two_side', 'tian_he', 'cong', 'zhuanwang', 'hua_qi', 'mu_mie', 'mu_mie_state', 'climate', 'zhonghe', 'queries',
          'ys_primary', 'ys_secondary', 'ys_avoid', 'ys_path',
          'dayun', 'dayun_spectrum', 'dayun_clash']
with open('scripts/dts_513_output.csv', 'w', encoding='utf-8-sig', newline='') as fo:
    w = csv.DictWriter(fo, fieldnames=FIELDS, extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
print(f'导出: {len(rows)} 行 {len(FIELDS)}列 -> scripts/dts_513_output.csv')
from collections import Counter
print('spectrum分布:', dict(Counter(r.get('spectrum', '') for r in rows)))
print('用神primary分布:', dict(Counter(r.get('ys_primary', '') for r in rows)))
print('有大运:', sum(1 for r in rows if r.get('dayun')), '大运新冲标注:', sum(1 for r in rows if r.get('dayun_clash')))
print('ERR:', [r['chart'] for r in rows if r.get('spectrum') == 'ERR'])
