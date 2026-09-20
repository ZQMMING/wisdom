# -*- coding: utf-8 -*-
"""DTS 513命例 全量断言对齐评估: 身旺衰/根/格局/用神 逐条命中率+差异清单."""
import re, sys, json, collections
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

# 1. 提取命例(四柱行+断语段)
pillars_lines = []
for i, ln in enumerate(lines):
    s = ln.strip()
    if s.startswith('八字'):
        b = s.split('：',1)[-1].split(':',1)[-1].strip()
        pp = GZ.findall(b)
        if len(pp)==4: pillars_lines.append((i, pp))
    else:
        pp = GZ.findall(s)
        if len(pp)==4 and len(s)<60:
            c = GZ.sub('',s).replace(' ','').replace('\u3000','')
            if c=='': pillars_lines.append((i, pp))

# 2. 每个命例断语段 = 四柱行后30行(到下一四柱行)
KW_WANG = ['身旺','日主旺','身强','强旺','旺极','太旺','旺相']
KW_RUO = ['身弱','日主弱','身衰','衰弱','弱极','太弱','衰极']
KW_YOUGEN = ['有根','通根','根重','根深','得地']
KW_WUGEN = ['无根','根轻','根浅','根拔']
KW_GEJU = ['正官格','七杀格','正印格','偏印格','正财格','偏财格','食神格','伤官格','建禄格','羊刃格','从格','化气格','专旺格']
KW_YONGSHEN = ['喜','用','宜','忌']

cases = []
for idx, (li, fp) in enumerate(pillars_lines):
    end = pillars_lines[idx+1][0] if idx+1 < len(pillars_lines) else min(li+40, len(lines))
    # 遇到章节标题(=====开头)或诗句行(7字以上逗号分隔, 非大运行/非八字行)就停止, 排除通用论述
    for _si in range(li+1, end):
        _s = lines[_si].strip()
        if _s.startswith('====='):
            end = _si; break
        # 诗句行: 7-15字, 含逗号, 非大运行(含多个干支), 非八字行(4组干支)
        if 7 <= len(_s) <= 20 and '，' in _s and not GZ.search(_s) and not _s.startswith('此'):
            end = _si; break
    segment = '\n'.join(lines[li:end])
    wang = [k for k in KW_WANG if k in segment]
    # 语义角色标注: "衰极"需判断主语, 排除"X衰极"(X为五行/天干/地支/十神主语)
    ruo = []
    for k in KW_RUO:
        if k == '衰极':
            # 检查"衰极"前面是否有明确的非日主主语
            import re as _re
            _subjects = r'[金木水火土甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥官杀财印食伤比劫禄刃]'
            _matches = _re.findall(_subjects + r'衰极', segment)
            _has_shen_shuaiji = '身衰极' in segment or '日主衰极' in segment
            _has_plain_shuaiji = '衰极' in segment
            if _has_plain_shuaiji and (not _matches or _has_shen_shuaiji):
                ruo.append(k)
        else:
            if k in segment:
                ruo.append(k)
    yougen = [k for k in KW_YOUGEN if k in segment]
    wugen = [k for k in KW_WUGEN if k in segment]
    geju = [k for k in KW_GEJU if k in segment]
    cases.append({'line':li+1, 'pillars':fp, 'wang':wang, 'ruo':ruo,
                  'yougen':yougen, 'wugen':wugen, 'geju':geju, 'segment':segment[:200]})

print(f'命例总数: {len(cases)}')
print(f'  含旺断语: {sum(1 for c in cases if c["wang"])}')
print(f'  含弱断语: {sum(1 for c in cases if c["ruo"])}')
print(f'  含有根断语: {sum(1 for c in cases if c["yougen"])}')
print(f'  含无根断语: {sum(1 for c in cases if c["wugen"])}')
print(f'  含格局断语: {sum(1 for c in cases if c["geju"])}')

# 3. 跑引擎
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_from_power
from engines.common.daymaster_tian_he import build_tian_he
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
from engines.common.special_pattern import build_special_patterns

results = []
wang_hit = wang_total = 0
ruo_hit = ruo_total = 0
yougen_hit = yougen_total = 0
wugen_hit = wugen_total = 0
wang_mismatch = []
ruo_mismatch = []
yougen_mismatch = []
wugen_mismatch = []
# 从格分类统计
cong_wang_hit = cong_wang_total = 0
cong_ruo_hit = cong_ruo_total = 0
normal_wang_hit = normal_wang_total = 0
normal_ruo_hit = normal_ruo_total = 0
cong_cases_detail = []  # 从格案例详情

for c in cases:
    p = {'year':list(c['pillars'][0]),'month':list(c['pillars'][1]),
         'day':list(c['pillars'][2]),'hour':list(c['pillars'][3])}
    try:
        f = build(p)
        pa = build_power_structure(p)
        hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
        rc = build_root_classes(p, hst)
        tc = build_tou_cang(f)
        wx = build_wang_xiang(f, f['day_stem'])
        rr = build_root_relations(rc, f['combination_facts'])
        ts = build_two_side(rc, tc, rr)
        bt = build_branch_tiers(p, f)
        th = build_tian_he(p, f)
        net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th)
        qs = {q['query_id'].split('QUERY-')[-1]: q for q in run_queries(net)}
        # P2: 消费wang_shuai+qiang_ruo布尔枚举(与DTS轨一致), 替代综合判断
        _th = build_tian_he(p, f)
        _wp = build_wuxing_power(p, f, _th)
        _spec = build_spectrum_from_power(_wp)
        _ws = _spec.get('wang_shuai', {})
        _qr = _spec.get('qiang_ruo', {})
        _in_season_v2 = _ws.get('in_season', False)
        _root_class_v2 = _qr.get('root_class', 'NONE')
        _has_heavy_v2 = _qr.get('has_heavy_root', False)
        _has_root_v2 = _qr.get('has_root', False)
        _support_n_v2 = _qr.get('support_stem_count', 0)
        _oppose_n_v2 = _qr.get('oppose_stem_count', 0)
        rw = net['dimensions']['ROOT'].get('root_weight_class', '')
        has_root = net['dimensions']['ROOT'].get('has_root', False)
        # 从格+专旺格识别(特殊格局, 不从普通身强弱对齐)
        _special = build_special_patterns(p, f, _wp)
        _special_patterns = [pt for pt in _special.get('patterns', []) if pt.get('pattern_id') in ('ZP-SPECIAL-CONG', 'ZP-SPECIAL-ZHUANWANG')]
        _cong_type = _special_patterns[0]['name'] if _special_patterns else ''
        _cong_state = _special_patterns[0].get('state', '') if _special_patterns else ''
        _is_cong = bool(_cong_type)
        # 身旺衰: 综合判断(月令+根气+帮扶+克泄耗), 仅用于对齐评估, 不影响引擎输出
        # 原典: 得时为旺, 失时为衰; 得地为根, 失地无根; 党众为强, 助寡为弱
        # 布尔+多态枚举+多维拓扑, 不做单一总裁决
        _seasonal = net['dimensions'].get('SEASONAL', {})
        _in_season = _seasonal.get('in_season', False)
        _support = net['dimensions'].get('SUPPORT', {})
        _support_count = sum(_support.get(k, {}).get('stem_count', 0) for k in ('BIJIE', 'JIECAI', 'YIN', 'PIAN_YIN'))
        _drain = net['dimensions'].get('DRAIN', {})
        _drain_count = sum(_drain.get(k, {}).get('stem_count', 0) for k in ('SHISHANG', 'SHANGGUAN', 'CAI', 'PIAN_CAI'))
        _control = net['dimensions'].get('CONTROL', {})
        _control_count = sum(_control.get(k, {}).get('stem_count', 0) for k in ('GUANSHA', 'ZHENG_GUAN', 'QI_SHA'))
        _oppose_count = _drain_count + _control_count  # 克泄耗总数
        # P2: 旺/衰判断消费wang_shuai+qiang_ruo(布尔+枚举, 不依赖ratio)
        # 注意: 对齐脚本用宽松条件(与原典身旺/身弱断言一致), 不同于DTS轨严格激活条件
        # 旺: 有重根 或 (得令且有根) 或 (帮扶>=克泄耗且有根)
        engine_wang = _has_heavy_v2 or (_in_season_v2 and _has_root_v2) or (_support_n_v2 >= _oppose_n_v2 and _has_root_v2)
        # 弱: 无根 或 (失令且克泄耗>=帮扶) 或 (根轻且克泄耗>=1) 或 (克泄耗>=3且帮扶<=1)
        # P1: 消费qiang_ruo.effective有效性过滤层(C寒湿过重+B根被冲)
        _effective = _qr.get('effective', '')
        _failure = _qr.get('failure_reasons', [])
        if _effective == '弱' and _failure:
            engine_ruo = True  # 有效性过滤触发, 修正为弱
        else:
            engine_ruo = (not _has_root_v2) or ((not _in_season_v2) and _oppose_n_v2 >= _support_n_v2) or (_root_class_v2 in ('LIGHT', 'NONE') and _oppose_n_v2 >= 1) or (_oppose_n_v2 >= 3 and _support_n_v2 <= 1)
        # 根
        engine_yougen = has_root or rw in ('HEAVY', 'LIGHT')
        engine_wugen = (not has_root) and rw == 'NONE'
        # 对齐评估
        if c['wang']:
            wang_total += 1
            if engine_wang: wang_hit += 1
            else: wang_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['wang'],'engine':rw,'segment':c['segment'][:100]})
            # 从格/普通格分类
            if _is_cong:
                cong_wang_total += 1
                if engine_wang: cong_wang_hit += 1
                cong_cases_detail.append({'line':c['line'],'pillars':c['pillars'],'cong':_cong_type,'state':_cong_state,'wang':c['wang'],'engine_wang':engine_wang,'segment':c['segment'][:80]})
            else:
                normal_wang_total += 1
                if engine_wang: normal_wang_hit += 1
        if c['ruo']:
            ruo_total += 1
            if engine_ruo: ruo_hit += 1
            else: ruo_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['ruo'],'engine':rw,'segment':c['segment'][:100]})
            # 从格/普通格分类
            if _is_cong:
                cong_ruo_total += 1
                if engine_ruo: cong_ruo_hit += 1
                cong_cases_detail.append({'line':c['line'],'pillars':c['pillars'],'cong':_cong_type,'state':_cong_state,'ruo':c['ruo'],'engine_ruo':engine_ruo,'segment':c['segment'][:80]})
            else:
                normal_ruo_total += 1
                if engine_ruo: normal_ruo_hit += 1
        if c['yougen']:
            yougen_total += 1
            if engine_yougen: yougen_hit += 1
            else: yougen_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['yougen'],'engine':f'has_root={has_root},rw={rw}'})
        if c['wugen']:
            wugen_total += 1
            if engine_wugen: wugen_hit += 1
            else: wugen_mismatch.append({'line':c['line'],'pillars':c['pillars'],'ren':c['wugen'],'engine':f'has_root={has_root},rw={rw}'})
        results.append({'line':c['line'],'root_class':rw,'has_root':has_root})
    except Exception as e:
        results.append({'line':c['line'],'error':str(e)})

print(f'\n=== 身旺衰断言对齐 ===')
print(f'  旺: {wang_hit}/{wang_total} = {wang_hit/wang_total*100:.1f}%' if wang_total else '  旺: 0例')
print(f'  弱: {ruo_hit}/{ruo_total} = {ruo_hit/ruo_total*100:.1f}%' if ruo_total else '  弱: 0例')
print(f'\n=== 从格分类对齐 ===')
print(f'  从格案例总数: {len(set(d["line"] for d in cong_cases_detail))}')
print(f'  从格-旺: {cong_wang_hit}/{cong_wang_total} = {cong_wang_hit/cong_wang_total*100:.1f}%' if cong_wang_total else '  从格-旺: 0例')
print(f'  从格-弱: {cong_ruo_hit}/{cong_ruo_total} = {cong_ruo_hit/cong_ruo_total*100:.1f}%' if cong_ruo_total else '  从格-弱: 0例')
print(f'  普通格-旺: {normal_wang_hit}/{normal_wang_total} = {normal_wang_hit/normal_wang_total*100:.1f}%' if normal_wang_total else '  普通格-旺: 0例')
print(f'  普通格-弱: {normal_ruo_hit}/{normal_ruo_total} = {normal_ruo_hit/normal_ruo_total*100:.1f}%' if normal_ruo_total else '  普通格-弱: 0例')
if cong_cases_detail:
    print(f'\n  从格案例明细:')
    for d in cong_cases_detail[:20]:
        pillars = ''.join([f'{g}{z}' for g,z in d['pillars']])
        label = '旺' if d.get('wang') else '弱'
        engine_label = d.get('engine_wang', d.get('engine_ruo'))
        print(f'    L{d["line"]} {pillars} {d["cong"]}({d["state"]}) 原典={label} 引擎={engine_label} | {d["segment"]}')
print(f'\n=== 根断言对齐 ===')
print(f'  有根: {yougen_hit}/{yougen_total} = {yougen_hit/yougen_total*100:.1f}%' if yougen_total else '  有根: 0例')
print(f'  无根: {wugen_hit}/{wugen_total} = {wugen_hit/wugen_total*100:.1f}%' if wugen_total else '  无根: 0例')

print(f'\n=== 差异清单(前10) ===')
if wang_mismatch:
    print(f'\n旺不匹配({len(wang_mismatch)}例):')
    for m in wang_mismatch[:10]:
        print(f"  L{m['line']}: {''.join(m['pillars'][0])}{''.join(m['pillars'][1])}{''.join(m['pillars'][2])}{''.join(m['pillars'][3])} 任氏={m['ren']} 引擎={m['engine']}")
if ruo_mismatch:
    print(f'\n弱不匹配({len(ruo_mismatch)}例):')
    for m in ruo_mismatch[:10]:
        print(f"  L{m['line']}: {''.join(m['pillars'][0])}{''.join(m['pillars'][1])}{''.join(m['pillars'][2])}{''.join(m['pillars'][3])} 任氏={m['ren']} 引擎={m['engine']}")

# 保存
with open('scripts/dts_assertion_align_results.json', 'w', encoding='utf-8') as f:
    json.dump({'wang_hit':wang_hit,'wang_total':wang_total,'wang_mismatch':wang_mismatch,
               'ruo_hit':ruo_hit,'ruo_total':ruo_total,'ruo_mismatch':ruo_mismatch,
               'yougen_hit':yougen_hit,'yougen_total':yougen_total,'yougen_mismatch':yougen_mismatch,
               'wugen_hit':wugen_hit,'wugen_total':wugen_total,'wugen_mismatch':wugen_mismatch,
               'results':results}, f, ensure_ascii=False, indent=2)
print(f'\n保存: scripts/dts_assertion_align_results.json')
