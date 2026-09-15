# -*- coding: utf-8 -*-
"""003B-02 修正：补入 DTS-017-002（病药/中和） + PZZQ-007-005（清浊/杂气）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
data = json.load(io.open(P, encoding='utf-8'))

# 1. BING_YAO 补 DTS-017-002（中和论注，有病去病语境）
data['domain_07_bing_yao']['books']['DTS'] = [
    {
        'domain_id': 'BING_YAO',
        'term_cluster_id': 'BING_YAO_SFTK',
        'surface_form': '有病方為貴，無傷不是奇，舉傷而言之也。至格中如去病，才祿兩相宜，則又中和矣',
        'source_id': 'DTS-017-002',
        'chapter_id': '通天論·中和論',
        'text_layer': 'ANNOTATION',
        'object_type': 'PATTERN',
        'semantic_role': 'MEDICINE_REF',
        'semantic_definition': 'DTS 病药表述（中和论注）：有病去病归中和；语境为中和论，勿与 SFTK 病药诊断混同',
        'verified_scope': 'PARTIAL',
        'scope_priority': 'SECONDARY',
        'excluded_scope': '中和論語境；病≠SFTK 病藥診斷；B1注層',
        'evidence_grade': 'B',
        'attribution': 'ORIGINAL_ANNOTATION',
        'execution_eligibility': 'SUPPORTING_RULE_ONLY',
    }
]

# 2. QING_ZHUO_ZHEN_JIA 补 PZZQ-007-005（杂气取清，PZZQ 用「雜」表达清浊）
data['domain_08_qing_zhuo_zhen_jia']['books']['PZZQ'] = [
    {
        'domain_id': 'QING_ZHUO_ZHEN_JIA',
        'term_cluster_id': 'QING_ZHUO_ZHEN_JIA',
        'surface_form': '四墓者，衝氣也。何以謂之雜氣？以其所藏者多，用神不一…透干會支，取其清者用之，雜而不雜也',
        'source_id': 'PZZQ-007-005',
        'chapter_id': '論用神格局高低',
        'text_layer': 'ORIGINAL',
        'object_type': 'TEN_GOD',
        'semantic_role': 'CLEAR_TURBID_REF',
        'semantic_definition': 'PZZQ 清浊表达（正文）：用「雜」不用「濁」；四墓杂气取清，雜而不雜',
        'verified_scope': 'PARTIAL',
        'scope_priority': 'CONDITIONAL',
        'excluded_scope': 'PZZQ 用「雜」表达清浊（四墓雜氣語境），與 DTS 清濁體系不同，不得合併；僅作清濁域輔助證據',
        'evidence_grade': 'A',
        'attribution': 'ORIGINAL_AUTHOR',
        'execution_eligibility': 'CONDITIONAL',
    }
]

json.dump(data, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('003B-02 补入完成：')
print('  BING_YAO/DTS: DTS-017-002（中和論注 B1，SUPPORTING_RULE_ONLY）')
print('  QING_ZHUO_ZHEN_JIA/PZZQ: PZZQ-007-005（正文 A，CONDITIONAL，雜≠濁注明）')

# 更新 checklist（补2条）
CP = r'D:\shuntian-ziping-p0\governance\patch_003b_evidence_checklist.json'
cl = json.load(io.open(CP, encoding='utf-8'))
for book, sid, doms in [('DTS', 'DTS-017-002', ['bing_yao']), ('PZZQ', 'PZZQ-007-005', ['qing_zhuo_zhen_jia'])]:
    if sid not in [it['source_id'] for it in cl[book]]:
        cl[book].append({
            'source_id': sid,
            'domains': doms,
            'chapter_verified': None,
            'text_layer_verified': None,
            'attribution_verified': None,
            'evidence_grade_verified': None,
            'usage_type_verified': 'PER_DOMAIN',
            'rule_boundary_ok': None,
            'verification_status': 'PENDING',
            'note': '003B-02 概念遗漏检查补入',
        })
json.dump(cl, io.open(CP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
total = sum(len(v) for v in cl.values())
print(f'checklist 更新：{total} 条')
