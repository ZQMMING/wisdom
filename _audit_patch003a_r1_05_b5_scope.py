# -*- coding: utf-8 -*-
"""R1-05 第五批：干支组合 / 六亲 / 神煞 / 命例验证 VERIFIED_SCOPE（16字段）"""
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

new_domains = {}

# ============ 干支组合 ============
new_domains['ganzhi_zuhe'] = {
    'domain_id': 'GANZHI_ZUHE',
    'term_cluster_id': 'GANZHI_ZUHE',
    'note': '干支组合：刑冲会合/干支配合/四柱组合断语',
    'books': {
        'YHZP': [
            cell('GANZHI_ZUHE', 'COMBO', '造化先須看日主，後把提綱看次第。四柱專論其財官', 'YHZP-131-001', '寸金搜髓論', 'ORIGINAL',
                 'FOUR_PILLARS', 'COMBO_RULE', '干支组合断语（看日主→提纲→财官）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('GANZHI_ZUHE', 'XING_CHONG_HUI', '刑者，三刑也，子卯巳申之類是也。衝者，六衝也，子午卯酉之類是也。會者，三會也，申子辰、巳酉丑之類是也',
                 'PZZQ-005-006', '論干支', 'ORIGINAL', 'BRANCH', 'XING_CHONG_HUI_DEFINITION',
                 '刑冲会合定义正文本体', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('GANZHI_ZUHE', 'COMBO', '天干地支相為配合，要詳細推其進退之機', 'DTS-007-002', '通天論·配合', 'ANNOTATION',
                 'STEM_BRANCH', 'COMBO_MECHANISM', '干支配合（B1）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'QTBJ': [
            cell('GANZHI_ZUHE', 'COMBO', '或支成木局…又有庚透富貴雙全', 'QTBJ-048-002', '四月戊土', 'ORIGINAL',
                 'BRANCH', 'COMBO_CONDITION', '地支成局组合（条件断语）', 'ALIGNED', 'PRIMARY', '綁定具體條件', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('GANZHI_ZUHE', 'COMBO', '地支至切，黨盛為強', 'SMTH-030-002', '論日主強弱（黨盛）', 'ORIGINAL',
                 'BRANCH', 'COMBO_STRENGTH', '地支党盛为强（地支组合）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SFTK': [
            cell('GANZHI_ZUHE', 'COMBO', '財星入庫逢沖破富有千倉官星正氣遇刑沖貴而不久', 'SFTK-119-002', '崖泉男命賦', 'ORIGINAL',
                 'FOUR_PILLARS', 'COMBO_RULE', '干支组合断语（入墓冲/刑冲）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 六亲 ============
new_domains['liu_qin'] = {
    'domain_id': 'LIU_QIN',
    'term_cluster_id': 'LIU_QIN_TEN_GOD',
    'note': '六亲：十神配六亲（YHZP 正文本体/PZZQ 用神配/DTS 注层）',
    'books': {
        'YHZP': [
            cell('LIU_QIN', 'TEN_GOD', '正印正母，偏印偏母及祖父也；偏財是父，乃母之夫星也…正財為妻…七殺是男，正官是女',
                 'YHZP-102-001', '六親總論', 'ORIGINAL', 'TEN_GOD', 'SIX_RELATION_DEFINITION',
                 '六亲配属正文本体（印母/财父/官子女）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('LIU_QIN', 'TEN_GOD', '其由用神配之者，則正印為母，身所自出…若偏財受我剋制，何反為父',
                 'PZZQ-007-012', '論用神格局高低', 'ORIGINAL', 'TEN_GOD', 'SIX_RELATION_DEFINITION',
                 '六亲配属（用神配）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('LIU_QIN', 'TEN_GOD', '子平之法以才為父，以印為母，而斷其吉凶十有九驗', 'DTS-031-002', '六親論·父母', 'ANNOTATION',
                 'TEN_GOD', 'SIX_RELATION_REF', '六亲（才父印母，B1）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
            cell('LIU_QIN', 'PATTERN', '君賴臣生理最微，兒能生母洩天機。母慈滅子關頭異，夫健何為又怕妻', 'DTS-045-001', '六親論·反局', 'ORIGINAL',
                 'PATTERN', 'SIX_RELATION_PATTERN', '反局六亲（君赖臣/母慈灭子）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'QTBJ': [
            cell('LIU_QIN', 'TEN_GOD', '印綬被傷母年早喪。財星得祿。父命長春', 'QTBJ-111-002', '增補月談賦', 'ORIGINAL',
                 'TEN_GOD', 'SIX_RELATION_RULE', '六亲断语（印母财父）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('LIU_QIN', 'TEN_GOD', '或問陰陽何所配合為夫婦。而成六親。答云。如甲以乙為妹。配與庚金為妻', 'SMTH-047-001', '論六親', 'ORIGINAL',
                 'TEN_GOD', 'SIX_RELATION_DEFINITION', '六亲配属（阴阳配合）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SFTK': [
            cell('LIU_QIN', 'TEN_GOD', '年上財官主祖宗之榮顯月上官殺主兄弟之凋零', 'SFTK-007-002', '六親說', 'ORIGINAL',
                 'FOUR_PILLARS', 'SIX_RELATION_RULE', '六亲宫位（年祖月父母日夫妻时子女）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 神煞 ============
new_domains['shen_sha'] = {
    'domain_id': 'SHEN_SHA',
    'term_cluster_id': 'SHEN_SHA',
    'note': '神煞：六部原文存在但 PATCH-002 裁决 EXCLUDED（混杂/后世添加过多），仅扫描分层不入 RULE',
    'books': {
        'YHZP': [
            cell('SHEN_SHA', 'SHEN_SHA', '（神煞分散于女命/子息等章，桃花/羊刃等）', 'YHZP-108-001', '論子息', 'ORIGINAL',
                 'SHEN_SHA', 'REF', '神煞语境（杀临羊刃/沐浴桃花）', 'EXCLUDED', '—', '神煞域 EXCLUDED（PATCH-002）', 'A', 'ORIGINAL_AUTHOR', 'EXCLUDED_FROM_RULE'),
        ],
        'PZZQ': [
            cell('SHEN_SHA', 'SHEN_SHA', '八字格局，專以月令配四柱，至於星辰好歹，既不能為生剋之用，又何以操成敗之權', 'PZZQ-007-010', '論用神格局高低', 'ORIGINAL',
                 'SHEN_SHA', 'REJECT_REF', '格局优先，星辰（神煞）不能操成败权', 'EXCLUDED', '—', '神煞域 EXCLUDED', 'A', 'ORIGINAL_AUTHOR', 'EXCLUDED_FROM_RULE'),
        ],
        'DTS': [
            cell('SHEN_SHA', 'SHEN_SHA', '三奇二德虛好語，咸池驛馬半推詳', 'DTS-034-001', '六親論·女命論', 'ORIGINAL',
                 'SHEN_SHA', 'REF', '神煞（女命正文提及但未成体系）', 'EXCLUDED', '—', '神煞域 EXCLUDED', 'A', 'ORIGINAL_AUTHOR', 'EXCLUDED_FROM_RULE'),
        ],
        'QTBJ': [
            cell('SHEN_SHA', 'SHEN_SHA', '（QTBJ 神煞极少，仅散见）', 'QTBJ-001-002', '五行總論', 'ORIGINAL',
                 'SHEN_SHA', 'REF', '—', 'EXCLUDED', '—', '神煞域 EXCLUDED', 'A', 'ORIGINAL_AUTHOR', 'EXCLUDED_FROM_RULE'),
        ],
        'SMTH': [
            cell('SHEN_SHA', 'SHEN_SHA', '（SMTH 神煞资料库最大：321条）', 'SMTH-020-023', '寅申已亥四宮互換神煞', 'ORIGINAL',
                 'SHEN_SHA', 'REF', '神煞大库（资料汇编性质）', 'EXCLUDED', '—', '神煞域 EXCLUDED（PATCH-002）', 'A', 'ORIGINAL_AUTHOR', 'EXCLUDED_FROM_RULE'),
        ],
        'SFTK': [
            cell('SHEN_SHA', 'SHEN_SHA', '（SFTK 神煞185条：吉神类/日贵格等）', 'SFTK-064-030', '吉神類', 'ORIGINAL',
                 'SHEN_SHA', 'REF', '神煞（华盖/将星等）', 'EXCLUDED', '—', '神煞域 EXCLUDED', 'A', 'ORIGINAL_AUTHOR', 'EXCLUDED_FROM_RULE'),
        ],
    },
}

# ============ 命例验证 ============
new_domains['ming_li'] = {
    'domain_id': 'MING_LI',
    'term_cluster_id': 'MING_LI_CASE',
    'note': '命例验证：evidence_grade 上限 REFERENCE（Human 约束），必须与原文纲领绑定',
    'books': {
        'YHZP': [
            cell('MING_LI', 'CASE', '假如己未、壬申、戊子、庚申，此乃斷左丞相之命', 'YHZP-079-010', '正氣官星（繼善篇注）', 'ANNOTATION',
                 'FOUR_PILLARS', 'CASE_REF', '命例（丞相）', 'PARTIAL', 'REFERENCE', '命例上限 REFERENCE', 'B', 'ORIGINAL_ANNOTATION', 'REFERENCE_ONLY'),
        ],
        'PZZQ': [
            cell('MING_LI', 'CASE', '如丁未、癸卯、癸亥、癸丑，梁丞相之命是也；己未、壬申、戊子、庚申，謝閣老之命是也', 'PZZQ-007-025', '論用神格局高低', 'ORIGINAL',
                 'FOUR_PILLARS', 'CASE_REF', '命例（梁丞相/谢阁老）', 'PARTIAL', 'REFERENCE', '命例上限 REFERENCE，须与纲领绑定', 'A', 'ORIGINAL_AUTHOR', 'REFERENCE_ONLY'),
        ],
        'DTS': [
            cell('MING_LI', 'CASE', '（DTS 命例极少，反局等以理论为主）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
        ],
        'QTBJ': [
            cell('MING_LI', 'CASE', '甲辰甲戌甲辰甲戌身伴君王富貴壽考此爲天元一氣', 'QTBJ-010-002', '九月甲木', 'ORIGINAL',
                 'FOUR_PILLARS', 'CASE_REF', '命例（天元一气）', 'PARTIAL', 'REFERENCE', '命例上限 REFERENCE', 'A', 'ORIGINAL_AUTHOR', 'REFERENCE_ONLY'),
        ],
        'SMTH': [
            cell('MING_LI', 'CASE', '（SMTH 命例极大量：日时断语中大量命例）', 'SMTH-066-013', '六乙日丙子時斷', 'ORIGINAL',
                 'FOUR_PILLARS', 'CASE_REF', '日时命例', 'PARTIAL', 'REFERENCE', '命例上限 REFERENCE', 'A', 'ORIGINAL_AUTHOR', 'REFERENCE_ONLY'),
        ],
        'SFTK': [
            cell('MING_LI', 'CASE', '壬申丙午乙亥庚午 趙丞相之造', 'SFTK-023-047', '陽刃格 附比刦建祿格', 'ORIGINAL',
                 'FOUR_PILLARS', 'CASE_REF', '命例（赵丞相）', 'PARTIAL', 'REFERENCE', '命例上限 REFERENCE', 'A', 'ORIGINAL_AUTHOR', 'REFERENCE_ONLY'),
        ],
    },
}

with open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8') as f:
    existing = json.load(f)
existing.update(new_domains)
with open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', 'w', encoding='utf-8') as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

for dom, v in new_domains.items():
    print(f'\n=== {v["domain_id"]} ===')
    for b, cells in v['books'].items():
        for c in cells:
            sid = c.get('source_id') or '—'
            print(f'  {b}: {sid} {c.get("text_layer") or "—"}/{c.get("evidence_grade") or "—"} {c["verified_scope"]} → {c["execution_eligibility"]}')
