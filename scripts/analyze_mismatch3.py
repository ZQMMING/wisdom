# -*- coding: utf-8 -*-
import csv, re
with open(r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

with open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt', encoding='utf-8-sig') as f:
    content = f.read()

# 统计不匹配类型
mismatch_types = {}
for row in rows:
    chart = row['chart']
    dayun_str = row.get('dayun', '')
    if not dayun_str:
        continue
    dayun_list = dayun_str.split('|')
    
    engine_xiji = {}
    for item in row.get('dayun_xiji', '').split('|'):
        if ':' in item:
            parts = item.split(':')
            gz = parts[0]
            label = parts[1] if len(parts) > 1 else ''
            engine_xiji[gz] = label
    
    chart_no_space = chart.replace(' ', '')
    chart_pattern = re.compile(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])')
    for m in chart_pattern.finditer(content):
        found = ''.join(m.groups())
        if found == chart_no_space:
            start = m.end()
            next_m = chart_pattern.search(content, start + 10)
            end = next_m.start() if next_m else min(len(content), start + 2000)
            ctx = content[start:end]
            
            for gz in dayun_list:
                if gz in engine_xiji:
                    engine_label = engine_xiji[gz]
                    gz_pos = ctx.find(gz)
                    if gz_pos >= 0:
                        gz_ctx = ctx[max(0, gz_pos-20):min(len(ctx), gz_pos+60)]
                        xi_kw = ['喜', '利', '吉', '宜', '发', '亨', '通']
                        ji_kw = ['忌', '不利', '凶', '不宜', '夭', '贫', '败', '破', '灾', '病', '死', '嫌']
                        has_xi = any(kw in gz_ctx for kw in xi_kw)
                        has_ji = any(kw in gz_ctx for kw in ji_kw)
                        
                        if 'SUPPRESS' in engine_label and has_xi and not has_ji:
                            key = '引擎SUPPRESS_原文XI'
                            mismatch_types[key] = mismatch_types.get(key, 0) + 1
                        elif 'SUPPORT' in engine_label and has_ji and not has_xi:
                            key = '引擎SUPPORT_原文JI'
                            mismatch_types[key] = mismatch_types.get(key, 0) + 1
                        elif 'NEUTRAL' in engine_label and has_xi and not has_ji:
                            key = '引擎NEUTRAL_原文XI'
                            mismatch_types[key] = mismatch_types.get(key, 0) + 1
                        elif 'NEUTRAL' in engine_label and has_ji and not has_xi:
                            key = '引擎NEUTRAL_原文JI'
                            mismatch_types[key] = mismatch_types.get(key, 0) + 1
            break

print('=== 不匹配类型统计(优化后) ===')
for k, v in sorted(mismatch_types.items(), key=lambda x: -x[1]):
    print(f'{k}: {v}')
