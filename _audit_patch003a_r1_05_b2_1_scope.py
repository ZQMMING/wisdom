# -*- coding: utf-8 -*-
"""R1-05 第二批 第1组：基础五行 VERIFIED_SCOPE（16字段完整schema）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def cell(domain, cluster, surface, source, chapter, layer, obj, role, definition,
         scope, priority, excluded, grade, attr, eligibility):
    return {
        'domain_id': domain, 'term_cluster_id': cluster, 'surface_form': surface,
        'source_id': source, 'chapter_id': chapter, 'text_layer': layer,
        'object_type': obj, 'semantic_role': role, 'semantic_definition': definition,
        'verified_scope': scope, 'scope_priority': priority, 'excluded_scope': excluded,
        'evidence_grade': grade, 'attribution': attr, 'execution_eligibility': eligibility,
    }

D = {}
D['wuxing_base'] = {
    'domain_id': 'WUXING_BASE',
    'term_cluster_id': 'WUXING_SHENGKE',
    'note': '基础五行：生克总纲+五行本质+五常配属',
    'books': {
        'YHZP': [
            cell('WUXING_BASE', 'SHENGKE', '金生水水生木木生火火生土土生金；金尅木木尅土土尅水水尅火火尅金',
                 'YHZP-054-001', '論五行相生相尅', 'ORIGINAL', 'FIVE_ELEMENT', 'GENERATIVE_RESTRICTIVE',
                 '五行生克总纲（相生相尅完整序列）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('WUXING_BASE', 'WUCHANG', '木曰曲直味酸主仁…火曰炎上味苦主禮',
                 'YHZP-117-001', '論性情', 'ORIGINAL', 'FIVE_ELEMENT', 'NATURE_ATTRIBUTE',
                 '五行五常性情配属（曲直/炎上/稼穡/從革/潤下）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('WUXING_BASE', 'ESSENCE', '水者太陰也，火者太陽也，木者少陽也，金者少陰也，土者陰陽老少木火金水衝氣所結',
                 'PZZQ-005-001', '論干支', 'ORIGINAL', 'FIVE_ELEMENT', 'ESSENCE_DEFINITION',
                 '五行本质定义（太陰太陽少陰少陽衝氣）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('WUXING_BASE', 'SHENGKE', '四時之運，相生而成，亦相剋而成',
                 'PZZQ-005-003', '論干支', 'ORIGINAL', 'FIVE_ELEMENT', 'GENERATIVE_RESTRICTIVE',
                 '生克互济（克者所以节而止之）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('WUXING_BASE', 'SHENGKE', '木浮水泛，土止水則生木；木旺火熾，金伐木則生火…',
                 'DTS-045-002', '六親論·反局', 'ANNOTATION', 'FIVE_ELEMENT', 'GENERATIVE_RESTRICTIVE',
                 '君赖臣生克关系（反局）', 'PARTIAL', 'SECONDARY', 'B1注層，不作A级生克总纲', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
            cell('WUXING_BASE', 'ESSENCE', '沛然而達，灼然而炎…五者氣之中，循而不息者也，故謂之行',
                 'DTS-001-001', '滴天髓序', 'LATER_COMMENTARY', 'FIVE_ELEMENT', 'ESSENCE_DEFINITION',
                 '五行定义（行=气之流行）', 'ALIGNED', 'REFERENCE', '序言層', 'C', 'LATER_COMMENTARY', 'SUPPORTING_ONLY'),
        ],
        'QTBJ': [
            cell('WUXING_BASE', 'SHENGKE', '北方陰極而生寒，寒生水…其相生也，所以相維；其相尅也，所以相制',
                 'QTBJ-001-001', '五行總論', 'ORIGINAL', 'FIVE_ELEMENT', 'GENERATIVE_RESTRICTIVE',
                 '五行总论（寒生水/热生火/风生木/燥生金/湿生土；相生相维相尅相制）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('WUXING_BASE', 'COLOR_NUMBER', '水黑火赤木青金白土黃…水一火二木三金四土五',
                 'QTBJ-001-002', '五行總論', 'ORIGINAL', 'FIVE_ELEMENT', 'COLOR_NUMBER_ATTRIBUTE',
                 '五行色数配属', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('WUXING_BASE', 'WUCHANG', '東方震巖木，龍名曰曲直，五常主仁…水屬北方名曰潤下，五常主智',
                 'SMTH-025-001', '論性情相貌', 'ORIGINAL', 'FIVE_ELEMENT', 'NATURE_ATTRIBUTE',
                 '五行五常性情配属（曲直仁/炎上礼/稼穡信/從革义/潤下智）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SFTK': [
            cell('WUXING_BASE', 'SHENGKE', '金生水。水生木。木生火。火生土。土生金。／金兌木。木尅土。土尅水。水尅火。火尅金。',
                 'SFTK-062-045', '十天干體象全編論', 'ORIGINAL', 'FIVE_ELEMENT', 'GENERATIVE_RESTRICTIVE',
                 '五行生克总纲', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# 追加到 r1_05_verified_scope.json
with open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8') as f:
    existing = json.load(f)
existing['wuxing_base'] = D['wuxing_base']
with open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print('基础五行已落档（16字段schema）')
for b, cells in D['wuxing_base']['books'].items():
    for c in cells:
        print(f"  {b}: {c['source_id']} [{c['chapter_id']}] {c['text_layer']}/{c['evidence_grade']} {c['verified_scope']} → {c['execution_eligibility']}")
