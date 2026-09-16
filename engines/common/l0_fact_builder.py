# -*- coding: utf-8 -*-
"""PATCH-137 L0 Fact Builder v1
只出可验证事实: 藏干/透干/十神/根/合冲. 不输出格局/旺衰/用神.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HIDDEN = json.load(open(ROOT/'registries/zhi_hidden_stems_v1.json', encoding='utf-8'))['hidden_stems']

WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
YANG = set('甲丙戊庚壬')
LIUHE = {'子':'丑','丑':'子','寅':'亥','亥':'寅','卯':'戌','戌':'卯','辰':'酉','酉':'辰','巳':'申','申':'巳','午':'未','未':'午'}
LIUCHONG = {'子':'午','午':'子','丑':'未','未':'丑','寅':'申','申':'寅','卯':'酉','酉':'卯','辰':'戌','戌':'辰','巳':'亥','亥':'巳'}


def ten_god(day_stem, other_stem):
    """以日干为主的十神事实. 不判旺衰."""
    if day_stem == other_stem:
        return '比肩'
    dw, ow = WUXING[day_stem], WUXING[other_stem]
    same_yin_yang = (day_stem in YANG) == (other_stem in YANG)
    sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    ke = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
    if sheng[dw] == ow:   # 我生
        return '食神' if same_yin_yang else '伤官'
    if ke[dw] == ow:      # 我克
        return '偏财' if same_yin_yang else '正财'
    if ke[ow] == dw:      # 克我
        return '七杀' if same_yin_yang else '正官'
    if sheng[ow] == dw:   # 生我
        return '偏印' if same_yin_yang else '正印'
    return '?'


def build(pillars):
    """pillars: {year:[g,z],month:[g,z],day:[g,z],hour:[g,z]}
    只出事实. 不判格局."""
    dg = pillars['day'][0]
    out = {'day_stem': dg,
           'month_branch': pillars['month'][1],
           'hidden_stems': {k: HIDDEN[v[1]] for k, v in pillars.items()},
           'stem_relations': {},
           'root_facts': {},
           'combination_facts': {'liuhe': [], 'liuchong': []}}
    # 十神事实: 每个天干 vs 日干
    for k, (g, z) in pillars.items():
        if k == 'day': continue
        out['stem_relations'][k] = {'stem': g, 'ten_god': ten_god(dg, g)}
    # 根事实: 日干在各支藏干中
    for k, (g, z) in pillars.items():
        out['root_facts'][k] = dg in HIDDEN[z]
    # 透干事实: 月令藏干哪些透到天干
    mz = pillars['month'][1]
    all_stems = [v[0] for v in pillars.values()]
    out['month_hidden_stems'] = HIDDEN[mz]
    out['month_transparent'] = [s for s in HIDDEN[mz] if s in all_stems]
    # 合冲事实
    zhis = [v[1] for v in pillars.values()]
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            a, b = zhis[i], zhis[j]
            if LIUHE.get(a) == b: out['combination_facts']['liuhe'].append([a, b])
            if LIUCHONG.get(a) == b: out['combination_facts']['liuchong'].append([a, b])
    # PATCH-141H-IMPLEMENT-A 月令生扶日主事实 (纯五行关系, 非得令/身强)
    sheng = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    mqi = HIDDEN[mz][0]            # 本气=注册表首藏干
    mqe = WUXING[mqi]; dme = WUXING[dg]
    out['month_qi_stem'] = mqi
    out['month_qi_element'] = mqe
    out['daymaster_element'] = dme
    out['month_supports_daymaster'] = (mqe == dme) or (sheng[mqe] == dme)
    return out


if __name__ == '__main__':
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    gc001 = {'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['壬','午']}
    print(json.dumps(build(gc001), ensure_ascii=False, indent=2))
