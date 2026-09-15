# -*- coding: utf-8 -*-
"""R1-03：12月×12时×6经典 人元用事 schedule 矩阵构建"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'D:\shuntian-ziping-p0\registries\source'

# 12 月支（按节气月）+ 12 时支
MONTHS = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
HOURS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 依据扫描证据构建：schedule_match 字典
# 每格: {book: {source_id, text_layer, grade, schedule_desc, level3: bool}}

# --- LEVEL-3 schedule 证据（仅有的精确时间表） ---
# YHZP-056-001 论天地干支暗藏总诀（ORIGINAL/A，12月完整）
YHZP_SCHEDULE = {
    '寅': ('YHZP-056-001', 'ORIGINAL', 'A', '立春念三丙火用，餘日甲木旺提綱'),
    '卯': ('YHZP-056-001', 'ORIGINAL', 'A', '驚蟄乙木未用事，春分乙未正相當'),
    '辰': ('YHZP-056-001', 'ORIGINAL', 'A', '清明乙木十日管，後來八日癸水洋；穀雨前三戊土盛'),
    '巳': ('YHZP-056-001', 'ORIGINAL', 'A', '立夏又代戊土取，小滿過午丙火光'),
    '午': ('YHZP-056-001', 'ORIGINAL', 'A', '芒種己土相當好，中停七日土高張；夏至丙丁火旺有土張'),
    '未': ('YHZP-056-001', 'ORIGINAL', 'A', '小暑十日丁火旺，後來三日乙木芳，己土三日威風盛，大暑己土十日黃'),
    '申': ('YHZP-056-001', 'ORIGINAL', 'A', '立秋十日壬水漲，處暑十五庚金良'),
    '酉': ('YHZP-056-001', 'ORIGINAL', 'A', '白露七日庚金旺，八日辛兮祇獨行'),
    '戌': ('YHZP-056-001', 'ORIGINAL', 'A', '寒露七日辛金管，八日丁火又水降；霜降己土十五日'),
    '亥': ('YHZP-056-001', 'ORIGINAL', 'A', '立冬七日癸水旺，壬水八日更流忙；小雪七日壬水急，八日甲木又芬芳'),
    '子': ('YHZP-056-001', 'ORIGINAL', 'A', '大雪七日壬水管，冬至癸水更潺汪'),
    '丑': ('YHZP-056-001', 'ORIGINAL', 'A', '小寒七日癸水養，八日辛金五庫藏；大寒十日己土勝'),
}

# DTS 原注 schedule（B1）
DTS_SCHEDULE_MONTH = {
    '寅': ('DTS-015-004', 'ANNOTATION', 'B', '立春後七日戊土用事，八日後十四日前者丙火用事，十五日後甲木用事'),
}
DTS_SCHEDULE_HOUR = {
    '子': ('DTS-015-006', 'ANNOTATION', 'B', '前三刻三分壬水用事，後三刻七分癸水用事'),
}

# QTBJ 上半月/下半月粗分（LEVEL-2.5，非精确日程）
QTBJ_HALF = {
    '午': ('QTBJ-018-001', 'ORIGINAL', 'A', '五月乙木：上半月屬陽…後下半月屬陰（三伏生寒）'),
}

matrix = {'months': {}, 'hours': {}}

# 月支矩阵：book → 每格
books = ['yhzp', 'pzzq', 'dts', 'qtbj', 'smth', 'sftk']
for m in MONTHS:
    matrix['months'][m] = {
        'yhzp': {'schedule_match': m in YHZP_SCHEDULE, 'source': YHZP_SCHEDULE.get(m, (None, None, None, None))[0],
                 'text_layer': YHZP_SCHEDULE.get(m, (None, None, None, None))[1],
                 'grade': YHZP_SCHEDULE.get(m, (None, None, None, None))[2],
                 'desc': YHZP_SCHEDULE.get(m, (None, None, None, None))[3]},
        'pzzq': {'schedule_match': False, 'source': None, 'text_layer': None, 'grade': None, 'desc': 'NOT_FOUND（真诠用月令取格，无精确用事日程）'},
        'dts': {'schedule_match': m in DTS_SCHEDULE_MONTH, 'source': DTS_SCHEDULE_MONTH.get(m, (None, None, None, None))[0],
                'text_layer': DTS_SCHEDULE_MONTH.get(m, (None, None, None, None))[1],
                'grade': DTS_SCHEDULE_MONTH.get(m, (None, None, None, None))[2],
                'desc': DTS_SCHEDULE_MONTH.get(m, (None, None, None, None))[3] if m in DTS_SCHEDULE_MONTH else 'NOT_FOUND（仅寅月有具体日程）'},
        'qtbj': {'schedule_match': m in QTBJ_HALF, 'source': QTBJ_HALF.get(m, (None, None, None, None))[0],
                 'text_layer': QTBJ_HALF.get(m, (None, None, None, None))[1],
                 'grade': QTBJ_HALF.get(m, (None, None, None, None))[2],
                 'desc': QTBJ_HALF.get(m, (None, None, None, None))[3] if m in QTBJ_HALF else 'NOT_FOUND（司權體系無精確日程）'},
        'smth': {'schedule_match': False, 'source': None, 'text_layer': None, 'grade': None, 'desc': 'NOT_FOUND（當權零星詩訣，無時間表）'},
        'sftk': {'schedule_match': False, 'source': None, 'text_layer': None, 'grade': None, 'desc': 'NOT_FOUND（當權/司權體系無精確日程）'},
    }

# 时支矩阵
for h in HOURS:
    matrix['hours'][h] = {
        'dts': {'schedule_match': h in DTS_SCHEDULE_HOUR, 'source': DTS_SCHEDULE_HOUR.get(h, (None, None, None, None))[0],
                'text_layer': DTS_SCHEDULE_HOUR.get(h, (None, None, None, None))[1],
                'grade': DTS_SCHEDULE_HOUR.get(h, (None, None, None, None))[2],
                'desc': DTS_SCHEDULE_HOUR.get(h, (None, None, None, None))[3] if h in DTS_SCHEDULE_HOUR else 'NOT_FOUND'},
    }
    for b in books:
        if b != 'dts':
            matrix['hours'][h][b] = {'schedule_match': False, 'source': None, 'text_layer': None, 'grade': None,
                                     'desc': 'NOT_FOUND（六部无该时支精确用事日程）'}

with open(r'D:\shuntian-ziping-p0\governance\r1_03_schedule_matrix.json', 'w', encoding='utf-8') as f:
    json.dump(matrix, f, ensure_ascii=False, indent=2)

print('R1-03 矩阵已写入 governance/r1_03_schedule_matrix.json')
print('月支 schedule_match 汇总:')
for m in MONTHS:
    hits = [b for b in books if matrix['months'][m][b]['schedule_match']]
    print(f'  {m}: {hits if hits else "全部NOT_FOUND"}')
print('时支 schedule_match:')
for h in HOURS:
    hits = [b for b in ['yhzp','pzzq','dts','qtbj','smth','sftk'] if matrix['hours'][h][b]['schedule_match']]
    print(f'  {h}: {hits if hits else "全部NOT_FOUND"}')
