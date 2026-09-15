# -*- coding: utf-8 -*-
"""R1-04：SOURCE_ALIGNMENT —— 人元用事 概念/机制/schedule 三层对齐"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 六部
BOOKS = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
NAMES = {'yhzp': 'YHZP渊海', 'pzzq': 'PZZQ真诠', 'dts': 'DTS滴天',
         'qtbj': 'QTBJ穷通', 'smth': 'SMTH三命', 'sftk': 'SFTK神峰'}

# 基于 R1-03 扫描证据构建对齐矩阵
# 每层状态：ALIGNED / PARTIALLY_ALIGNED / CONFLICT / NOT_FOUND
alignment = {
    'domain': 'human_element_use_shi',  # 人元用事
    'layers': {
        'LEVEL-1_CONCEPT': {  # 概念层：人元/藏干/用事/司令 概念存在性
            'yhzp': {'status': 'ALIGNED', 'evidence': 'YHZP-030-001 論三元「子中所藏癸水為人元」；049-002 四時用事', 'priority': 'A'},
            'pzzq': {'status': 'PARTIALLY_ALIGNED', 'evidence': '無「人元/用事」詞，以「八字用神專求月令」表達月令主事', 'priority': 'A'},
            'dts': {'status': 'ALIGNED', 'evidence': '015-003 正文「人元用事之神，宅之向也」', 'priority': 'A'},
            'qtbj': {'status': 'ALIGNED', 'evidence': '48 條司權/司令/當權體系', 'priority': 'A'},
            'smth': {'status': 'PARTIALLY_ALIGNED', 'evidence': '「當權」零星詩訣（142-001 丙臨寅馬卻當權）', 'priority': 'A'},
            'sftk': {'status': 'ALIGNED', 'evidence': '123-002「支中所藏者為人元」+ 36 條當權體系', 'priority': 'A'},
        },
        'LEVEL-2_MECHANISM': {  # 机制层：时间位置→地支→藏干→用事主体→取用
            'yhzp': {'status': 'ALIGNED', 'evidence': '056-001 總訣 12 月分段 + 049-002 四時用事', 'priority': 'A'},
            'pzzq': {'status': 'ALIGNED', 'evidence': '月令取格機制（用神專求月令），無具體日程但機制一致', 'priority': 'A'},
            'dts': {'status': 'ALIGNED', 'evidence': '015-004 令星用事「知此可以取用，亦可以取格矣」', 'priority': 'B1'},
            'qtbj': {'status': 'ALIGNED', 'evidence': '逐月司權標注（如「丙火司權」「庚金司令」）', 'priority': 'A'},
            'smth': {'status': 'PARTIALLY_ALIGNED', 'evidence': '當權零星，未成體系', 'priority': 'A'},
            'sftk': {'status': 'ALIGNED', 'evidence': '當權/司權體系 + 十干逐月歌（061-033/035）', 'priority': 'A'},
        },
        'LEVEL-3_SCHEDULE': {  # schedule 层：精确时间表（仅此层裁决执行资格）
            'yhzp': {'status': 'ALIGNED', 'evidence': '056-001 12/12 月完整時間表（立春念三丙火用餘日甲木旺提綱…大寒十日己土勝）', 'priority': 'A', 'eligibility': 'CORE_RULE_ELIGIBLE'},
            'pzzq': {'status': 'NOT_FOUND', 'evidence': '無精確用事日程', 'priority': None, 'eligibility': 'FAIL_CLOSED'},
            'dts': {'status': 'PARTIALLY_ALIGNED', 'evidence': '寅月三段（015-004）+ 子時（015-006），其餘 NOT_FOUND', 'priority': 'B1', 'eligibility': 'CANDIDATE_RULE'},
            'qtbj': {'status': 'PARTIALLY_ALIGNED', 'evidence': '僅午月上半月/下半月粗分（018-001），非精確日程', 'priority': 'A', 'eligibility': 'CANDIDATE_RULE（粗分）'},
            'smth': {'status': 'NOT_FOUND', 'evidence': '無時間表', 'priority': None, 'eligibility': 'FAIL_CLOSED'},
            'sftk': {'status': 'NOT_FOUND', 'evidence': '當權體系無精確日程', 'priority': None, 'eligibility': 'FAIL_CLOSED'},
        },
    },
    'schedule_variants': {
        '寅月': {
            'status': 'CONFLICT',
            'yhzp': {'source': 'YHZP-056-001', 'grade': 'A', 'schedule': '立春念三丙火用，餘日甲木旺提綱'},
            'dts': {'source': 'DTS-015-004', 'grade': 'B1', 'schedule': '立春後七日戊土，八日後十四日前丙火，十五日後甲木'},
            'note': '兩套體系無法合併；禁止平均/投票/覆蓋/拼接（003A-RULE-10）',
        },
        '子時': {
            'status': 'PARTIALLY_ALIGNED',
            'dts': {'source': 'DTS-015-006', 'grade': 'B1', 'schedule': '前三刻三分壬水，後三刻七分癸水'},
            'others': '其餘五書 NOT_FOUND；禁止從任氏曰「余時亦有前後用事」反推具體日數（FAIL_CLOSED）',
        },
        '其餘11時支': {
            'status': 'NOT_FOUND',
            'note': '六部無精確 schedule；禁止現代補全、禁止從月令 schedule 類推',
        },
    },
    'source_priority': {
        'note': 'SOURCE_PRIORITY 僅表示證據/執行資格層級，不表示書的高下',
        'rules': [
            {'source': 'YHZP-056-001', 'book': 'YHZP', 'grade': 'A', 'schedule_scope': '12/12月', 'eligibility': 'CORE_RULE_ELIGIBLE'},
            {'source': 'DTS-015-004', 'book': 'DTS', 'grade': 'B1', 'schedule_scope': '寅月', 'eligibility': 'CANDIDATE_RULE'},
            {'source': 'DTS-015-006', 'book': 'DTS', 'grade': 'B1', 'schedule_scope': '子時', 'eligibility': 'CANDIDATE_RULE'},
            {'source': 'QTBJ-018-001', 'book': 'QTBJ', 'grade': 'A', 'schedule_scope': '午月上半月/下半月', 'eligibility': 'CANDIDATE_RULE（粗分）'},
        ],
    },
}

with open(r'D:\shuntian-ziping-p0\governance\r1_04_source_alignment.json', 'w', encoding='utf-8') as f:
    json.dump(alignment, f, ensure_ascii=False, indent=2)

print('R1-04 SOURCE_ALIGNMENT 已写入 governance/r1_04_source_alignment.json')
print('\n三层对齐状态汇总：')
for layer, books_map in alignment['layers'].items():
    print(f'\n{layer}:')
    for b, v in books_map.items():
        print(f'  {NAMES[b]}: {v["status"]}')
print('\nschedule_variants:')
for k, v in alignment['schedule_variants'].items():
    print(f'  {k}: {v["status"]}')
