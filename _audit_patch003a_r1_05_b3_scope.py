# -*- coding: utf-8 -*-
"""R1-05 第三批：生扶克泄耗 / 气势 / 调候 / 通关 VERIFIED_SCOPE（16字段）"""
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

# ============ 生扶克泄耗 ============
new_domains['shengfu_kexie'] = {
    'domain_id': 'SHENGFU_KEXIE',
    'term_cluster_id': 'SHENGFU_KEXIE_WUXING',
    'note': '生扶克泄耗：五行生克五类关系（生我/我生/克我/我克/比和）',
    'books': {
        'YHZP': [
            cell('SHENGFU_KEXIE', 'FIVE_RELATION', '生我者爲父母，我生者爲子孫，尅我者爲官鬼，我尅者爲妻財，比和者爲兄弟',
                 'YHZP-054-002', '論五行相生相尅', 'ANNOTATION', 'FIVE_ELEMENT', 'FIVE_RELATION_DEFINITION',
                 '五行五类关系定名（父母/子孙/官鬼/妻财/兄弟）', 'ALIGNED', 'PRIMARY', '注層B1', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
            cell('SHENGFU_KEXIE', 'SHISHEN', '食神者，生我財神之謂也…名盜氣', 'YHZP-086-001', '論食神', 'ORIGINAL',
                 'TEN_GOD', 'DEFINITION', '食神定义（盗气）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('SHENGFU_KEXIE', 'SHUN_NI', '財喜食以相生、生官以護財…煞傷刃劫逆用', 'PZZQ-005-007', '論干支', 'ORIGINAL',
                 'TEN_GOD', 'SHUN_NI_USE', '生扶克泄顺逆用', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('SHENGFU_KEXIE', 'RESCUE', '官輕要助官；煞重身輕又須印比；無官只論才', 'DTS-030-002', '六親論·子女', 'ANNOTATION',
                 'TEN_GOD', 'RESCUE_RELATION', '生扶救应（助官/印比帮身）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'QTBJ': [
            cell('SHENGFU_KEXIE', 'DRAIN', '亥宮壬水無力回克洩氣故也仍用申宮長生之水', 'QTBJ-030-001', '四月丙火', 'ORIGINAL',
                 'TEN_GOD', 'DRAIN_STATE', '泄气/回克条件断语', 'ALIGNED', 'PRIMARY', '綁定具體日干月令', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('SHENGFU_KEXIE', 'FIVE_RELATION', '我生他。一名提孩。劫煞歲去生煞。猶母生子', 'SMTH-006-012', '劫煞（一十六般，一名大煞）', 'ORIGINAL',
                 'FIVE_ELEMENT', 'FIVE_RELATION_REF', '我生关系（神煞语境）', 'PARTIAL', 'SECONDARY', '神煞域', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'SFTK': [
            cell('SHENGFU_KEXIE', 'DRAIN', '午未月傷官泄氣太重再行寅午戌火運泄木精英太甚安得不死乎', 'SFTK-020-034', '月支正財格 附棄命從財格', 'ORIGINAL',
                 'TEN_GOD', 'DRAIN_STATE', '泄气太重之病（病药语境）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 气势 ============
new_domains['qi_shi'] = {
    'domain_id': 'QI_SHI',
    'term_cluster_id': 'QI_SHI_TREND',
    'note': '气势：气/势/精神/气势攸长（DTS 正文本体）',
    'books': {
        'YHZP': [
            cell('QI_SHI', 'QI', '氣出陽明，水勢恃源，東流滔注', 'YHZP-014-051', '納音三十組注解', 'ANNOTATION',
                 'QI', 'TREND_REF', '水势（纳音语境）', 'PARTIAL', 'SECONDARY', '纳音域', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'PZZQ': [
            cell('QI_SHI', 'QI', '合化之義…以氣而語其生之序也', 'PZZQ-005-004', '論干支', 'ORIGINAL',
                 'QI', 'ESSENCE_DEFINITION', '气为生成之序', 'PARTIAL', 'REFERENCE', '—', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'DTS': [
            cell('QI_SHI', 'TREND', '論才論煞論精神，四柱平和易養成。氣勢攸長無斲喪，關星雖有不傷身', 'DTS-035-001', '六親論·小兒論', 'ORIGINAL',
                 'QI', 'TREND_STATE', '气势正文（气势攸长无斲丧）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('QI_SHI', 'TREND', '又要看氣勢：如在日主雄旺，氣勢在於才官…氣勢在東南', 'DTS-035-002', '六親論·小兒論', 'ANNOTATION',
                 'QI', 'TREND_STATE', '气势方位判断（B1）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
            cell('QI_SHI', 'TREND', '其勢沖奔，不可遏也', 'DTS-008-022', '通天論·天干', 'ANNOTATION',
                 'QI', 'TREND_STATE', '势冲奔（B1）', 'PARTIAL', 'SECONDARY', '注層', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'QTBJ': [
            cell('QI_SHI', 'TREND', '無風自止其勢亂也遇水返化其源其勢盡也', 'QTBJ-002-002', '論木', 'ORIGINAL',
                 'FIVE_ELEMENT', 'TREND_STATE', '木势（生木/死木）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('QI_SHI', 'QI', '生旺旺中生福惡旺裏反宜鬼相制', 'SMTH-023-006', '戰關伏降刑衝破合', 'ORIGINAL',
                 'QI', 'TREND_REF', '生旺气势（战关）', 'PARTIAL', 'SECONDARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'SFTK': [
            cell('QI_SHI', 'SPIRIT', '吉福最宜生旺祿馬全要精神', 'SFTK-133-001', '憎愛賦', 'ORIGINAL',
                 'QI', 'SPIRIT_STATE', '精神（禄马全要精神）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 调候 ============
new_domains['tiao_hou'] = {
    'domain_id': 'TIAO_HOU',
    'term_cluster_id': 'TIAO_HOU_CLIMATE',
    'note': '调候：后世术语，六部原文用寒暖燥湿/解冻/寒冷（QTBJ 绝对核心、DTS 寒温湿燥论）',
    'books': {
        'YHZP': [
            cell('TIAO_HOU', 'CLIMATE', '水主寒，面赤黧黑', 'YHZP-118-006', '論疾病', 'ORIGINAL',
                 'FIVE_ELEMENT', 'CLIMATE_ATTRIBUTE', '五行主性（水主寒）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'PZZQ': [
            cell('TIAO_HOU', 'CLIMATE', '論命惟以月令用神為主，然亦須配氣候而互參之…木逢冬水，雖透官星，亦難準貴，蓋金寒而水益凍',
                 'PZZQ-007-003', '論用神格局高低', 'ORIGINAL', 'QI', 'CLIMATE_CONDITION',
                 '配气候互参（金寒水冻影响格局）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('TIAO_HOU', 'CLIMATE', '過於濕者，滯而無成；過於燥者，烈而有禍', 'DTS-026-004', '通天論·寒溫濕燥論', 'ANNOTATION',
                 'FIVE_ELEMENT', 'CLIMATE_RULE', '寒温湿燥核心（湿滞燥祸）', 'PARTIAL', 'SECONDARY', '注層B1', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
            cell('TIAO_HOU', 'CLIMATE', '金水傷官，寒則冷嗽，熱則痰嗽', 'DTS-053-011', '六親論·疾病', 'ORIGINAL',
                 'TEN_GOD', 'CLIMATE_RULE', '寒热病症（调候疾病）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'QTBJ': [
            cell('TIAO_HOU', 'CLIMATE', '濕泥寒凍非丙暖不生取丙爲尊', 'QTBJ-060-001', '三冬己土', 'ORIGINAL',
                 'DAY_STEM', 'CLIMATE_RULE', '调候核心（寒冻取丙）', 'ALIGNED', 'PRIMARY（絕對核心）', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('TIAO_HOU', 'CLIMATE', '值冰凍之時。金水無交歡之象。專用丙火解凍', 'QTBJ-109-001', '十一月癸水', 'ORIGINAL',
                 'DAY_STEM', 'CLIMATE_RULE', '调候（冰冻结冻用丙）', 'ALIGNED', 'PRIMARY（絕對核心）', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'SMTH': [
            cell('TIAO_HOU', 'CLIMATE', '金清水冷。日鎖鸞臺。土燥火炎。夜寒鴛帳', 'SMTH-043-004', '招嫁不定', 'ORIGINAL',
                 'FIVE_ELEMENT', 'CLIMATE_REF', '寒燥（女命语境）', 'PARTIAL', 'REFERENCE', '—', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'SFTK': [
            cell('TIAO_HOU', 'CLIMATE', '孟春之令猶有微寒當用火以溫煖則木無盤屈之拘', 'SFTK-061-006', '五星論', 'ORIGINAL',
                 'FIVE_ELEMENT', 'CLIMATE_RULE', '微寒用火温暖（四时调候）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
    },
}

# ============ 通关 ============
new_domains['tong_guan'] = {
    'domain_id': 'TONG_GUAN',
    'term_cluster_id': 'TONG_GUAN_LINK',
    'note': '通关：DTS 通關論正文（牛郎织女）；其余五部无「通關」一词；「引化」六部0命中（后世术语）',
    'books': {
        'YHZP': [
            cell('TONG_GUAN', 'QI_LINK', '其法寅卯相通、辰巳相通、午未相通、申酉相通、戌亥相通、子丑相通', 'YHZP-021-002', '論起通法', 'ANNOTATION',
                 'BRANCH', 'QI_LINK', '地支通气（通=支气相贯，非引化通关）', 'PARTIAL', 'SECONDARY', '注層B1；此「通」=支通气，勿与引化通關混', 'B', 'ORIGINAL_ANNOTATION', 'SUPPORTING_RULE_ONLY'),
        ],
        'PZZQ': [
            cell('TONG_GUAN', 'LINK', '月令所藏不一，而用神遂有變化', 'PZZQ-005-009', '論干支', 'ORIGINAL',
                 'USEFUL_GOD', 'CHANGE_MECHANISM', '用神变化（月令藏干主次）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
        ],
        'DTS': [
            cell('TONG_GUAN', 'LINK', '關內有織女，關外有牛郎。此關若通也，相激入洞房', 'DTS-019-001', '通天論·通關論', 'ORIGINAL',
                 'FIVE_ELEMENT', 'LINK_DEFINITION', '通关正文本体（关通则相合相生）', 'ALIGNED', 'PRIMARY', '—', 'A', 'ORIGINAL_AUTHOR', 'CORE_RULE_ELIGIBLE'),
            cell('TONG_GUAN', 'LINK', '木土而得火，火金而得土，土水而得金，金木而得水…乃為通關也', 'DTS-019-002', '通天論·通關論', 'ANNOTATION',
                 'FIVE_ELEMENT', 'LINK_MECHANISM', '通关具体机制（引合会之神/补所缺之物）', 'PARTIAL', 'SECONDARY', '注層B1', 'B', 'ORIGINAL_ANNOTATION', 'CANDIDATE_RULE'),
        ],
        'QTBJ': [
            cell('TONG_GUAN', 'LINK', '（无「通關」原文）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
        ],
        'SMTH': [
            cell('TONG_GUAN', 'LINK', '月中通氣無衝破，必定榮華仕路人', 'SMTH-074-001', '六乙日甲申時斷', 'ORIGINAL',
                 'QI', 'QI_LINK', '月中通气（日时断语）', 'PARTIAL', 'REFERENCE', '日時斷語為條件變量', 'A', 'ORIGINAL_AUTHOR', 'CONDITIONAL'),
        ],
        'SFTK': [
            cell('TONG_GUAN', 'LINK', '（无「通關」原文）', None, '—', '—', '—', '—', 'NOT_FOUND', '—', '—', None, None, None, 'FAIL_CLOSED'),
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
