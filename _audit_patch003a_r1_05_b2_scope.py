# -*- coding: utf-8 -*-
"""R1-05 第二批 第1组：十神 / 生旺休囚 / 根气 / 党众 VERIFIED_SCOPE（16字段）"""
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

# ============ 十神 ============
new_domains['shishen'] = {
    'domain_id': 'SHISHEN',
    'term_cluster_id': 'SHISHEN_SHISHEN',
    'note': '十神：八格定名+十神六亲配属+顺逆用',
    'books': {
        'YHZP': [
            cell('SHISHEN', 'SHISHEN', '日主橫看十神定例（傷官/偏財/正財…）', 'YHZP-032-006', '日主橫看十神定例', 'ORIGINAL',
                 'TEN_GOD', 'DEFINITION', '十神定例（日主×十神对照）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('SHISHEN', 'SHISHEN', '正印正母…七殺是男，正官是女', 'YHZP-102-001', '六親總論', 'ORIGINAL',
                 'TEN_GOD', 'SIX_RELATION_ATTRIBUTE', '十神六亲配属（印母/财妻/官杀子女）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('SHISHEN', 'SHISHEN', '格局分為財官印食…煞傷刃劫逆用', 'PZZQ-005-007', '論干支', 'ORIGINAL',
                 'TEN_GOD', 'SHUN_NI_USE', '十神顺逆用（财官印食顺/煞伤刃劫逆）', 'ALIGNED', 'PRIMARY', '不得擴展為所有格局判斷', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('SHISHEN', 'SHISHEN', '八格：傷官、食神、正財、偏財、正官、偏官、正印、偏印', 'DTS-013-001', '通天論·八格論', 'ORIGINAL',
                 'TEN_GOD', 'DEFINITION', '八格定名（十神八类）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('SHISHEN', 'SHISHEN', '財官印綬分偏正，兼論食神八格定', 'DTS-013-002', '通天論·八格論', 'ORIGINAL',
                 'TEN_GOD', 'DEFINITION', '十神偏正分定', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'QTBJ': [
            cell('SHISHEN', 'SHISHEN', '印綬若逢官正官逢定許入朝班…', 'QTBJ-111-003', '增補月談賦', 'ORIGINAL',
                 'TEN_GOD', 'CONDITIONAL_RULE', '十神条件断语（印逢官/官逢印…）', 'ALIGNED', 'PRIMARY', '斷語須綁定具體條件', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('SHISHEN', 'SHISHEN', '如甲以乙為妹，配與庚金為妻…', 'SMTH-047-001', '論六親', 'ORIGINAL',
                 'TEN_GOD', 'SIX_RELATION_ATTRIBUTE', '十神六亲配属（阴阳配合成六亲）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SFTK': [
            cell('SHISHEN', 'SHISHEN', '丙戊庚壬甲爲傷官小人…辛癸乙丁己爲偏官七殺…', 'SFTK-069-003', '地支造化之圖', 'ORIGINAL',
                 'TEN_GOD', 'DEFINITION', '十神造化图（日主×十神对照）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('SHISHEN', 'SHISHEN', '丁日寅提正印。卯上偏印格局真…', 'SFTK-074-001', '丁日定格', 'ORIGINAL',
                 'TEN_GOD', 'CONDITIONAL_RULE', '十干逐月定格（丁日十二支格局）', 'ALIGNED', 'PRIMARY', '逐月條件綁定', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 生旺休囚 ============
new_domains['shengwang_xiuqiu'] = {
    'domain_id': 'SHENGWANG_XIUQIU',
    'term_cluster_id': 'SHENGWANG_SHISI',
    'note': '生旺休囚：十二长生宫+旺相休囚死+阳顺阴逆',
    'books': {
        'YHZP': [
            cell('SHENGWANG_XIUQIU', 'SHIER_CHANGSHENG', '甲木生亥，沐浴在子…乙木生午，沐浴在巳…', 'YHZP-015-002', '論天干生旺死絕', 'ORIGINAL',
                 'DAY_STEM', 'SHENGWANG_SCHEDULE', '十二长生逐干（阳顺阴逆）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('SHENGWANG_XIUQIU', 'SHIER_CHANGSHENG', '長生、沐浴、冠帶、臨官、帝旺、衰、病、死、墓庫、絕、胎、養', 'YHZP-016-001', '五行發用定例', 'ORIGINAL',
                 'FIVE_ELEMENT', 'DEFINITION', '十二宫定名', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('SHENGWANG_XIUQIU', 'SHIER_CHANGSHENG', '陽主聚以進為進，故主順；陰主散以退為進，故主逆', 'PZZQ-005-002', '論干支', 'ORIGINAL',
                 'DAY_STEM', 'SHENGWANG_SCHEDULE', '阳顺阴逆原则', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('SHENGWANG_XIUQIU', 'SHENGWANG', '如戊寅、壬申、丙寅、己酉皆長生日主', 'DTS-010-013', '通天論·干支論', 'ANNOTATION',
                 'DAY_STEM', 'SHENGWANG_REF', '长生日主（B1）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'QTBJ': [
            cell('SHENGWANG_XIUQIU', 'SHENGWANG', '須忌死絕之地只宜生旺之方', 'QTBJ-002-003', '論木', 'ORIGINAL',
                 'FIVE_ELEMENT', 'SHENGWANG_RULE', '生旺死绝方位宜忌', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('SHENGWANG_XIUQIU', 'SHENGWANG', '生旺則長壽，死絕則夭折；譬如根深者蔭固', 'SMTH-028-001', '論壽夭', 'ORIGINAL',
                 'FIVE_ELEMENT', 'SHENGWANG_RULE', '生旺死绝与寿夭', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SFTK': [
            cell('SHENGWANG_XIUQIU', 'SHIER_CHANGSHENG', '長生 沐浴。冠帶。臨官。帝旺。衰。病。死。墓。絕。胎。養。', 'SFTK-062-050', '十天干體象全編論', 'ORIGINAL',
                 'FIVE_ELEMENT', 'DEFINITION', '十二宫定名', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('SHENGWANG_XIUQIU', 'SHENGWANG', '凡傷官行旺相吉死墓皆凶，陽順陰逆以用神而推', 'SFTK-020-041', '月支正財格 附棄命從財格', 'ORIGINAL',
                 'TEN_GOD', 'SHENGWANG_RULE', '伤官行运旺相吉死墓凶', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 根气 ============
new_domains['gen_qi'] = {
    'domain_id': 'GEN_QI',
    'term_cluster_id': 'GEN_QI_ROOT',
    'note': '根气：有根/无根/根深/根轻/天覆地载',
    'books': {
        'YHZP': [
            cell('GEN_QI', 'ROOT', '從象者，如甲乙日主無根也', 'YHZP-123-003', '神趣八法（有類屬從化返照鬼伏）', 'ORIGINAL',
                 'DAY_STEM', 'ROOT_STATE', '从格无根条件', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('GEN_QI', 'ROOT', '四柱無根，得時為旺', 'YHZP-138-001', '子機賦', 'ORIGINAL',
                 'DAY_STEM', 'ROOT_STATE', '无根得时为旺（根≠旺）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('GEN_QI', 'ROOT', '財喜根深，不宜太露…財要有根', 'PZZQ-007-021', '論用神格局高低', 'ORIGINAL',
                 'TEN_GOD', 'ROOT_STATE', '财星根深（根对象=财星）', 'ALIGNED', 'PRIMARY', '根對象化（可為財/官/日主）', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('GEN_QI', 'ROOT', '不論有根無根，俱要天覆地載', 'DTS-010-003', '通天論·干支論', 'ORIGINAL',
                 'STEM_BRANCH', 'ROOT_STATE', '有根无根皆需天覆地载（根气正文本体）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('GEN_QI', 'ROOT', '通根透癸，沖天奔地', 'DTS-008-021', '通天論·天干', 'ORIGINAL',
                 'DAY_STEM', 'ROOT_STATE', '壬水通根（根为结构事实）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'QTBJ': [
            cell('GEN_QI', 'ROOT', '庚金無根平常人也…或甲多制戊庚金無根', 'QTBJ-011-001', '十月甲木', 'ORIGINAL',
                 'TEN_GOD', 'ROOT_STATE', '庚金无根断语（条件性）', 'ALIGNED', 'PRIMARY', '綁定具體日干月令', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('GEN_QI', 'ROOT', '就戊午無根之況已為破敗', 'SMTH-023-003', '戰關伏降刑衝破合', 'ORIGINAL',
                 'DAY_STEM', 'ROOT_STATE', '无根破败断语', 'PARTIAL', 'SECONDARY', '日時斷語為條件變量', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'SFTK': [
            cell('GEN_QI', 'ROOT', '三合財多略無根氣則為棄命就財格', 'SFTK-020-014', '月支正財格 附棄命從財格', 'ORIGINAL',
                 'TEN_GOD', 'ROOT_STATE', '财星无根→从财', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 党众 ============
new_domains['dang_zhong'] = {
    'domain_id': 'DANG_ZHONG',
    'term_cluster_id': 'DANG_ZHONG_GROUP',
    'note': '党众：党多/党盛/偏党/帮身',
    'books': {
        'YHZP': [
            cell('DANG_ZHONG', 'GROUP', '中和之氣爲福厚，偏黨之氣爲福薄', 'YHZP-076-075', '喜忌篇', 'ANNOTATION',
                 'QI', 'GROUP_STATE', '偏党福薄（中和vs偏党）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'PZZQ': [
            cell('DANG_ZHONG', 'GROUP', '煞旺食強而身健…煞以攻身似非美物而大貴之格多存七煞', 'PZZQ-007-027', '論用神格局高低', 'ORIGINAL',
                 'TEN_GOD', 'GROUP_STATE', '煞旺身健（党众为结构条件）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('DANG_ZHONG', 'GROUP', '如子運午年…午之黨多，干頭遇丙戊甲字者必凶', 'DTS-057-001', '六親論·何爲衝', 'ORIGINAL',
                 'BRANCH', 'GROUP_STATE', '党众正文（午之黨多→干头助子必凶）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('DANG_ZHONG', 'GROUP', '真神得令，假神得局而黨多', 'DTS-023-004', '通天論·真假論', 'ANNOTATION',
                 'TEN_GOD', 'GROUP_STATE', '假神得局而党多（真假判据）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'QTBJ': [
            cell('DANG_ZHONG', 'GROUP', '或支成木局…又有庚透富貴雙全', 'QTBJ-048-002', '四月戊土', 'ORIGINAL',
                 'BRANCH', 'GROUP_STATE', '地支成局（党众之会局）', 'ALIGNED', 'PRIMARY', '綁定具體條件', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('DANG_ZHONG', 'GROUP', '亡神却煞不宜全。莫敵得黨却生年', 'SMTH-020-014', '寅申已亥四宮互換神煞', 'ORIGINAL',
                 'SHEN_SHA', 'GROUP_STATE', '神煞得党（神煞域）', 'EXCLUDED', '—', '神煞域 EXCLUDED（PATCH-002）', 'A', 'ORIGINAL_AUTHOR', 'EXCLUDED_FROM_RULE'),
        ],
        'SFTK': [
            cell('DANG_ZHONG', 'GROUP', '年月日時俱有土旺水強進氣亦不能勝衆土也', 'SFTK-011-054', '正官格', 'ORIGINAL',
                 'FIVE_ELEMENT', 'GROUP_STATE', '众土党众（病药语境）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
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
            print(f'  {b}: {c["source_id"]} {c["text_layer"]}/{c["evidence_grade"]} {c["verified_scope"]} → {c["execution_eligibility"]}')
