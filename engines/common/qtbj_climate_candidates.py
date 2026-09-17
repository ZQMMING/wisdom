# -*- coding: utf-8 -*-
"""P160 QTBJ 调候候选查表视图 · 第二刀（旁路只读查表, 不碰旧 climate 主链）

只做一件事:
  日干 × 月令 -> 《穷通宝鉴》原文所载调候干及其先后次序(纯查表候选, 并列不裁)。

与第一刀 PZZQ 格神视图并列、独立 namespace, 不混成"总用神":
  - 格局用神(PZZQ) 与 调候用神(QTBJ) 各自记录, 互不覆盖;
  - 不判断调候干是否透出/得用, 不判富贵/岁运喜忌/从化/降级;
  - order 只是原文所载先后次序, 非评分/权重/优先级裁决;
  - 未在本表录入的日干月令一律 NOT_REGISTERED, 不编造、不补全。

原典锚点(甲木十二月全):
  QTBJ-003-002 正月甲木 初春余寒, 丙暖癸滋(寒木向阳)
  QTBJ-004-001 二月甲木 庚得所名阳刃架杀, 木旺宜丁火之光辉
  QTBJ-005-001 三月甲木 先取庚金次用壬水
  QTBJ-006-001 四月甲木 退气丙火司权, 先癸后丁
  QTBJ-007-001 五六月甲木 五月先癸后丁庚次之; 六月先丁后庚无癸亦可
  QTBJ-008-001 七月甲木 先丁后庚, 丁庚两全
  QTBJ-009-001 八月甲木 丁火为先, 次用丙火, 庚金再次
  QTBJ-010-001 九月甲木 独爱丁火, 壬癸滋扶(专用丁癸)
  QTBJ-011-001 十月甲木 庚丁为要, 丙火次之
  QTBJ-012-001 十一月甲木 丁先庚后, 丙火佐之
  QTBJ-013-001 十二月甲木 先用庚劈甲引丁火
"""
from typing import Any, Dict, List

# 日干 × 月令 -> 调候候选干(按原文先后次序)
# 仅录有直接原文锚点的代表条; 其余 NOT_REGISTERED
_CLIMATE_TABLE: Dict = {
    ('甲', '寅'): {  # 正月甲木: 初春余寒, 火暖为主, 癸滋佐(寒木向阳)
        'candidates': [('丙', 1), ('癸', 2)],
        'evidence_refs': ['QTBJ-003-002'],
    },
    ('甲', '卯'): {  # 二月甲木: 庚金得所名阳刃架杀, 木旺宜火(丁)之光辉
        'candidates': [('庚', 1), ('丁', 2)],
        'evidence_refs': ['QTBJ-004-001'],
    },
    ('甲', '辰'): {  # 三月甲木: 先取庚金, 次用壬水
        'candidates': [('庚', 1), ('壬', 2)],
        'evidence_refs': ['QTBJ-005-001'],
    },
    ('甲', '巳'): {  # 四月甲木: 退气丙火司权, 先癸后丁(庚太多反受病)
        'candidates': [('癸', 1), ('丁', 2)],
        'evidence_refs': ['QTBJ-006-001'],
    },
    ('甲', '午'): {  # 五六月甲木: 五月先癸后丁, 庚金次之
        'candidates': [('癸', 1), ('丁', 2), ('庚', 3)],
        'evidence_refs': ['QTBJ-007-001'],
    },
    ('甲', '未'): {  # 六月甲木: 三伏生寒丁火退气, 先丁后庚, 无癸亦可
        'candidates': [('丁', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-007-001'],
    },
    ('甲', '申'): {  # 七月甲木: 木性枯槁金土乘旺, 先丁后庚
        'candidates': [('丁', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-008-001'],
    },
    ('甲', '酉'): {  # 八月甲木: 木囚金旺, 丁火为先, 次用丙火, 庚金再次
        'candidates': [('丁', 1), ('丙', 2), ('庚', 3)],
        'evidence_refs': ['QTBJ-009-001'],
    },
    ('甲', '戌'): {  # 九月甲木: 木星凋零, 独爱丁火, 壬癸滋扶(专用丁癸)
        'candidates': [('丁', 1), ('癸', 2)],
        'evidence_refs': ['QTBJ-010-001'],
    },
    ('甲', '亥'): {  # 十月甲木: 庚丁为要, 丙火次之(忌壬泛身须戊制, 戊不入主用)
        'candidates': [('庚', 1), ('丁', 2), ('丙', 3)],
        'evidence_refs': ['QTBJ-011-001'],
    },
    ('甲', '子'): {  # 十一月甲木: 丁先庚后, 丙火佐之
        'candidates': [('丁', 1), ('庚', 2), ('丙', 3)],
        'evidence_refs': ['QTBJ-012-001'],
    },
    ('甲', '丑'): {  # 十二月甲木: 先用庚劈甲, 引丁火通明
        'candidates': [('庚', 1), ('丁', 2)],
        'evidence_refs': ['QTBJ-013-001'],
    },
}


def build_climate_candidates(facts: Dict[str, Any]) -> Dict[str, Any]:
    """只读查表: 日干×月令 -> 调候候选干+次序。不判透出/富贵/从化/岁运。"""
    dm = facts['day_stem']
    mb = facts['month_branch']
    row = _CLIMATE_TABLE.get((dm, mb))

    out = {
        'module': 'QTBJ_CLIMATE_VIEW',
        'patch': 'P160-QTBJ-CLIMATE-2',
        # 冲突命名空间归属(对齐 namespace_registry PATCH-023C): 防跨领域串规则
        'namespace': 'QTBJ.climate_use',
        'namespace_type': 'climate',
        'day_master': dm,
        'month_branch': mb,
        'climate_candidates': [],
        'candidate_count': 0,
        'judgment_status': 'CLIMATE_CANDIDATE_ONLY',
        'boundary_note': (
            '仅《穷通宝鉴》日干×月令原文所载调候干及先后次序的查表投影; '
            'order 为原文次序非评分; 并列不裁, 不 selected; 不判断调候干透出/得用; '
            '不录富贵/岁运喜忌/从化/降级; 与 PZZQ 格局用神独立 namespace, 不混为总用神; '
            '未录入条目返回 NOT_REGISTERED, 不补全不编造; 不接 production_entry'
        ),
        'evidence_refs': [],
    }

    if row is None:
        out['state'] = 'NOT_REGISTERED'
        out['note'] = '该日干月令调候未在本表录入, 待逐条原文补录'
        return out

    cands: List[Dict[str, Any]] = []
    for stem, order in row['candidates']:
        cands.append({
            'candidate_id': 'CL-%s-%s-%s-%d' % (dm, mb, stem, order),
            'stem': stem,
            'order': order,                 # 原文先后次序, 非权重
            'evidence_refs': list(row['evidence_refs']),
            'status': 'CANDIDATE',
        })
    # 按原文次序排列(表内已排)
    cands.sort(key=lambda c: c['order'])
    out['climate_candidates'] = cands
    out['candidate_count'] = len(cands)
    out['state'] = 'REGISTERED'
    out['evidence_refs'] = list(row['evidence_refs'])
    return out
