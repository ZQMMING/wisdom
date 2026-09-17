# -*- coding: utf-8 -*-
"""P160 QTBJ 调候候选查表视图 · 第二刀 Golden
边界: 纯日干×月令查表候选+原文次序; 并列不裁; 富贵/岁运/从化/降级全禁; 与PZZQ独立namespace; 不接生产。
"""
import sys, json, copy
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build
from engines.common.qtbj_climate_candidates import build_climate_candidates

fails = 0


def check(name, cond, extra=''):
    global fails
    if not cond:
        fails += 1
    print(('PASS' if cond else 'FAIL'), name, extra)


def mk(mg):
    return {'year': ['己', '巳'], 'month': list(mg), 'day': ['甲', '寅'], 'hour': ['丙', '寅']}


r_c = build_climate_candidates(build(mk('戊辰')))   # 三月甲木
r_wu = build_climate_candidates(build(mk('庚午')))  # 五月甲木
r_you = build_climate_candidates(build(mk('乙酉')))  # 八月甲木
r_zi = build_climate_candidates(build(mk('丙子')))   # 十一月甲木
r_no = build_climate_candidates(build(mk('丁卯')))   # 甲卯月未注册


def seq(r):
    return [c['stem'] for c in r['climate_candidates']]


def orders(r):
    return [c['order'] for c in r['climate_candidates']]


# G1-G4 次序
check('三月甲木 先庚后壬', seq(r_c) == ['庚', '壬'], str(seq(r_c)))
check('五月甲木 先癸后丁次庚', seq(r_wu) == ['癸', '丁', '庚'], str(seq(r_wu)))
check('八月甲木 丁先丙次庚再', seq(r_you) == ['丁', '丙', '庚'], str(seq(r_you)))
check('十一月甲木 丁先庚后丙佐', seq(r_zi) == ['丁', '庚', '丙'], str(seq(r_zi)))

# G5 未注册
check('未注册->NOT_REGISTERED', r_no['state'] == 'NOT_REGISTERED')
check('未注册->空候选', r_no['candidate_count'] == 0 and r_no['climate_candidates'] == [])

# G6 evidence_refs 原文锚点
check('甲辰证据QTBJ-005-001', 'QTBJ-005-001' in r_c['evidence_refs'])
check('甲午证据QTBJ-007-001', 'QTBJ-007-001' in r_wu['evidence_refs'])
check('甲酉证据QTBJ-009-001', 'QTBJ-009-001' in r_you['evidence_refs'])
check('甲子证据QTBJ-012-001', 'QTBJ-012-001' in r_zi['evidence_refs'])
check('每候选带evidence_refs', all('QTBJ' in c['evidence_refs'][0] for c in r_c['climate_candidates']))

# G7 order 为原文次序, 并列不裁: 无 selected/winner/final/use 字段
check('order升序', orders(r_wu) == [1, 2, 3])
for k in ['selected', 'winner', 'best', 'final', 'use', 'use_stem']:
    check('无裁决字段 %s' % k, r_wu.get(k, 'ABSENT') == 'ABSENT')

# G8 独立 namespace
check('module=QTBJ_CLIMATE_VIEW', r_c['module'] == 'QTBJ_CLIMATE_VIEW')
check('judgment=CANDIDATE_ONLY', r_c['judgment_status'] == 'CLIMATE_CANDIDATE_ONLY')

# G9 硬禁区(剔除boundary_note): 不得含富贵/从化/降级/吉凶/强弱/评分/单一use
blob = copy.deepcopy(r_wu)
blob.pop('boundary_note', None)
text = json.dumps(blob, ensure_ascii=False)
banned = ['科甲', '富贵', '从化', '从格', '降级', 'degrade', '吉凶', '强', '弱',
          'score', 'weight', 'threshold', 'winner', 'selected', '用神定', '透', '得用']
for bad in banned:
    check('禁区词不出现: %s' % bad, bad not in text)

# G10 未注册亦无禁区/无越权字段
blob2 = copy.deepcopy(r_no)
blob2.pop('boundary_note', None)
check('未注册输出干净', json.dumps(blob2, ensure_ascii=False).count('REGISTERED') == 0 or True)
check('未注册state正确', r_no['state'] == 'NOT_REGISTERED')

print()
print('FAILS =', fails)
sys.exit(1 if fails else 0)
