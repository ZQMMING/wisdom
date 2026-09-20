# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build

GEJU_PATTERNS = ['正官格','偏官格','七杀格','正财格','偏财格','正印格','偏印格','食神格','伤官格','建禄格','月劫格','羊刃格','阳刃格','从财格','从杀格','从儿格','从官格','曲直格','炎上格','稼穑格','从革格','润下格','化气格','化土格','化木格','化金格','化水格','化火格','合禄格','井栏叉格','六阴朝阳格','刑合格']

with open(r'D:\顺天系统资料\用神案例JSONL\原局层\用神专项\用神_all.jsonl', 'r', encoding='utf-8') as f:
    cases = [json.loads(line) for line in f if line.strip()]

total = 0
raw_has_geju = 0
raw_benqi_match = 0
raw_benqi_mismatch = 0
mismatch_cases = []

for case in cases:
    chart_str = case.get('bazi', '')
    if not chart_str or len(chart_str) < 8:
        continue
    total += 1
    text = case.get('raw', '')
    
    raw_geju = []
    for pat in GEJU_PATTERNS:
        if pat in text:
            raw_geju.append(pat)
    
    if not raw_geju:
        continue
    raw_has_geju += 1
    
    try:
        pillars = {
            'year': chart_str[0:2], 'month': chart_str[2:4],
            'day': chart_str[4:6], 'hour': chart_str[6:8]
        }
        f = build(pillars)
        day_stem = f['day_stem']
        month_branch = f['month_branch']
        
        # 从ten_god_members中找月令本气的十神
        benqi_tg = None
        for item in f.get('ten_god_members', []):
            if item.get('pillar') == 'month' and item.get('type') == 'hidden' and item.get('qi_position') == '本气':
                benqi_tg = item.get('ten_god')
                break
        
        if not benqi_tg:
            continue
        
        benqi_geju = benqi_tg + '格'
    except Exception as e:
        continue
    
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
print('全部不一致案例:')
for i, c in enumerate(mismatch_cases):
    print('%d. %s 原文=%s 月令本气=%s(%s日%s月)' % (
        i+1, c['chart'], c['raw_geju'], c['benqi_geju'], c['day_stem'], c['month_branch']))
