# -*- coding: utf-8 -*-
"""用神四轨并行层 命中率@K 评估脚本

对比:
- 旧引擎: 单一答案准确率 (primary == 标准答案)
- 新四轨: 命中率@K (标准答案 ∈ 所有激活轨道候选集)
"""
import sys, json, re
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
from engines.common.yongshen_multi_track import build_yongshen_multi_track
from engines.common.daymaster_power_queries import run_queries
from engines.common.bingyao_layer import build_bingyao_layer

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

def extract_yongshen(raw):
    """从原文提取用神五行"""
    patterns = [
        r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用',
        r'用([甲乙丙丁戊己庚辛壬癸水火木金土])',
        r'取([甲乙丙丁戊己庚辛壬癸水火木金土])为用',
        r'([甲乙丙丁戊己庚辛壬癸水火木金土])为用神',
        r'用神在([甲乙丙丁戊己庚辛壬癸水火木金土])',
        r'专用([甲乙丙丁戊己庚辛壬癸水火木金土])',
        r'宜用([甲乙丙丁戊己庚辛壬癸水火木金土])',
    ]
    result = []
    for pat in patterns:
        for m in re.findall(pat, raw):
            if m in STEM_WX:
                result.append(STEM_WX[m])
            elif m in '水火木金土':
                result.append(m)
    return list(dict.fromkeys(result))

def run_both(bazi_str):
    """同时运行旧引擎和新四轨"""
    bazi = bazi_str.replace(' ', '')
    if len(bazi) != 8:
        return None
    pillars = {'year': bazi[0:2], 'month': bazi[2:4], 'day': bazi[4:6], 'hour': bazi[6:8]}
    try:
        f = build(pillars)
        pa = build_power_structure(pillars)
        hst = {pillars[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
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
        queries = run_queries(net)
        by = build_bingyao_layer(f, queries)
        old = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)
        new = build_yongshen_multi_track(pillars, f, wpo, spt, spc, clc, bingyao=by)
        return {'old': old, 'new': new, 'tier': spt.get('spectrum'), 'bing_count': by.get('bing_count', 0)}
    except Exception as e:
        return {'error': str(e)}

def main():
    case_path = r'D:\顺天系统资料\用神案例JSONL\原局层\all.jsonl'
    with open(case_path, 'r', encoding='utf-8') as f:
        cases = [json.loads(line) for line in f if line.strip()]

    total = 0
    old_match = 0
    new_hit = 0
    old_mismatch_new_hit = 0  # 旧引擎不匹配但新四轨命中
    both_mismatch = 0
    by_book = {}
    mismatch_details = []

    for c in cases:
        bazi = c.get('bazi', '') or c.get('chart', '')
        raw = c.get('raw', '') or c.get('judgment', '') or c.get('断语', '') or ''
        book = c.get('book', '未知')
        if not bazi or len(bazi.replace(' ', '')) != 8:
            continue
        std = extract_yongshen(raw)
        if not std:
            continue
        total += 1
        result = run_both(bazi)
        if not result or 'error' in result:
            continue

        old_primary = result['old'].get('yongshen_primary')
        new_candidates = result['new'].get('candidate_elements', [])
        tier = result.get('tier', '')

        # 旧引擎: 单一答案匹配
        old_ok = old_primary in std
        # 新四轨: 命中率@K (标准答案任一在候选集中)
        new_ok = any(s in new_candidates for s in std)

        if old_ok:
            old_match += 1
        if new_ok:
            new_hit += 1
        if not old_ok and new_ok:
            old_mismatch_new_hit += 1
        if not old_ok and not new_ok:
            both_mismatch += 1
            mismatch_details.append({
                'bazi': bazi, 'book': book, 'tier': tier,
                'std': std, 'old_primary': old_primary,
                'new_candidates': new_candidates,
                'conflict': result['new'].get('conflict', {}).get('has_conflict', False),
            })

        by_book.setdefault(book, {'total': 0, 'old': 0, 'new': 0})
        by_book[book]['total'] += 1
        if old_ok:
            by_book[book]['old'] += 1
        if new_ok:
            by_book[book]['new'] += 1

    print("=" * 60)
    print("用神四轨并行层 命中率@K 评估")
    print("=" * 60)
    print(f"可对齐案例数: {total}")
    print()
    print(f"旧引擎单一答案准确率: {old_match}/{total} = {old_match/total*100:.1f}%")
    print(f"新四轨命中率@K:       {new_hit}/{total} = {new_hit/total*100:.1f}%")
    print()
    print(f"旧不匹配但新命中(提升): {old_mismatch_new_hit} 例")
    print(f"两者都不匹配:           {both_mismatch} 例")
    print()
    print("-" * 60)
    print("按书籍对比:")
    print(f"{'书籍':<12} {'总数':>4} {'旧准确率':>8} {'新命中率':>8} {'提升':>6}")
    print("-" * 60)
    for book, d in sorted(by_book.items(), key=lambda x: -x[1]['total']):
        old_pct = d['old']/d['total']*100 if d['total'] else 0
        new_pct = d['new']/d['total']*100 if d['total'] else 0
        delta = new_pct - old_pct
        print(f"{book:<12} {d['total']:>4} {old_pct:>7.1f}% {new_pct:>7.1f}% {delta:>+5.1f}%")
    print()

    if mismatch_details:
        print("=" * 60)
        print(f"两者都不匹配的案例 ({len(mismatch_details)}例):")
        print("=" * 60)
        for d in mismatch_details[:10]:
            print(f"  {d['bazi']} [{d['book']}] tier={d['tier']}")
            print(f"    标准答案: {d['std']}, 旧引擎: {d['old_primary']}, 新候选: {d['new_candidates']}")

    # 保存不匹配详情
    out_path = r'D:\shuntian-ziping-p0\scripts\multi_track_mismatch.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(mismatch_details, f, ensure_ascii=False, indent=2)
    print(f"\n不匹配详情已保存: {out_path}")

if __name__ == '__main__':
    main()
