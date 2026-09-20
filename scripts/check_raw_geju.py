# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.pzzq_producer_v1 import produce_pattern_candidates

# 十神映射
TEN_GOD = {
    ('甲','甲'):'比肩', ('甲','乙'):'劫财', ('甲','丙'):'食神', ('甲','丁'):'伤官', ('甲','戊'):'偏财',
    ('甲','己'):'正财', ('甲','庚'):'七杀', ('甲','辛'):'正官', ('甲','壬'):'偏印', ('甲','癸'):'正印',
}
# 简化：用五行生克计算十神
WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

def get_ten_god(day, other):
    dw = WUXING[day]; ow = WUXING[other]
    if dw == ow:
        return '比肩' if (day, other) in [('甲','甲'),('丙','丙'),('戊','戊'),('庚','庚'),('壬','壬')] else '劫财'
    if SHENG[dw] == ow:
        return '食神' if (day, other) in [('甲','丙'),('丙','戊'),('戊','庚'),('庚','壬'),('壬','甲')] else '伤官'
    if KE[dw] == ow:
        return '偏财' if (day, other) in [('甲','戊'),('丙','庚'),('戊','壬'),('庚','甲'),('壬','丙')] else '正财'
    if SHENG[ow] == dw:
        return '偏印' if (day, other) in [('甲','壬'),('丙','甲'),('戊','丙'),('庚','戊'),('壬','庚')] else '正印'
    if KE[ow] == dw:
        return '七杀' if (day, other) in [('甲','庚'),('丙','壬'),('戊','甲'),('庚','丙'),('壬','戊')] else '正官'
    return '未知'

# 月令本气
MONTH_BENQI = {
    '子':'癸','丑':'己','寅':'甲','卯':'乙','辰':'戊','巳':'丙',
    '午':'丁','未':'己','申':'庚','酉':'辛','戌':'戊','亥':'壬'
}

with open(r'D:\顺天系统资料\用神案例JSONL\原局层\用神专项\用神_all.jsonl', 'r', encoding='utf-8') as f:
    cases = [json.loads(line) for line in f if line.strip()]

GEJU_PATTERNS = ['正官格','偏官格','七杀格','正财格','偏财格','正印格','偏印格','食神格','伤官格','建禄格','月劫格','羊刃格','阳刃格','从财格','从杀格','从儿格','从官格','曲直格','炎上格','稼穑格','从革格','润下格','化气格','化土格','化木格','化金格','化水格','化火格','合禄格','井栏叉格','六阴朝阳格','刑合格']

total = 0
raw_has_geju = 0
raw_benqi_match = 0  # 原文格局与月令本气十神一致
raw_benqi_mismatch = 0  # 原文格局与月令本气十神不一致
mismatch_cases = []

for case in cases:
    chart_str = case.get('bazi', '')
    if not chart_str or len(chart_str) < 8:
        continue
    total += 1
    text = case.get('raw', '')
    
    # 提取原文格局
    raw_geju = []
    for pat in GEJU_PATTERNS:
        if pat in text:
            raw_geju.append(pat)
    
    if not raw_geju:
        continue
    raw_has_geju += 1
    
    # 计算月令本气十神
    try:
        pillars = {
            'year': chart_str[0:2], 'month': chart_str[2:4],
            'day': chart_str[4:6], 'hour': chart_str[6:8]
        }
        day_stem = pillars['day'][0]
        month_branch = pillars['month'][1]
        benqi_stem = MONTH_BENQI[month_branch]
        benqi_tg = get_ten_god(day_stem, benqi_stem)
        benqi_geju = benqi_tg + '格'
    except:
        continue
    
    # 检查原文格局是否包含月令本气十神格
    if benqi_geju in raw_geju:
        raw_benqi_match += 1
    else:
        raw_benqi_mismatch += 1
        mismatch_cases.append({
            'chart': chart_str,
            'raw_geju': raw_geju,
            'benqi_geju': benqi_geju,
            'day_stem': day_stem,
            'month_branch': month_branch
        })

print('总案例数:', total)
print('原文有格局:', raw_has_geju)
print('原文格局与月令本气一致:', raw_benqi_match)
print('原文格局与月令本气不一致:', raw_benqi_mismatch)
if raw_has_geju > 0:
    print('不一致比例: %.1f%%' % (raw_benqi_mismatch / raw_has_geju * 100))
print()
print('前15个不一致案例:')
for i, c in enumerate(mismatch_cases[:15]):
    print('%d. %s 原文=%s 月令本气=%s(%s月%s)' % (
        i+1, c['chart'], c['raw_geju'], c['benqi_geju'], c['month_branch'], c['day_stem']))
