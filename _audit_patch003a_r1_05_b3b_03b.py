# -*- coding: utf-8 -*-
"""003B-03 补 relation_type：旺衰/令地根/势/月令 5 领域（OBJECT+SOURCE+RELATION+CLASSICAL_SCOPE 四维）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
data = json.load(io.open(P, encoding='utf-8'))

# source → relation_type（按领域语境判断）
RELATION = {
    # 旺强衰：旺/强是「旺于某时/强于某因」的状态关系
    'domain_01_wang_qiang_shuai': {
        'YHZP-138-001': 'PROSPEROUS_AT / STRONG_AT',
        'YHZP-069-001': 'PROSPEROUS_AT',
        'PZZQ-005-002': 'PROSPEROUS_AT',
        'DTS-016-001': 'PROSPEROUS_AT（衰旺真機）',
        'DTS-016-002': 'PROSPEROUS_CONTAINED（旺中有衰）',
        'DTS-001-001': 'PROSPEROUS_AT / SUPPORTED_AT（當王而旺得輔而強）',
        'SFTK-120-004': 'PROSPEROUS_AT（月提得令）',
        'SFTK-129-038': 'PROSPEROUS_BLOCKED（失令持勢不作旺）',
    },
    # 令时地根：得令/得时/通根 都是对象↔月令/地支的关系
    'domain_02_ling_shi_di_gen': {
        'YHZP-056-001': 'GET_ORDER / RULING_SCHEDULE',
        'YHZP-030-001': 'GET_ORDER',
        'YHZP-138-001': 'GET_TIME（得時）',
        'PZZQ-005-007': 'GET_ORDER',
        'PZZQ-005-002': 'GET_ORDER（不逢祿旺遇休囚）',
        'DTS-015-003': 'RULING_ELEMENT（人元用事）',
        'DTS-015-004': 'RULING_SCHEDULE（寅月用事）',
        'DTS-015-006': 'RULING_SCHEDULE（子時用事）',
        'QTBJ-018-001': 'SEASONAL_CONDITION',
        'SFTK-129-038': 'GET_ORDER_BLOCKED（失令持勢）',
        'SFTK-120-004': 'GET_ORDER（月提得令）',
        'SFTK-062-035': 'GET_ORDER',
    },
    # 势：势向关系
    'domain_03_shi': {
        'DTS-008-003': 'TREND_TO（從氣不從勢）',
        'DTS-008-022': 'TREND_BURST（勢沖奔）',
        'SMTH-035-001': 'TREND_GROUP',
        'SFTK-129-038': 'TREND_HOLD（持勢）',
    },
    # 月令：月令主事关系
    'domain_04_yue_ling': {
        'YHZP-063-001': 'RULE_MONTH',
        'YHZP-056-001': 'RULE_MONTH / RULING_SCHEDULE',
        'PZZQ-005-007': 'RULE_MONTH（專求月令）',
        'DTS-015-003': 'RULE_MONTH / RULING_ELEMENT',
        'SFTK-120-004': 'RULE_MONTH（月提得令）',
        'SFTK-008-001': 'RULE_MONTH（先看月令）',
    },
    # 根气：通根关系（对象化：日主/官/财/杀/印）
    'gen_qi': {
        'YHZP-123-003': 'ROOTED_IN（無根）',
        'YHZP-138-001': 'ROOTED_IN（無根得時）',
        'PZZQ-007-021': 'ROOTED_IN（財根深）',
        'DTS-010-003': 'ROOTED_IN / COVERED_SUPPORTED（天覆地載）',
        'DTS-008-021': 'ROOTED_IN（通根）',
        'QTBJ-011-001': 'ROOTED_IN（無根）',
        'SMTH-023-003': 'ROOTED_IN（無根破敗）',
        'SFTK-020-014': 'ROOTED_IN（無根棄命從財）',
    },
}

added = 0
for dk, relmap in RELATION.items():
    dom = data.get(dk)
    if not dom:
        print(f'!! {dk} 不存在')
        continue
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            sid = c.get('source_id')
            if sid and sid in relmap:
                c['relation_type'] = relmap[sid]
                added += 1

json.dump(data, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'relation_type 已补：{added} cell（5 领域）')
print('验证四维完整性：OBJECT + SOURCE + RELATION + CLASSICAL_SCOPE')
missing = 0
for dk in RELATION:
    for b, cells in data[dk].get('books', {}).items():
        for c in cells:
            if not c.get('relation_type'):
                missing += 1
                print(f'  ⚠️ {dk}/{b}/{c.get("source_id")} 缺 relation_type')
print(f'缺失：{missing}')
