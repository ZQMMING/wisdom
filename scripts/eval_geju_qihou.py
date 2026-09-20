# -*- coding: utf-8 -*-
"""格局+调候上游根基评估脚本"""
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
from engines.common.pzzq_producer_v1 import produce_pattern_candidates

STEM_WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

def run_full_engine(bazi_str):
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
        pzzq = produce_pattern_candidates(f)
        return {'f': f, 'spc': spc, 'clc': clc, 'pzzq': pzzq, 'wpo': wpo}
    except Exception as e:
        print(f"  引擎错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_geju_from_raw(raw):
    """从原文提取格局名称"""
    geju_patterns = [
        r'(正官格|七杀格|偏官格|正财格|偏财格|正印格|偏印格|食神格|伤官格)',
        r'(建禄格|月劫格|羊刃格|阳刃格)',
        r'(从财格|从杀格|从官格|从儿格|从势格|从强格|从旺格)',
        r'(曲直格|炎上格|稼穑格|从革格|润下格|专旺格)',
        r'(化土格|化金格|化水格|化木格|化火格|化气格)',
        r'(两气成象格|井栏叉格|六阴朝阳格|刑合格|合禄格)',
    ]
    found = []
    for pattern in geju_patterns:
        matches = re.findall(pattern, raw)
        found.extend(matches)
    return list(dict.fromkeys(found))

def main():
    input_file = r'D:\顺天系统资料\用神案例JSONL\原局层\用神专项\用神_all.jsonl'
    with open(input_file, encoding='utf-8') as f:
        cases = [json.loads(line) for line in f if line.strip()]
    
    print(f"总案例数: {len(cases)}")
    print()
    
    geju_total = 0
    geju_match = 0
    geju_mismatch_cases = []
    
    qihou_total = 0
    qihou_correct = 0
    qihou_mismatch_cases = []
    
    special_pattern_stats = {}
    
    for i, case in enumerate(cases):
        chart_str = case.get('bazi', '') or case.get('chart', '')
        if not chart_str or len(chart_str) < 8:
            continue
        
        text = case.get('raw', '') or case.get('text', '') or case.get('judgment', '')
        raw_geju = extract_geju_from_raw(text)
        
        result = run_full_engine(chart_str)
        if not result:
            continue
        
        # 格局评估
        spc = result['spc']
        pzzq = result['pzzq']
        
        # 提取引擎格局
        engine_geju = []
        if isinstance(spc, dict):
            patterns = spc.get('patterns', [])
            if isinstance(patterns, list):
                for p in patterns:
                    if isinstance(p, dict):
                        name = p.get('pattern_name', '') or p.get('name', '') or p.get('type', '')
                        if name:
                            engine_geju.append(name)
            # 特殊格局
            for key in ['cong_type', 'zhuanwang', 'hua_qi', 'liangqi']:
                val = spc.get(key)
                if val and isinstance(val, str):
                    engine_geju.append(val)
        
        # pzzq格局
        if isinstance(pzzq, dict):
            candidates = pzzq.get('pattern_candidates', []) or pzzq.get('candidates', [])
            if isinstance(candidates, list):
                for c in candidates:
                    if isinstance(c, dict):
                        name = c.get('pattern_type', '') or c.get('pattern_name', '') or c.get('name', '') or c.get('type', '')
                        if name:
                            # 统一格式：加"格"字
                            if not name.endswith('格'):
                                name = name + '格'
                            engine_geju.append(name)
            primary = pzzq.get('primary_pattern', '') or pzzq.get('pattern', '')
            if primary:
                if not primary.endswith('格'):
                    primary = primary + '格'
                engine_geju.append(primary)
        
        engine_geju = list(dict.fromkeys([g for g in engine_geju if g]))
        
        # 统计特殊格局
        for g in engine_geju:
            special_pattern_stats[g] = special_pattern_stats.get(g, 0) + 1
        
        if raw_geju:
            geju_total += 1
            ALIAS = {'化土格': '化土气格', '化木格': '化木气格', '化金格': '化金气格', '化水格': '化水气格', '化火格': '化火气格', '偏官格': '七杀格', '羊刃格': '阳刃格'}
            def norm(g): return ALIAS.get(g, g)
            raw_set = set(norm(g) for g in raw_geju)
            engine_set = set(norm(g) for g in engine_geju)
            if raw_set & engine_set:
                geju_match += 1
            else:
                geju_mismatch_cases.append({'case_id': case.get('case_id', ''), 'chart': chart_str, 'raw_geju': raw_geju, 'engine_geju': engine_geju, 'text': text[:100]})
        
        # 调候评估
        clc = result['clc']
        if isinstance(clc, dict) and clc.get('climate_candidates'):
            qihou_total += 1
            # 检查调候候选是否包含原文用神
            candidates = clc['climate_candidates']
            candidate_elements = set()
            for c in candidates:
                if isinstance(c, dict):
                    stem = c.get('stem', '')
                    if stem and stem in STEM_WX:
                        candidate_elements.add(STEM_WX[stem])
            
            # 从原文提取用神五行
            yongshen_patterns = [
                r'以([甲乙丙丁戊己庚辛壬癸])为用',
                r'专用([甲乙丙丁戊己庚辛壬癸])',
                r'用神在([甲乙丙丁戊己庚辛壬癸])',
            ]
            raw_yongshen = set()
            for p in yongshen_patterns:
                for m in re.findall(p, text):
                    if m in STEM_WX:
                        raw_yongshen.add(STEM_WX[m])
            
            if raw_yongshen:
                if raw_yongshen & candidate_elements:
                    qihou_correct += 1
                else:
                    qihou_mismatch_cases.append({
                        'case_id': case.get('case_id', ''),
                        'chart': chart_str,
                        'raw_yongshen': list(raw_yongshen),
                        'candidates': list(candidate_elements),
                        'text': text[:100]
                    })
        
        if (i + 1) % 20 == 0:
            print(f"  已处理 {i+1}/{len(cases)}")
    
    print()
    print("=" * 60)
    print("格局识别评估")
    print(f"  原文有格局: {geju_total}")
    print(f"  格局匹配: {geju_match}")
    if geju_total > 0:
        print(f"  准确率: {geju_match/geju_total*100:.1f}%")
    print(f"  不匹配数: {len(geju_mismatch_cases)}")
    print()
    print("特殊格局统计:")
    for k, v in sorted(special_pattern_stats.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print()
    print("=" * 60)
    print("调候候选评估")
    print(f"  有调候候选: {qihou_total}")
    print(f"  原文有用神: {qihou_correct + len(qihou_mismatch_cases)}")
    print(f"  调候包含原文用神: {qihou_correct}")
    if (qihou_correct + len(qihou_mismatch_cases)) > 0:
        print(f"  准确率: {qihou_correct/(qihou_correct+len(qihou_mismatch_cases))*100:.1f}%")
    print(f"  不匹配数: {len(qihou_mismatch_cases)}")
    print()
    
    # 保存不匹配案例
    with open(r'D:\shuntian-ziping-p0\scripts\geju_mismatch.json', 'w', encoding='utf-8') as f:
        json.dump(geju_mismatch_cases, f, ensure_ascii=False, indent=2)
    with open(r'D:\shuntian-ziping-p0\scripts\qihou_mismatch.json', 'w', encoding='utf-8') as f:
        json.dump(qihou_mismatch_cases, f, ensure_ascii=False, indent=2)
    
    print("不匹配案例已保存到 scripts/geju_mismatch.json 和 scripts/qihou_mismatch.json")
    
    # 打印前10个格局不匹配案例
    if geju_mismatch_cases:
        print()
        print("前10个格局不匹配案例:")
        for c in geju_mismatch_cases[:10]:
            print(f"  {c['chart']}: 原文={c['raw_geju']}, 引擎={c['engine_geju']}")
    
    # 打印前10个调候不匹配案例
    if qihou_mismatch_cases:
        print()
        print("前10个调候不匹配案例:")
        for c in qihou_mismatch_cases[:10]:
            print(f"  {c['chart']}: 原文用神={c['raw_yongshen']}, 调候候选={c['candidates']}")

if __name__ == '__main__':
    main()
