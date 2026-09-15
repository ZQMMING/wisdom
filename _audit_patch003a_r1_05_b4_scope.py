# -*- coding: utf-8 -*-
"""R1-05 第四批：格局成败 / 相神 / 顺逆 VERIFIED_SCOPE（16字段）"""
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

# ============ 格局成败 ============
new_domains['geju_chengbai'] = {
    'domain_id': 'GEJU_CHENGBAI',
    'term_cluster_id': 'GEJU_CHENGBAI',
    'note': '格局成败：成格/败格/破格/因成得败/因败得成',
    'books': {
        'YHZP': [
            cell('GEJU_CHENGBAI', 'BREAK', '如逢甲乙木生旺運，化不成反爲不吉。己字中露出二甲字，謂之爭合；有一個乙字露出，謂之妒合，爲破格不成',
                 'YHZP-123-004', '神趣八法（有類屬從化返照鬼伏）', 'ORIGINAL', 'PATTERN', 'BREAK_CONDITION',
                 '化格破格条件（争合妒合）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('GEJU_CHENGBAI', 'SUCCESS_FAIL', '用神專尋月令，以四柱配之，必有成敗。何謂成？如官逢財印，又無刑衝破害，官格成也…何謂敗？官逢傷尅刑衝，官格敗也',
                 'PZZQ-005-008', '論干支', 'ORIGINAL', 'PATTERN', 'SUCCESS_FAIL_DEFINITION',
                 '格局成败正文本体（成格/败格条件）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('GEJU_CHENGBAI', 'SUCCESS_FAIL', '八字之中，變化不一，遂分成敗；而成敗之中，又變化不測，遂有因成得敗、因敗得成之奇',
                 'PZZQ-007-002', '論用神格局高低', 'ORIGINAL', 'PATTERN', 'TRANSITION',
                 '因成得败/因败得成（成败互转）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('GEJU_CHENGBAI', 'CLEAR_TURBID', '雖然成敗不一，不過悠忽了此生耳', 'DTS-022-004', '通天論·清濁論', 'ANNOTATION',
                 'QI', 'TREND_REF', '成败（清浊注语境）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'QTBJ': [
            cell('GEJU_CHENGBAI', 'BREAK', '得一丙透無癸出破格不特科甲定主名臣顯官', 'QTBJ-025-001', '十二月乙木', 'ORIGINAL',
                 'PATTERN', 'BREAK_CONDITION', '破格条件（癸出破格）', 'ALIGNED', 'PRIMARY', '綁定具體日干月令', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('GEJU_CHENGBAI', 'SUCCESS_FAIL', '謀望有成有敗，幾度遇凶則吉', 'SMTH-071-017', '六乙日辛巳時斷', 'ORIGINAL',
                 'PATTERN', 'SUCCESS_FAIL_REF', '成败（日时断语）', 'PARTIAL', 'REFERENCE', '日時斷語為條件變量', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'SFTK': [
            cell('GEJU_CHENGBAI', 'ENTRY', '凡看八字先明從化為本從化不成方論財官財官無取方論格局', 'SFTK-082-001', '十干從化定訣', 'ORIGINAL',
                 'PATTERN', 'ENTRY_ORDER', '格局判定入口（从化→财官→格局）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('GEJU_CHENGBAI', 'BREAK', '八字中有二甲字謂之爭合有一乙字謂之妬合皆為破格', 'SFTK-058-013', '神趣八法類象', 'ORIGINAL',
                 'PATTERN', 'BREAK_CONDITION', '化格破格（争合妒合）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 相神 ============
new_domains['xiang_shen'] = {
    'domain_id': 'XIANG_SHEN',
    'term_cluster_id': 'XIANG_SHEN_ASSIST',
    'note': '相神：辅用神者（PZZQ 独有核心概念，DTS 0 命中）',
    'books': {
        'YHZP': [
            cell('XIANG_SHEN', 'ASSIST', '（无「相神」原文，以格局/用神语境为主）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
        ],
        'PZZQ': [
            cell('XIANG_SHEN', 'ASSIST', '月令既得用神，則別位亦必有相，若君之有相，輔我用神者是也。如官逢財生，則官為用、財為相…凡全局之格，賴此一字而成者，均謂之相也',
                 'PZZQ-007-004', '論用神格局高低', 'ORIGINAL', 'TEN_GOD', 'ASSIST_DEFINITION',
                 '相神定义正文本体（辅用神者）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('XIANG_SHEN', 'ASSIST', '（DTS 无「相神」概念，0 命中）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
        ],
        'QTBJ': [
            cell('XIANG_SHEN', 'ASSIST', '（无「相神」术语；「用神」体系为丁甲丙取用）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
        ],
        'SMTH': [
            cell('XIANG_SHEN', 'ASSIST', '（无「相神」术语，0 命中）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
        ],
        'SFTK': [
            cell('XIANG_SHEN', 'ASSIST', '此是有病之命得藥救之亦多富貴', 'SFTK-020-033', '月支正財格 附棄命從財格', 'ORIGINAL',
                 'TEN_GOD', 'MEDICINE_REF', '病药救应（近相神功能，但术语不同）', 'PARTIAL', 'REFERENCE', '病药域术语，勿与相神混用', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
    },
}

# ============ 顺逆 ============
new_domains['shun_ni'] = {
    'domain_id': 'SHUN_NI',
    'term_cluster_id': 'SHUN_NI_USE',
    'note': '顺逆：顺用逆用（PZZQ 格局用）/ 顺其气势（DTS）/ 阳顺阴逆（长生）',
    'books': {
        'YHZP': [
            cell('SHUN_NI', 'LONG_SHENG', '陽生陰死，陽死陰生，循環無窮。如甲木生亥、乙木生午，順逆之別也', 'YHZP-015-003', '論天干生旺死絕', 'ANNOTATION',
                 'DAY_STEM', 'SHUN_NI_ORDER', '阳顺阴逆（长生）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'PZZQ': [
            cell('SHUN_NI', 'PATTERN_USE', '此用神之善而順用之者也；煞傷刃劫，此用神之不善而逆用之者也。當順而順，當逆而逆，配合得宜，皆為貴格',
                 'PZZQ-005-007', '論干支', 'ORIGINAL', 'TEN_GOD', 'SHUN_NI_DEFINITION',
                 '顺逆用正文本体（财官印食顺/煞伤刃劫逆）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('SHUN_NI', 'QI_TREND', '順逆不齊也，不可逆者，順其氣勢而已矣', 'DTS-025-001', '通天論·順逆', 'ORIGINAL',
                 'QI', 'SHUN_NI_TREND', '顺逆正文（顺其气势）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('SHUN_NI', 'YIN_YANG', '陰陽順逆之說，洛書流行之用，其理信有之也，其法不可執一', 'DTS-010-001', '通天論·干支論', 'ORIGINAL',
                 'DAY_STEM', 'SHUN_NI_ORDER', '阳顺阴逆（不可执一）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'QTBJ': [
            cell('SHUN_NI', '—', '（无「順逆」术语，0 命中；以用神取用为主）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
        ],
        'SMTH': [
            cell('SHUN_NI', 'YIN_YANG', '陰陽順逆要推詳。引旺有倚文學貴', 'SMTH-002-026', '論太極貴（一名科名星）', 'ORIGINAL',
                 'DAY_STEM', 'SHUN_NI_REF', '阴阳顺逆（神煞语境）', 'PARTIAL', 'REFERENCE', '神煞域', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'SFTK': [
            cell('SHUN_NI', 'LUCK', '順運西南應發達…逆行大運宜東', 'SFTK-061-033', '五星論', 'ORIGINAL',
                 'LUCK', 'SHUN_NI_LUCK', '顺逆运（大运顺逆行）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
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
