# -*- coding: utf-8 -*-
"""P160 QTBJ 调候候选查表视图 · 第二刀 Golden
边界: 纯日干×月令查表候选+原文次序; 并列不裁; 富贵/岁运/从化/降级全禁; 与PZZQ独立namespace; 不接生产。
甲木/乙木十二月已全量录入(本Golden覆盖); 丙火等仍 NOT_REGISTERED。
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


def mk(mb, day_gz=('甲', '寅')):
    return {'year': ['己', '巳'], 'month': ['戊', mb], 'day': list(day_gz), 'hour': ['丙', '寅']}


def seq(r):
    return [c['stem'] for c in r['climate_candidates']]


def orders(r):
    return [c['order'] for c in r['climate_candidates']]


# 甲木十二月全量次序
CASES = [
    ('甲', '寅', ['丙', '癸'], 'QTBJ-003-002'),
    ('甲', '卯', ['庚', '丁'], 'QTBJ-004-001'),
    ('甲', '辰', ['庚', '壬'], 'QTBJ-005-001'),
    ('甲', '巳', ['癸', '丁'], 'QTBJ-006-001'),
    ('甲', '午', ['癸', '丁', '庚'], 'QTBJ-007-001'),
    ('甲', '未', ['丁', '庚'], 'QTBJ-007-001'),
    ('甲', '申', ['丁', '庚'], 'QTBJ-008-001'),
    ('甲', '酉', ['丁', '丙', '庚'], 'QTBJ-009-001'),
    ('甲', '戌', ['丁', '癸'], 'QTBJ-010-001'),
    ('甲', '亥', ['庚', '丁', '丙'], 'QTBJ-011-001'),
    ('甲', '子', ['丁', '庚', '丙'], 'QTBJ-012-001'),
    ('甲', '丑', ['庚', '丁'], 'QTBJ-013-001'),
    ('乙', '寅', ['丙', '癸'], 'QTBJ-014-002'),
    ('乙', '卯', ['丙', '癸'], 'QTBJ-015-001'),
    ('乙', '辰', ['癸', '丙'], 'QTBJ-016-001'),
    ('乙', '巳', ['癸', '丙'], 'QTBJ-017-001'),
    ('乙', '午', ['癸', '丙'], 'QTBJ-018-001'),
    ('乙', '未', ['癸', '丙'], 'QTBJ-019-002'),
    ('乙', '申', ['丙', '癸'], 'QTBJ-020-001'),
    ('乙', '酉', ['癸', '丙'], 'QTBJ-021-001'),
    ('乙', '戌', ['癸', '辛'], 'QTBJ-022-001'),
    ('乙', '亥', ['丙', '戊'], 'QTBJ-023-001'),
    ('乙', '子', ['丙'], 'QTBJ-024-001'),
    ('乙', '丑', ['丙'], 'QTBJ-025-001'),
    ('丙', '寅', ['壬', '庚'], 'QTBJ-027-002'),
    ('丙', '卯', ['壬', '庚'], 'QTBJ-028-001'),
    ('丙', '辰', ['壬', '甲'], 'QTBJ-029-001'),
    ('丙', '巳', ['壬', '庚'], 'QTBJ-030-001'),
    ('丙', '午', ['壬', '庚'], 'QTBJ-031-001'),
    ('丙', '未', ['壬', '庚'], 'QTBJ-032-001'),
    ('丙', '申', ['壬'], 'QTBJ-033-001'),
    ('丙', '酉', ['壬'], 'QTBJ-034-001'),
    ('丙', '戌', ['壬', '甲'], 'QTBJ-035-001'),
    ('丙', '亥', ['甲', '戊', '庚'], 'QTBJ-036-001'),
    ('丙', '子', ['壬', '戊'], 'QTBJ-037-001'),
    ('丙', '丑', ['壬', '甲'], 'QTBJ-038-001'),
    ('丁', '寅', ['庚', '甲'], 'QTBJ-039-001'),
    ('丁', '卯', ['庚', '甲'], 'QTBJ-040-001'),
    ('丁', '辰', ['甲', '庚'], 'QTBJ-041-001'),
    ('丁', '巳', ['庚', '甲'], 'QTBJ-042-001'),
    ('丁', '午', ['甲', '庚'], 'QTBJ-043-002'),
    ('丁', '未', ['甲', '庚'], 'QTBJ-044-001'),
    ('丁', '申', ['甲', '丙'], 'QTBJ-045-001'),
    ('丁', '酉', ['甲', '丙', '庚'], 'QTBJ-045-001'),
    ('丁', '戌', ['甲', '庚'], 'QTBJ-045-001'),
    ('丁', '亥', ['甲', '庚'], 'QTBJ-046-002'),
    ('丁', '子', ['甲', '庚'], 'QTBJ-046-002'),
    ('丁', '丑', ['甲', '庚'], 'QTBJ-046-002'),
    ('戊', '寅', ['丙', '甲', '癸'], 'QTBJ-048-001'),
    ('戊', '卯', ['丙', '甲', '癸'], 'QTBJ-048-001'),
    ('戊', '辰', ['甲', '丙', '癸'], 'QTBJ-048-001'),
    ('戊', '巳', ['甲', '丙', '癸'], 'QTBJ-048-004'),
    ('戊', '午', ['壬', '甲'], 'QTBJ-049-001'),
    ('戊', '未', ['癸', '丙', '甲'], 'QTBJ-050-001'),
    ('戊', '申', ['丙', '癸', '甲'], 'QTBJ-051-001'),
    ('戊', '酉', ['丙', '癸'], 'QTBJ-052-001'),
    ('戊', '戌', ['甲', '癸', '丙'], 'QTBJ-053-001'),
    ('戊', '亥', ['甲', '丙'], 'QTBJ-054-001'),
    ('戊', '子', ['丙', '甲'], 'QTBJ-054-001'),
    ('戊', '丑', ['丙', '甲'], 'QTBJ-054-001'),
]

rows = {}
for dm, mb, want_seq, ev in CASES:
    r = build_climate_candidates(build(mk(mb, day_gz=(dm, '寅'))))
    rows[(dm, mb)] = r
    check('%s%s月 次序=%s' % (dm, mb, want_seq), seq(r) == want_seq, str(seq(r)))
    check('%s%s月 REGISTERED' % (dm, mb), r['state'] == 'REGISTERED')
    check('%s%s月 证据=%s' % (dm, mb, ev), ev in r['evidence_refs'])

# 已录不变(原四刀锚点)
check('三月甲木 先庚后壬', seq(rows[('甲', '辰')]) == ['庚', '壬'])
check('五月甲木 先癸后丁次庚', seq(rows[('甲', '午')]) == ['癸', '丁', '庚'])
check('八月甲木 丁先丙次庚再', seq(rows[('甲', '酉')]) == ['丁', '丙', '庚'])
check('十一月甲木 丁先庚后丙佐', seq(rows[('甲', '子')]) == ['丁', '庚', '丙'])

# 未注册: 己土等仍 NOT_REGISTERED
r_no = build_climate_candidates(build(mk('辰', day_gz=('己', '卯'))))  # 己日辰月
check('己土未注册->NOT_REGISTERED', r_no['state'] == 'NOT_REGISTERED')
check('己土未注册->空候选', r_no['candidate_count'] == 0 and r_no['climate_candidates'] == [])

# order 升序 + 无裁决字段
check('order升序', orders(rows[('甲', '午')]) == [1, 2, 3])
for k in ['selected', 'winner', 'best', 'final', 'use', 'use_stem']:
    check('无裁决字段 %s' % k, rows[('甲', '午')].get(k, 'ABSENT') == 'ABSENT')

# 独立 namespace / judgment
check('module=QTBJ_CLIMATE_VIEW', rows[('甲', '辰')]['module'] == 'QTBJ_CLIMATE_VIEW')
check('judgment=CANDIDATE_ONLY', rows[('甲', '辰')]['judgment_status'] == 'CLIMATE_CANDIDATE_ONLY')
check('挂牌QTBJ.climate_use', rows[('甲', '辰')]['namespace'] == 'QTBJ.climate_use')

# 硬禁区(剔除boundary_note): 不得含富贵/从化/降级/吉凶/强弱/评分
blob = copy.deepcopy(rows[('甲', '午')])
blob.pop('boundary_note', None)
text = json.dumps(blob, ensure_ascii=False)
banned = ['科甲', '富贵', '从化', '从格', '降级', 'degrade', '吉凶', '强', '弱',
          'score', 'weight', 'threshold', 'winner', 'selected', '用神定', '透', '得用']
for bad in banned:
    check('禁区词不出现: %s' % bad, bad not in text)

print()
print('FAILS =', fails)
sys.exit(1 if fails else 0)
