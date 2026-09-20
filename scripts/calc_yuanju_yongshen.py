# -*- coding: utf-8 -*-
"""原局用神全量评估脚本 - 针对原局层用神专项163条案例"""
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

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
WUXING_STEMS = {'木':['甲','乙'], '火':['丙','丁'], '土':['戊','己'], '金':['庚','辛'], '水':['壬','癸']}

def extract_yongshen_from_raw(raw):
    """从原文中提取用神 - 高优先级模式匹配 + 五行匹配"""
    yongshen_list = []
    
    # 模式1: "以X为用" / "用X" / "取X为用" / "X为用神"
    patterns = [
        r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用',
        r'用([甲乙丙丁戊己庚辛壬癸水火木金土])',
        r'取([甲乙丙丁戊己庚辛壬癸水火木金土])为用',
        r'([甲乙丙丁戊己庚辛壬癸水火木金土])为用神',
        r'用神在([甲乙丙丁戊己庚辛壬癸水火木金土])',
        r'专用([甲乙丙丁戊己庚辛壬癸水火木金土])',
        r'宜用([甲乙丙丁戊己庚辛壬癸水火木金土])',
        r'当用([甲乙丙丁戊己庚辛壬癸水火木金土])',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, raw)
        for m in matches:
            if m in STEM_WX:
                yongshen_list.append(STEM_WX[m])
            elif m in '水火木金土':
                yongshen_list.append(m)
    
    # 去重
    yongshen_list = list(dict.fromkeys(yongshen_list))
    return yongshen_list

def run_engine(bazi_str):
    """运行引擎计算用神"""
    bazi = bazi_str.replace(' ', '')
    if len(bazi) != 8:
        return None
    
    pillars = {'year': bazi[0:2], 'month': bazi[2:4], 'day': bazi[4:6], 'hour': bazi[6:8]}
    
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
        
        return ye
    except Exception as e:
        print(f"  引擎错误: {e}")
        return None

def main():
    input_file = r'D:\顺天系统资料\用神案例JSONL\原局层\用神专项\用神_all.jsonl'
    
    with open(input_file, encoding='utf-8') as f:
        cases = [json.loads(line) for line in f if line.strip()]
    
    print(f"总案例数: {len(cases)}")
    
    total = 0
    match = 0
    mismatch = 0
    no_yongshen_in_raw = 0
    engine_error = 0
    mismatch_cases = []
    
    for i, case in enumerate(cases):
        case_id = case.get('case_id', '')
        book = case.get('book', '')
        bazi = case.get('bazi', '')
        raw = case.get('raw', '')
        
        if not bazi or len(bazi.replace(' ', '')) != 8:
            continue
        
        total += 1
        
        # 从原文提取用神
        raw_yongshen = extract_yongshen_from_raw(raw)
        
        if not raw_yongshen:
            no_yongshen_in_raw += 1
            continue
        
        # 运行引擎
        ye = run_engine(bazi)
        if ye is None:
            engine_error += 1
            continue
        
        engine_primary = ye.get('yongshen_primary', '')
        engine_secondary = ye.get('yongshen_secondary', [])
        engine_all = [engine_primary] + engine_secondary if engine_primary else engine_secondary
        engine_all = [x for x in engine_all if x]
        
        # 比较：引擎primary在原文用神列表中即为匹配
        if engine_primary and engine_primary in raw_yongshen:
            match += 1
        else:
            mismatch += 1
            mismatch_cases.append({
                'case_id': case_id,
                'book': book,
                'bazi': bazi,
                'raw_yongshen': raw_yongshen,
                'engine_primary': engine_primary,
                'engine_secondary': engine_secondary,
                'theory_source': ye.get('theory_source', ''),
                'spectrum_tier': ye.get('spectrum_tier', ''),
                'raw_snippet': raw[:200]
            })
        
        if (i + 1) % 20 == 0:
            print(f"  已处理 {i+1}/{len(cases)}, 当前匹配: {match}/{total - no_yongshen_in_raw - engine_error}")
    
    print(f"\n=== 原局用神评估结果 ===")
    print(f"总案例数: {len(cases)}")
    print(f"有效案例(八字完整): {total}")
    print(f"原文有用神: {total - no_yongshen_in_raw}")
    print(f"原文无用神(跳过): {no_yongshen_in_raw}")
    print(f"引擎错误: {engine_error}")
    print(f"可对齐案例: {total - no_yongshen_in_raw - engine_error}")
    print(f"匹配: {match}")
    print(f"不匹配: {mismatch}")
    if (total - no_yongshen_in_raw - engine_error) > 0:
        print(f"准确率: {match/(total - no_yongshen_in_raw - engine_error)*100:.1f}% ({match}/{total - no_yongshen_in_raw - engine_error})")
    
    # 保存不匹配案例
    output_file = r'D:\shuntian-ziping-p0\scripts\yuanju_yongshen_mismatch.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mismatch_cases, f, ensure_ascii=False, indent=2)
    print(f"\n不匹配案例已保存到: {output_file}")
    
    # 按书籍统计
    print(f"\n=== 按书籍统计 ===")
    book_stats = {}
    for case in cases:
        book = case.get('book', '')
        if book not in book_stats:
            book_stats[book] = {'total': 0, 'match': 0, 'mismatch': 0, 'no_yongshen': 0}
        book_stats[book]['total'] += 1
    
    for mc in mismatch_cases:
        book = mc['book']
        if book in book_stats:
            book_stats[book]['mismatch'] += 1
    
    # 重新计算匹配数
    for book in book_stats:
        book_cases = [c for c in cases if c.get('book') == book]
        book_match = 0
        for case in book_cases:
            bazi = case.get('bazi', '')
            raw = case.get('raw', '')
            if not bazi or len(bazi.replace(' ', '')) != 8:
                continue
            raw_yongshen = extract_yongshen_from_raw(raw)
            if not raw_yongshen:
                book_stats[book]['no_yongshen'] += 1
                continue
            ye = run_engine(bazi)
            if ye is None:
                continue
            engine_primary = ye.get('yongshen_primary', '')
            if engine_primary and engine_primary in raw_yongshen:
                book_match += 1
        book_stats[book]['match'] = book_match
    
    for book, stats in sorted(book_stats.items()):
        alignable = stats['total'] - stats['no_yongshen']
        if alignable > 0:
            print(f"  {book}: {stats['match']}/{alignable} ({stats['match']/alignable*100:.1f}%), 无用神{stats['no_yongshen']}")
        else:
            print(f"  {book}: 无可对齐案例")

if __name__ == '__main__':
    main()
