# -*- coding: utf-8 -*-
"""PATCH-160 作用发动层 ACTIVITY（审计报告 governance/audit_effectiveness_report.md §4）

只描述"作用有没有发动的结构前提"(动/静/引动候选), 不描述作用成败/吉凶/强弱/用神.
全部状态为中性结构态(ACTIVE_CANDIDATE / DORMANT / *_CANDIDATE / UNKNOWN),
不含"有用/无用/成/败/拔/伤/吉/凶"等结论词.

本文件当前实现两个模块:
  ① 透藏动静 build_activity_tou_cang
  ② 冲支三类 build_activity_clash_class
合去归属/通关候选/成势候选/化气候选 后续按审计契约逐刀加入.

原典边界:
- 透=动候选: PZZQ-007-031(露而根深/藏而不露, A级); SFTK-006-002(透出方动物, B级病药派)
- 藏=静但非永无效: DTS-027-002(伏藏之神岁运冲扶则为患; 岁运属 PATCH-215 冻结, 本层不做引发)
- 冲三类: DTS-009-003/004/005/006
  四生方寅申巳亥逢冲=生方怕动(根动候选); 四库辰戌丑未逢冲=库宜开(开候选);
  四败子午卯酉逢冲=败地逢冲仔细推(UNKNOWN, 不硬判).
"""
from typing import Any, Dict

# ---- 通用发动态 ----
ACTIVE_CANDIDATE = 'ACTIVE_CANDIDATE'   # 发动前提具备(如透干于外), 仅"动候选", 非有力/有用
DORMANT = 'DORMANT'                     # 静(如藏而不透), 原局发动不彰, 非无力/无用
ABSENT_STATE = 'ABSENT'                 # 不现
UNKNOWN_STATE = 'UNKNOWN'               # 原典要求 case-by-case, fail-closed

# ---- 冲支三类 ----
SHENG_FANG = set('寅申巳亥')   # 四生方
KU = set('辰戌丑未')           # 四库
BAI_DI = set('子午卯酉')       # 四败(四旺)

SHENGFANG_CLASH = 'SHENGFANG_CLASH_ROOT_MOVED_CANDIDATE'  # 生方冲, 根动候选(不判伤)
KU_CLASH = 'KU_CLASH_OPENED_CANDIDATE'                    # 库冲, 开候选(不判吉凶)
BAI_CLASH = 'BAI_CLASH_UNKNOWN'                           # 败地冲, 原典命细推, UNKNOWN

_CLASH_NOTE = {
    SHENGFANG_CLASH: '四生方逢冲, 原典"生方怕动/冲则根动", 仅根动候选, 不判根拔伤根',
    KU_CLASH: '四库逢冲, 原典"库宜开", 仅开库候选, 不判开库吉凶',
    BAI_CLASH: '四败逢冲, 原典"败地逢冲仔细推", case-by-case, 不硬判',
}


def classify_clash_branch(branch: str) -> str:
    if branch in SHENG_FANG:
        return SHENGFANG_CLASH
    if branch in KU:
        return KU_CLASH
    if branch in BAI_DI:
        return BAI_CLASH
    return UNKNOWN_STATE


# ============ 模块① 透藏动静 ============
def build_activity_tou_cang(tou_cang: Dict[str, Any]) -> Dict[str, Any]:
    """输入 D13 build_tou_cang 输出. 透(含透藏俱备)=动候选; 藏而不透=静."""
    groups = {}
    for gname, g in (tou_cang or {}).get('groups', {}).items():
        tou = bool(g.get('tou'))
        cang = bool(g.get('cang'))
        if tou:
            state = ACTIVE_CANDIDATE
        elif cang:
            state = DORMANT
        else:
            state = ABSENT_STATE
        groups[gname] = {
            'activity_state': state,
            'tou': tou,
            'cang': cang,
            'tou_cang_state': g.get('state'),
        }
    return {
        'module': 'ACTIVITY_TOU_CANG',
        'patch': 'PATCH-160-ACTIVITY-1',
        'groups': groups,
        'judgment_status': 'ACTIVITY_STRUCTURE_ONLY',
        'boundary_note': (
            '透=发动候选(非有力/有用/吉), 藏不透=静(非无力/无用/废); '
            '藏者岁运引发属 PATCH-215 冻结不做; 盖头压制为 B 级涉运不做; 不输出 STRONG/WEAK'
        ),
        'evidence_refs': ['PZZQ-007-031', 'SFTK-006-002', 'DTS-027-002'],
    }


# ============ ACTIVITY 层组装(独立于 9 维结构网络, 消费已封板 D13/D8 输出) ============
def build_activity_layer(tou_cang: Dict[str, Any] = None,
                         root_relations: Dict[str, Any] = None) -> Dict[str, Any]:
    return {
        'layer': 'DAYMASTER_ACTIVITY',
        'patch': 'PATCH-160-ACTIVITY',
        'tou_cang_activity': build_activity_tou_cang(tou_cang or {'groups': {}}),
        'clash_class': build_activity_clash_class(root_relations or {}),
        'judgment_status': 'ACTIVITY_STRUCTURE_ONLY_NO_EFFECT',
        'boundary_note': (
            '作用发动层: 仅记录动/静/引动前提(候选态); 不输出有用无用/成败/化真/成势/'
            '喜忌/吉凶/STRONG/WEAK; 成败层须另取用神授权; 岁运引发属 PATCH-215 冻结'
        ),
    }


# ============ 模块② 冲支三类 ============
def build_activity_clash_class(root_relations: Dict[str, Any]) -> Dict[str, Any]:
    """输入 D8 build_root_relations 输出. 对其中 relation=CLASH 的日主根支按地支三类标注."""
    per_pillar = {}
    for pillar, d in (root_relations or {}).get('root_branch_relations', {}).items():
        if not d.get('is_root'):
            continue
        for rel in d.get('relations', []):
            if rel.get('relation') == 'CLASH':
                cls = classify_clash_branch(d['branch'])
                per_pillar[pillar] = {
                    'branch': d['branch'],
                    'with_branches': rel.get('with_branches', []),
                    'clash_class': cls,
                }
    return {
        'module': 'ACTIVITY_CLASH_CLASS',
        'patch': 'PATCH-160-ACTIVITY-2',
        'root_clash_pillars': per_pillar,
        'judgment_status': 'ACTIVITY_STRUCTURE_ONLY',
        'boundary_note': (
            '仅按四生/四库/四败标注冲的发动类型; 不判根拔/伤根/衰者拔旺者发/开库吉凶; '
            '败地冲保持 UNKNOWN; 刑穿有动不动, 效力轻于冲, 不在本模块; 不输出 STRONG/WEAK'
        ),
        'evidence_refs': ['DTS-009-003', 'DTS-009-004', 'DTS-009-005', 'DTS-009-006', 'DTS-008-014'],
    }
