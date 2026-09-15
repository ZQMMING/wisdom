# -*- coding: utf-8 -*-
"""R1-05 冻结边界落库：为 25 领域补 classical_usage_type + rule_boundary（Human 2026-09-16 裁决）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
with io.open(P, encoding='utf-8') as f:
    data = json.load(f)

# (domain_key, classical_usage_type, rule_boundary)
BOUNDARIES = {
    'domain_01_wang_qiang_shuai': (
        'FOUNDATIONAL',
        {'allowed': ['六部各自旺强衰结构判定（逐书语境）'], 'forbidden': ['统一旺衰算法', 'WANG→STRONG 自动映射', '旺=强']}),
    'domain_02_ling_shi_di_gen': (
        'FOUNDATIONAL',
        {'allowed': ['得令/得时/得地/得垣/持势独立建模（对象化）'], 'forbidden': ['得令=身强', '得地=身强', '时=令=得令', 'RULING_SCHEDULE→WEIGHT']}),
    'domain_03_shi': (
        'FOUNDATIONAL',
        {'allowed': ['STRUCTURAL_TREND_STATE 独立判定（DTS-035-001 气势正文）'], 'forbidden': ['势=强', 'TREND_STATE→STRENGTH_STATE']}),
    'domain_04_yue_ling': (
        'FOUNDATIONAL',
        {'allowed': ['月令为结构入口（PZZQ-005-007 专求月令）'], 'forbidden': ['月令→Boolean→身旺', '月令统一判定算法']}),
    'domain_05_ge_ju': (
        'PRIMARY_RULE',
        {'allowed': ['PZZQ 用神格局判断', 'SFTK 从化→财官→格局入口（SFTK-082-001）'], 'forbidden': ['统一八字格局判断', '跨书偷换格局语义']}),
    'domain_06_yong_shen': (
        'PRIMARY_RULE',
        {'allowed': ['PZZQ 用神判断（月令专求）', 'SFTK 病药用神（病药域）', 'QTBJ 调候取用（调候域）'], 'forbidden': ['统一八字用神', '用神=喜神=相神混用']}),
    'domain_07_bing_yao': (
        'PRIMARY_RULE',
        {'allowed': ['SFTK 病药诊断（先看月令→从重者论，SFTK-008-001）'], 'forbidden': ['病药=统一用神算法', '病药救应=相神']}),
    'domain_08_qing_zhuo_zhen_jia': (
        'PRIMARY_RULE',
        {'allowed': ['DTS 清浊结构事实判定（透干/相战，DTS-022-002 B1）'], 'forbidden': ['清浊量化阈值', '清枯/半浊半清重叠归类']}),
    'domain_09_cong_hua': (
        'PRIMARY_RULE',
        {'allowed': ['SFTK 从化判定入口（SFTK-082-001）', 'DTS 化象不遇条件（DTS-041-002）'], 'forbidden': ['甲己不遇集合机械复制给其他四合']}),
    'wuxing_base': (
        'FOUNDATIONAL',
        {'allowed': ['六部五行生克总纲（YHZP-054-001 等）'], 'forbidden': ['跨书统一五行定义', 'DTS 无 A 级生克总纲时用反局冒充']}),
    'shishen': (
        'FOUNDATIONAL',
        {'allowed': ['六部十神定名/六亲配属（各自语境）'], 'forbidden': ['同一十神名跨书强制同一语义']}),
    'shengwang_xiuqiu': (
        'FOUNDATIONAL',
        {'allowed': ['十二长生逐干（YHZP-015-002 A）', '阳顺阴逆（PZZQ-005-002 A）'], 'forbidden': ['十二长生统一算法', '生旺=身旺']}),
    'gen_qi': (
        'FOUNDATIONAL',
        {'allowed': ['ROOT(object=日主/官/财/杀/印) 对象化解析', 'DTS-010-003 不论有根无根俱要天覆地载'], 'forbidden': ['ROOT≠DAY_MASTER_ONLY', 'has_root(day_master) 作为通用强弱开关']}),
    'dang_zhong': (
        'PRIMARY_RULE',
        {'allowed': ['DTS-057-001 午之黨多必凶（结构事实）'], 'forbidden': ['党众=数量阈值≥N', '神煞得党（EXCLUDED）']}),
    'shengfu_kexie': (
        'FOUNDATIONAL',
        {'allowed': ['五行五类关系定名（YHZP-054-002 B1）', '泄气/回克（SFTK-020-034 A）'], 'forbidden': ['生扶克泄耗统一权重/评分']}),
    'qi_shi': (
        'PRIMARY_RULE',
        {'allowed': ['DTS-035-001 气势攸长无斲丧（正文 A）'], 'forbidden': ['气势=强', '气势量化']}),
    'tiao_hou': (
        'PRIMARY_RULE',
        {'allowed': ['QTBJ 调候取用（CLASSICAL_SCOPE=QTBJ 必须绑定）', 'PZZQ 配气候互参（PZZQ-007-003，CONTEXTUAL）'], 'forbidden': ['统一调候喜忌算法', '调候作为统一八字基础层', '寒暖=通关']}),
    'tong_guan': (
        'SUPPORTING',
        {'allowed': ['DTS-019-001《通關論》通关（DTS_SCOPE_ONLY，正文 A）'], 'forbidden': ['YHZP引化=通关', 'QTBJ寒暖=通关', 'SFTK病药=通关', 'CONCEPT_SIMILAR≠CONCEPT_EQUAL 违规合并']}),
    'geju_chengbai': (
        'PRIMARY_RULE',
        {'allowed': ['PZZQ-005-008 成败判定', 'PZZQ-007-002 因成得败/因败得成'], 'forbidden': ['成败=Boolean', '跨书成败统一']}),
    'xiang_shen': (
        'SUPPORTING',
        {'allowed': ['PZZQ-007-004 相神定义（PZZQ_ONLY）'], 'forbidden': ['病药救应=相神', '其他书注册 xiangshen_state']}),
    'shun_ni': (
        'PRIMARY_RULE',
        {'allowed': ['PZZQ-005-007 顺逆用（正文 A）', 'DTS-025-001 顺其气势（DTS_PRIMARY）'], 'forbidden': ['其他经典引用顺逆未经重新验证', '顺逆=阳顺阴逆混用']}),
    'ganzhi_zuhe': (
        'FOUNDATIONAL',
        {'allowed': ['PZZQ-005-006 刑冲会合定义（正文 A）', '干支组合断语（各书语境）'], 'forbidden': ['刑冲会合统一量化']}),
    'liu_qin': (
        'PRIMARY_RULE',
        {'allowed': ['YHZP-102-001 六亲配属（正文 A）', 'PZZQ-007-012 用神配六亲', 'SFTK-007-002 六亲宫位'], 'forbidden': ['六亲跨书强制统一', '命例反推六亲规则']}),
    'shen_sha': (
        'EXCLUDED',
        {'allowed': ['文献检索', '参考展示'], 'forbidden': ['命局核心裁决', '用神判断', '吉凶自动输出', 'RULE 层准入']}),
    'ming_li': (
        'REFERENCE_ONLY',
        {'allowed': ['Rule 验证', 'Golden Case', 'Regression Test'], 'forbidden': ['从命例反推规则', '命例作 PRIMARY 证据']}),
}

added = 0
for key, (usage, boundary) in BOUNDARIES.items():
    if key in data:
        data[key]['classical_usage_type'] = usage
        data[key]['rule_boundary'] = boundary
        added += 1

with io.open(P, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'已补 {added}/25 领域：classical_usage_type + rule_boundary')
for k, v in BOUNDARIES.items():
    print(f'  {k}: {v[0]}')
