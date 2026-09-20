# -*- coding: utf-8 -*-
import json
import os
import re
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
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
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine

WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

def extract_yongshen(raw):
    """从原文中提取用神判断 - V5.2优化版：优先匹配命例正文明确用神，支持天干和五行"""
    # V5: 最优先匹配"以X为用"，X可以是天干或五行，避免被后面注解覆盖
    import re as _re
    m = _re.search(r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用(?!者)', raw)
    if m:
        g = m.group(1)
        return WX.get(g, g)
    # V5.2: 匹配五行用神模式
    wx_patterns = [
        r'用神必在([水火木金土])',
        r'用神在([水火木金土])',
        r'以([水火木金土])为用神',
        r'用神是([水火木金土])',
        r'用神为([水火木金土])',
        r'专用([水火木金土])',
        r'专取([水火木金土])',
        r'取([水火木金土])为用神',
        r'当以([水火木金土])为用神',
        r'必以([水火木金土])为用神',
        r'宜用([水火木金土])为用',
    ]
    for pat in wx_patterns:
        m = _re.search(pat, raw)
        if m:
            return m.group(1)
    # 高优先级模式: 明确的用神判断
    high_priority_patterns = [
        r'用神必在([甲乙丙丁戊己庚辛壬癸])',
        r'用神在([甲乙丙丁戊己庚辛壬癸])',
        r'以([甲乙丙丁戊己庚辛壬癸])为用神',
        r'用神是([甲乙丙丁戊己庚辛壬癸])',
        r'用神为([甲乙丙丁戊己庚辛壬癸])',
        r'专用([甲乙丙丁戊己庚辛壬癸])[水火木金土]?',
        r'专取([甲乙丙丁戊己庚辛壬癸])[水火木金土]?',
        r'专尚([甲乙丙丁戊己庚辛壬癸])[水火木金土]?',
        r'专以([甲乙丙丁戊己庚辛壬癸])[水火木金土]?为用',
        r'取([甲乙丙丁戊己庚辛壬癸])为用神',
        r'当以([甲乙丙丁戊己庚辛壬癸])为用神',
        r'必以([甲乙丙丁戊己庚辛壬癸])为用神',
        r'宜用([甲乙丙丁戊己庚辛壬癸])[水火木金土]?为用',
        r'用神必须([甲乙丙丁戊己庚辛壬癸])',
        r'用神专取([甲乙丙丁戊己庚辛壬癸])',
        r'用神专用([甲乙丙丁戊己庚辛壬癸])',
    ]
    for pat in high_priority_patterns:
        m = re.search(pat, raw)
        if m:
            stem = m.group(1)
            return WX.get(stem, stem)

    # 中优先级模式: 以X为用、用X等
    medium_priority_patterns = [
        r'以([甲乙丙丁戊己庚辛壬癸])为用',
        r'当以([甲乙丙丁戊己庚辛壬癸])为用',
        r'必以([甲乙丙丁戊己庚辛壬癸])为用',
        r'宜用([甲乙丙丁戊己庚辛壬癸])',
        r'用([甲乙丙丁戊己庚辛壬癸])[水火木金土]为',
        r'用([甲乙丙丁戊己庚辛壬癸])[水火木金土]，',
        r'用([甲乙丙丁戊己庚辛壬癸])[水火木金土]。',
    ]
    for pat in medium_priority_patterns:
        m = re.search(pat, raw)
        if m:
            stem = m.group(1)
            return WX.get(stem, stem)

    return None

def run_engine(bazi_str):
    """运行用神引擎"""
    parts = bazi_str.split()
    if len(parts) != 4:
        return None
    pillars = {
        'year': (parts[0][0], parts[0][1]),
        'month': (parts[1][0], parts[1][1]),
        'day': (parts[2][0], parts[2][1]),
        'hour': (parts[3][0], parts[3][1]),
    }
    try:
        f = build(pillars)
        pa = build_power_structure(pillars)
        hst = {pillars[k][1]: f['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
        rc = build_root_classes(pillars, hst)
        tc = build_tou_cang(f)
        wx = build_wang_xiang(f, f['day_stem'])
        rr = build_root_relations(rc, f['combination_facts'])
        ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(pillars, f)
        th = build_tian_he(pillars, f)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)
        wpo = build_wuxing_power(pillars, f, th)
        spt = build_spectrum_topology(net, wpo)
        cl = build_climate_structure(pillars, f, th)
        spc = build_special_patterns(pillars, f, wpo, th, cl)
        clc = build_climate_candidates(f)
        ye = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)
        return ye.get('yongshen_primary')
    except Exception as e:
        return None

base = r'D:\顺天系统资料\用神案例JSONL\用神专项'
files = ['DTS滴天髓阐微.jsonl','PZZQ子平真诠.jsonl','QTBJ穷通宝鉴.jsonl','SFTK神峰通考.jsonl','SMTH三命通会.jsonl','YHZP渊海子平.jsonl']

total = 0
has_yongshen = 0
match = 0
mismatch = 0
mismatch_cases = []

for fname in files:
    fpath = os.path.join(base, fname)
    with open(fpath, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                case = json.loads(line)
            except:
                continue
            total += 1
            raw = case.get('raw', '')
            bazi = case.get('bazi', '')
            expected = extract_yongshen(raw)
            if not expected:
                continue
            has_yongshen += 1
            actual = run_engine(bazi)
            if actual is None:
                continue
            if actual == expected:
                match += 1
            else:
                mismatch += 1
                if len(mismatch_cases) < 20:
                    mismatch_cases.append({
                        'case_id': case.get('case_id', ''),
                        'book': case.get('book', ''),
                        'bazi': bazi,
                        'expected': expected,
                        'actual': actual,
                    })

print(f'总案例数: {total}')
print(f'可提取用神案例数: {has_yongshen}')
print(f'引擎可运行案例数: {match + mismatch}')
print(f'匹配: {match}')
print(f'不匹配: {mismatch}')
if match + mismatch > 0:
    print(f'准确率: {match/(match+mismatch)*100:.1f}%')
print()
print('不匹配案例(前20):')
for c in mismatch_cases:
    print(f"  {c['case_id']} {c['book']} {c['bazi']}: 原文={c['expected']}, 引擎={c['actual']}")
