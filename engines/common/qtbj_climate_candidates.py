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
    ('乙', '寅'): {  # 正月乙木: 天气犹有余寒, 丙火为先, 癸水次之
        'candidates': [('丙', 1), ('癸', 2)],
        'evidence_refs': ['QTBJ-014-002'],
    },
    ('乙', '卯'): {  # 二月乙木: 阳气渐升, 以丙为君癸为臣(专用丙癸)
        'candidates': [('丙', 1), ('癸', 2)],
        'evidence_refs': ['QTBJ-015-001'],
    },
    ('乙', '辰'): {  # 三月乙木: 阳气愈炽, 先癸后丙
        'candidates': [('癸', 1), ('丙', 2)],
        'evidence_refs': ['QTBJ-016-001'],
    },
    ('乙', '巳'): {  # 四月乙木: 木性枯焦, 专用癸水, 丙火酌用
        'candidates': [('癸', 1), ('丙', 2)],
        'evidence_refs': ['QTBJ-017-001'],
    },
    ('乙', '午'): {  # 五月乙木: 丁火司权禾稼俱旱, 用癸滋(癸为先)
        'candidates': [('癸', 1), ('丙', 2)],
        'evidence_refs': ['QTBJ-018-001'],
    },
    ('乙', '未'): {  # 六月乙木: 夏月专用癸水, 丙火酌用, 庚辛次之
        'candidates': [('癸', 1), ('丙', 2)],
        'evidence_refs': ['QTBJ-019-002'],
    },
    ('乙', '申'): {  # 七月乙木: 金神司令, 先丙后癸
        'candidates': [('丙', 1), ('癸', 2)],
        'evidence_refs': ['QTBJ-020-001'],
    },
    ('乙', '酉'): {  # 八月乙木: 白露后专用癸滋桂, 秋分后宜丙癸次之
        'candidates': [('癸', 1), ('丙', 2)],
        'evidence_refs': ['QTBJ-021-001'],
    },
    ('乙', '戌'): {  # 九月乙木: 根枯叶落赖癸水滋养, 辛金发水之源
        'candidates': [('癸', 1), ('辛', 2)],
        'evidence_refs': ['QTBJ-022-001'],
    },
    ('乙', '亥'): {  # 十月乙木: 壬水司令, 取丙为用, 戊土为次
        'candidates': [('丙', 1), ('戊', 2)],
        'evidence_refs': ['QTBJ-023-001'],
    },
    ('乙', '子'): {  # 十一月乙木: 一阳来复, 专用丙火解冻(戊制水不可作用)
        'candidates': [('丙', 1)],
        'evidence_refs': ['QTBJ-024-001'],
    },
    ('乙', '丑'): {  # 十二月乙木: 木寒宜丙, 专以丙火为用
        'candidates': [('丙', 1)],
        'evidence_refs': ['QTBJ-025-001'],
    },
    ('丙', '寅'): {  # 正月丙火: 专用壬水扶阳, 庚金佐之
        'candidates': [('壬', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-027-002'],
    },
    ('丙', '卯'): {  # 二月丙火: 阳气舒兆专用壬水, 庚辛佐使
        'candidates': [('壬', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-028-001'],
    },
    ('丙', '辰'): {  # 三月丙火: 用壬水, 甲木为辅(壬甲两透)
        'candidates': [('壬', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-029-001'],
    },
    ('丙', '巳'): {  # 四月丙火: 专用壬水解炎, 金为佐(得庚发水源)
        'candidates': [('壬', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-030-001'],
    },
    ('丙', '午'): {  # 五月丙火: 愈炎得壬, 庚高透方为上命
        'candidates': [('壬', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-031-001'],
    },
    ('丙', '未'): {  # 六月丙火: 壬水为用, 取庚辅佐
        'candidates': [('壬', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-032-001'],
    },
    ('丙', '申'): {  # 七月丙火: 日近西山仍用壬水辅映光辉
        'candidates': [('壬', 1)],
        'evidence_refs': ['QTBJ-033-001'],
    },
    ('丙', '酉'): {  # 八月丙火: 余光存于湖海仍用壬水转映
        'candidates': [('壬', 1)],
        'evidence_refs': ['QTBJ-034-001'],
    },
    ('丙', '戌'): {  # 九月丙火: 壬水用, 甲木为辅
        'candidates': [('壬', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-035-001'],
    },
    ('丙', '亥'): {  # 十月丙火: 太阳失令, 甲戊庚出干(火旺酌用壬)
        'candidates': [('甲', 1), ('戊', 2), ('庚', 3)],
        'evidence_refs': ['QTBJ-036-001'],
    },
    ('丙', '子'): {  # 十一月丙火: 冬至一阳生, 壬水为最, 戊土佐之
        'candidates': [('壬', 1), ('戊', 2)],
        'evidence_refs': ['QTBJ-037-001'],
    },
    ('丙', '丑'): {  # 十二月丙火: 侮雪欺霜喜壬为用, 甲为辅
        'candidates': [('壬', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-038-001'],
    },
    ('丁', '寅'): {  # 正月丁火: 甲木当权为母, 非庚劈甲何以引丁
        'candidates': [('庚', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-039-001'],
    },
    ('丁', '卯'): {  # 二月丁火: 湿乙伤丁, 先庚后甲
        'candidates': [('庚', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-040-001'],
    },
    ('丁', '辰'): {  # 三月丁火: 先用甲木引丁制土, 次看庚金
        'candidates': [('甲', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-041-001'],
    },
    ('丁', '巳'): {  # 四月丁火: 取甲引丁必用庚劈甲
        'candidates': [('庚', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-042-001'],
    },
    ('丁', '午'): {  # 五月丁火: 须用甲木, 又要庚劈甲
        'candidates': [('甲', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-043-002'],
    },
    ('丁', '未'): {  # 六月丁火: 得甲出干, 无庚不妙(甲引丁庚劈甲)
        'candidates': [('甲', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-044-001'],
    },
    ('丁', '申'): {  # 七月丁火: 三秋甲庚丙并用, 七月甲丙(申中有庚)
        'candidates': [('甲', 1), ('丙', 2)],
        'evidence_refs': ['QTBJ-045-001'],
    },
    ('丁', '酉'): {  # 八月丁火: 甲丙庚皆用
        'candidates': [('甲', 1), ('丙', 2), ('庚', 3)],
        'evidence_refs': ['QTBJ-045-001'],
    },
    ('丁', '戌'): {  # 九月丁火: 专用甲庚
        'candidates': [('甲', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-045-001'],
    },
    ('丁', '亥'): {  # 三冬丁火: 专用庚甲, 甲木为尊庚金佐之
        'candidates': [('甲', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-046-002'],
    },
    ('丁', '子'): {  # 三冬丁火: 专用庚甲, 甲木为尊庚金佐之
        'candidates': [('甲', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-046-002'],
    },
    ('丁', '丑'): {  # 三冬丁火: 专用庚甲, 甲木为尊庚金佐之
        'candidates': [('甲', 1), ('庚', 2)],
        'evidence_refs': ['QTBJ-046-002'],
    },
    ('戊', '寅'): {  # 正月戊土: 正二月先丙后甲, 癸又次
        'candidates': [('丙', 1), ('甲', 2), ('癸', 3)],
        'evidence_refs': ['QTBJ-048-001'],
    },
    ('戊', '卯'): {  # 二月戊土: 正二月先丙后甲, 癸又次
        'candidates': [('丙', 1), ('甲', 2), ('癸', 3)],
        'evidence_refs': ['QTBJ-048-001'],
    },
    ('戊', '辰'): {  # 三月戊土: 三月先甲后丙, 癸又次
        'candidates': [('甲', 1), ('丙', 2), ('癸', 3)],
        'evidence_refs': ['QTBJ-048-001'],
    },
    ('戊', '巳'): {  # 四月戊土: 先用甲疏, 取丙癸为佐
        'candidates': [('甲', 1), ('丙', 2), ('癸', 3)],
        'evidence_refs': ['QTBJ-048-004'],
    },
    ('戊', '午'): {  # 五月戊土: 先看壬水, 次取甲木(丙火酌用)
        'candidates': [('壬', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-049-001'],
    },
    ('戊', '未'): {  # 六月戊土: 先看癸水, 次用丙火, 甲木再次
        'candidates': [('癸', 1), ('丙', 2), ('甲', 3)],
        'evidence_refs': ['QTBJ-050-001'],
    },
    ('戊', '申'): {  # 七月戊土: 先丙后癸, 甲木次之
        'candidates': [('丙', 1), ('癸', 2), ('甲', 3)],
        'evidence_refs': ['QTBJ-051-001'],
    },
    ('戊', '酉'): {  # 八月戊土: 先丙后癸, 不必木疏
        'candidates': [('丙', 1), ('癸', 2)],
        'evidence_refs': ['QTBJ-052-001'],
    },
    ('戊', '戌'): {  # 九月戊土: 先看用木(甲), 次取癸水, 后取丙火
        'candidates': [('甲', 1), ('癸', 2), ('丙', 3)],
        'evidence_refs': ['QTBJ-053-001'],
    },
    ('戊', '亥'): {  # 十月戊土: 先用甲木, 次取丙火
        'candidates': [('甲', 1), ('丙', 2)],
        'evidence_refs': ['QTBJ-054-001'],
    },
    ('戊', '子'): {  # 十一二月戊土: 严寒丙火为尊, 甲木为佐
        'candidates': [('丙', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-054-001'],
    },
    ('戊', '丑'): {  # 十一二月戊土: 严寒丙火为尊, 甲木为佐
        'candidates': [('丙', 1), ('甲', 2)],
        'evidence_refs': ['QTBJ-054-001'],
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
