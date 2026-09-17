# -*- coding: utf-8 -*-
"""P160-C 得时不旺/失时不弱 结构条件精确化 Golden
边界: 只把"有无"升级为"成党=透干且通根"; 命题 state 恒 UNKNOWN; 不输出 STRONG/WEAK;
不计数/不权重; evidence 绑 PZZQ-005-005(論干支 得时不旺失时不弱原文)。
"""
import sys, json, copy
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_power_queries import run_queries

fails = 0


def check(name, cond, extra=''):
    global fails
    if not cond:
        fails += 1
    print(('PASS' if cond else 'FAIL'), name, extra)


def net(pillars):
    facts = build(pillars)
    pa = build_power_structure(pillars)
    hst = {pillars[k][1]: facts['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
    rc = build_root_classes(pillars, hst)
    tc = build_tou_cang(facts)
    wx = build_wang_xiang(facts, facts['day_stem'])
    rr = build_root_relations(rc, facts['combination_facts'])
    ts = build_two_side(rc, tc, rr)
    return build_power_network(pa, rc, tc, wx, rr, ts)


def qm(run):
    return {q['query_id']: q for q in run}


# 盘1: 甲日寅月(得时), 官杀金成党(庚申年金透金根, 癸酉时金) => 得时不旺 结构匹配
p1 = {'year': ['庚', '申'], 'month': ['戊', '寅'], 'day': ['甲', '寅'], 'hour': ['癸', '酉']}
m1 = qm(run_queries(net(p1)))
q1d = m1['ZP-160-QUERY-DESHI-BUWANG']
check('盘1 得时不旺 STRUCTURE_MATCH', q1d['match_type'] == 'STRUCTURE_MATCH', str(q1d['match_type']))
check('盘1 命题 state 仍 UNKNOWN', q1d['state'] == 'UNKNOWN', q1d['state'])
check('盘1 证据绑 PZZQ-005-005', 'PZZQ-005-005' in q1d['evidence_refs'])

# 盘2: 甲日寅月(得时), 庚透而无金根, 食伤火/财土均不透干 => 克泄不成党 => NO_MATCH
p2 = {'year': ['庚', '寅'], 'month': ['壬', '寅'], 'day': ['甲', '寅'], 'hour': ['甲', '子']}
m2 = qm(run_queries(net(p2)))
q2d = m2['ZP-160-QUERY-DESHI-BUWANG']
check('盘2 得时但不成党 NO_MATCH', q2d['match_type'] == 'NO_MATCH', str(q2d['match_type']))

# 盘3: 甲日申月(失时), 比劫成党(甲子年甲透, 寅日寅卯木根) => 失时不弱 结构匹配
p3 = {'year': ['甲', '子'], 'month': ['壬', '申'], 'day': ['甲', '寅'], 'hour': ['丁', '卯']}
m3 = qm(run_queries(net(p3)))
q3s = m3['ZP-160-QUERY-SHISHI-BURUO']
check('盘3 失时不弱 STRUCTURE_MATCH', q3s['match_type'] == 'STRUCTURE_MATCH', str(q3s['match_type']))
check('盘3 命题 state 仍 UNKNOWN', q3s['state'] == 'UNKNOWN', q3s['state'])
check('盘3 证据绑 PZZQ-005-005', 'PZZQ-005-005' in q3s['evidence_refs'])

# 盘4: 甲日申月(失时), 比劫木/印水均不透干 => 扶身不成党 => NO_MATCH
p4 = {'year': ['庚', '午'], 'month': ['戊', '申'], 'day': ['甲', '申'], 'hour': ['丙', '戌']}
m4 = qm(run_queries(net(p4)))
q4s = m4['ZP-160-QUERY-SHISHI-BURUO']
check('盘4 失时无成党 NO_MATCH', q4s['match_type'] == 'NO_MATCH', str(q4s['match_type']))

# CAN_REN_CAIGUAN: 盘1有根->SUPPORTED; 盘4无根->NOT_SUPPORTED
check('盘1 有根 能任财官 SUPPORTED', m1['ZP-160-QUERY-REN-CAIGUAN']['state'] == 'SUPPORTED',
      m1['ZP-160-QUERY-REN-CAIGUAN']['state'])
check('盘4 无根 能任财官 NOT_SUPPORTED', m4['ZP-160-QUERY-REN-CAIGUAN']['state'] == 'NOT_SUPPORTED',
      m4['ZP-160-QUERY-REN-CAIGUAN']['state'])
check('盘1 能任证据绑 PZZQ-005-005', 'PZZQ-005-005' in m1['ZP-160-QUERY-REN-CAIGUAN']['evidence_refs'])

# 越界防护: 三态query不得输出 STRONG/WEAK 命题
blob = copy.deepcopy(m1)
text = json.dumps(blob, ensure_ascii=False)
for bad in ['"STRONG"', '"WEAK"', '身强', '身弱', 'score', 'weight', 'threshold', 'winner', 'selected']:
    check('query 不含越界: %s' % bad, bad not in text)

print()
print('FAILS =', fails)
sys.exit(1 if fails else 0)
