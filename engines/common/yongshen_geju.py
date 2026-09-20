# -*- coding: utf-8 -*-
"""P160 PZZQ 格局用神结构视图 · 第一刀（只读派生，不重算格局）

只做两件事：
  A. GE_SHEN_CANDIDATE —— 月令定格结果的只读结构投影(格神是谁 + 顺用/逆用分类)
  B. USE_GOD_CANDIDATE —— 月令藏干透干关系下的用神变化候选枚举(并列, 不裁决)

铁律(用户裁决 P160-第1刀):
  - 只读消费 pzzq_producer_v1.pattern_candidates, 绝不重算月令定格;
  - 多候选并列保留, 禁止 winner/selected/best/primary/final;
  - 格神 ≠ 格局成立 ≠ 格局高低 ≠ 用神最终裁决;
  - 顺用/逆用仅为原典分类字段, 不得解释成吉凶成败;
  - 相神/有情无情/有力无力/成格败格/贵贱吉凶/扶抑/身强弱 一律不出现;
  - 不复活 use_god_rules/producer 死代码; 不接 production_entry; 旁路 Golden。

原典:
  PZZQ-005-007 八字用神专求月令; 财官印食善而顺用, 煞伤刃劫不善而逆用; 不向月令求用神者执假失真。
  PZZQ-005-009 月令所藏不一, 透干不同则用神变化(寅月不透甲透丙, 同知作主)。
"""
from typing import Any, Dict, List
from engines.common.pzzq_producer_v1 import produce_pattern_candidates

# 顺用(善) / 逆用(不善) 分类 —— 仅原典结构分类, 非吉凶
# 善而顺用: 财官印食; 不善而逆用: 煞伤刃劫(月劫/建禄属比劫逆用)
SHUN_YONG = 'SHUN_YONG'   # 财/官/印/食 —— 善而顺用
NI_YONG = 'NI_YONG'       # 七杀/伤官/建禄/月劫 —— 不善而逆用
SHUN_NI_UNKNOWN = 'UNKNOWN'

# 按原始十神(ten_god)分类: 财官印食=善而顺用; 煞伤+比劫(建禄/月劫)=不善而逆用
_SHUN_GROUPS = {'正财', '偏财', '正官', '正印', '偏印', '食神'}
_NI_GROUPS = {'七杀', '伤官', '比肩', '劫财'}

# 定格来源映射(producer basis -> 候选来源语义)
_BASIS_TO_SOURCE = {
    'transparent': 'TRANSPARENT_STEM',   # 月令藏干透于天干
    'month_benqi': 'BENQI',              # 不透, 取月令本气
}

_EVIDENCE = ['PZZQ-005-007', 'PZZQ-005-009']
XIANGSHEN_EVIDENCE = ['PZZQ-006-001', 'PZZQ-006-002']

# 相神候选映射 (原典: 善而顺用/不善而逆用的配合关系)
# 只输出候选类型, 不判有情/有力/成败
XIANGSHEN_MAP = {
    # 顺用(善): 财官印食
    '正财': [{'xiang_type': 'SHENG_CAI', 'name': '食神生财', 'ten_god': ['食神', '伤官']},
             {'xiang_type': 'HU_CAI', 'name': '官杀护财', 'ten_god': ['正官', '七杀']}],
    '偏财': [{'xiang_type': 'SHENG_CAI', 'name': '食神生财', 'ten_god': ['食神', '伤官']},
             {'xiang_type': 'HU_CAI', 'name': '官杀护财', 'ten_god': ['正官', '七杀']}],
    '正官': [{'xiang_type': 'SHENG_GUAN', 'name': '财生官', 'ten_god': ['正财', '偏财']},
             {'xiang_type': 'HU_GUAN', 'name': '印护官', 'ten_god': ['正印', '偏印']}],
    '正印': [{'xiang_type': 'SHENG_YIN', 'name': '官杀生印', 'ten_god': ['正官', '七杀']},
             {'xiang_type': 'HU_YIN', 'name': '比劫护印', 'ten_god': ['比肩', '劫财']}],
    '偏印': [{'xiang_type': 'SHENG_YIN', 'name': '官杀生印', 'ten_god': ['正官', '七杀']},
             {'xiang_type': 'HU_YIN', 'name': '比劫护印', 'ten_god': ['比肩', '劫财']}],
    '食神': [{'xiang_type': 'BANG_SHEN_SHI', 'name': '比劫帮身生食', 'ten_god': ['比肩', '劫财']}],
    # 逆用(不善): 煞伤刃劫
    '七杀': [{'xiang_type': 'ZHI_SHA', 'name': '食神制煞', 'ten_god': ['食神']},
             {'xiang_type': 'HUA_SHA', 'name': '印化煞', 'ten_god': ['正印', '偏印']}],
    '伤官': [{'xiang_type': 'ZHI_SHANG', 'name': '印制伤官', 'ten_god': ['正印', '偏印']},
             {'xiang_type': 'HUA_SHANG', 'name': '财化伤官', 'ten_god': ['正财', '偏财']}],
    '比肩': [{'xiang_type': 'ZHI_JIE', 'name': '官杀制比劫', 'ten_god': ['正官', '七杀']},
             {'xiang_type': 'HUA_JIE', 'name': '食伤化比劫', 'ten_god': ['食神', '伤官']}],
    '劫财': [{'xiang_type': 'ZHI_JIE', 'name': '官杀制比劫', 'ten_god': ['正官', '七杀']},
             {'xiang_type': 'HUA_JIE', 'name': '食伤化比劫', 'ten_god': ['食神', '伤官']}],
}


def classify_shun_ni(ten_god: str) -> str:
    """财官印食=顺用; 煞伤刃劫(建禄/月劫)=逆用; 否则 UNKNOWN。"""
    if ten_god in _SHUN_GROUPS:
        return SHUN_YONG
    if ten_god in _NI_GROUPS:
        return NI_YONG
    return SHUN_NI_UNKNOWN


def build_yongshen_geju(facts: Dict[str, Any]) -> Dict[str, Any]:
    """只读消费月令定格候选, 输出格神/用神变化结构候选视图。

    与上游 candidate 一一对应: 月令多藏干透多干则并列多候选;
    不透则本气单候选。全程不 selected、不评分、不判成败。
    """
    pc = produce_pattern_candidates(facts)

    candidates: List[Dict[str, Any]] = []
    for i, c in enumerate(pc.get('pattern_candidates', [])):
        tg = c.get('ten_god')
        stem = c.get('month_stem')
        basis = c.get('basis')
        # 稳定可 diff 的逻辑 ID(基于月令支+定格干, 不依赖 dict 顺序)
        cid = 'GE-%s-%s-%02d' % (facts.get('month_branch', '?'), stem or '?', i)
        candidates.append({
            'candidate_id': cid,
            'pattern_type': c.get('pattern_type'),
            'ten_god': tg,
            'month_stem': stem,
            'shun_ni_yong': classify_shun_ni(tg),      # 仅分类字段
            'candidate_source': _BASIS_TO_SOURCE.get(basis, 'UNKNOWN'),
            'source_fact_ids': c.get('evidence', []),   # 上游事实定位
            'trigger_fact_ids': c.get('evidence', []),   # 该候选由哪些事实触发
            'evidence_refs': list(_EVIDENCE),
            'status': 'CANDIDATE',
        })

    return {
        'module': 'YONGSHEN_GEJU_VIEW',
        'patch': 'P160-PZZQ-GESHEN-1',
        # 冲突命名空间归属(对齐 namespace_registry PATCH-023C): 防跨领域串规则
        'namespace': 'PZZQ.use_god',
        'namespace_type': 'pattern',
        # 格神识别视图 与 用神变化候选视图 同源同列表, 并列不裁
        'ge_shen_candidates': candidates,
        'use_god_candidates': candidates,
        'candidate_count': len(candidates),
        'judgment_status': 'GEJU_CANDIDATE_ONLY',
        'boundary_note': (
            '仅月令定格结构投影与藏干透干变化候选枚举; 多候选并列不裁决, 不输出 selected/final; '
            '顺逆用仅原典分类非吉凶; 格神≠格局成立/高低/最终用神; 相神/有情无情/有力无力/'
            '成格败格/贵贱吉凶/扶抑/身强弱均不出现; 不接 production_entry'
        ),
        'evidence_refs': list(_EVIDENCE),
    }


def build_xiangshen_candidates(facts: Dict[str, Any], ge_shen_candidates: List[Dict] = None) -> Dict[str, Any]:
    """相神候选识别 (PZZQ第二刀 · 结构化, 不判有情/有力/成败).

    原典: 善而顺用则财喜食神以相生, 生官以护财; 官喜透财以相生, 生印以护官;
          印喜官煞以相生, 劫才以护印; 食喜身旺以相生.
          不善而逆用则七煞喜食神以制伏; 伤官喜佩印以制伏, 生财以化伤;
          阳刃喜官煞以制伏; 月劫喜透官以制伏, 利用财而透食以化劫.

    只做: 根据格神类型识别相神候选类型 + 检查是否在命局中出现
    不做: 有情/有力/成格/败格/贵贱/吉凶
    """
    if ge_shen_candidates is None:
        geju_view = build_yongshen_geju(facts)
        ge_shen_candidates = geju_view.get('ge_shen_candidates', [])

    ten_god_members = facts.get('ten_god_members', [])
    all_xiangshen: List[Dict[str, Any]] = []

    for gc in ge_shen_candidates:
        tg = gc.get('ten_god', '')
        xiang_map = XIANGSHEN_MAP.get(tg, [])
        for xm in xiang_map:
            # 检查相神候选十神是否在命局中出现
            appeared = any(m.get('ten_god') in xm['ten_god'] for m in ten_god_members)
            appeared_stems = [m.get('stem') for m in ten_god_members if m.get('ten_god') in xm['ten_god']]
            all_xiangshen.append({
                'xiang_id': 'XS-%s-%s' % (gc.get('candidate_id', '?'), xm['xiang_type']),
                'ge_shen_id': gc.get('candidate_id'),
                'ge_shen_ten_god': tg,
                'xiang_type': xm['xiang_type'],
                'xiang_name': xm['name'],
                'xiang_ten_god': xm['ten_god'],
                'appeared_in_chart': appeared,
                'appeared_stems': appeared_stems,
                'status': 'CANDIDATE',
                'evidence_refs': list(XIANGSHEN_EVIDENCE),
            })

    return {
        'module': 'XIANGSHEN_CANDIDATES_VIEW',
        'patch': 'P160-PZZQ-XIANGSHEN-1',
        'namespace': 'PZZQ.xiangshen',
        'namespace_type': 'pattern',
        'xiangshen_candidates': all_xiangshen,
        'candidate_count': len(all_xiangshen),
        'appeared_count': sum(1 for x in all_xiangshen if x['appeared_in_chart']),
        'judgment_status': 'XIANGSHEN_CANDIDATE_ONLY',
        'boundary_note': (
            '相神候选仅基于格神类型的原典配合关系枚举; 只检查是否在命局中出现, '
            '不判有情/无情/有力/无力/成格/败格/贵贱/吉凶; 多候选并列不裁决'
        ),
        'evidence_refs': list(XIANGSHEN_EVIDENCE),
    }
