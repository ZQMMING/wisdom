# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

shenruo_heavy=[]
for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    if '身弱' in text and r['root_class']=='HEAVY':
        idx = text.find('身弱')
        context = text[max(0,idx-20):idx+len('身弱')+20]
        exclude=['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不', '非身弱', '不论身', '身弱者']
        if any(ex in context for ex in exclude):
            continue
        if not ('LIGHT-ROOT' in qs or 'JIRUO-WUGEN' in qs or 'JISHUAI-CONGSHENG' in qs or 'CAIDUO-SHENRUAN' in qs or 'SHAZHONG-SHENQING' in qs):
            shenruo_heavy.append(r)

print(f'身弱HEAVY不匹配: {len(shenruo_heavy)}')
print()

# 分类
root_struck=0
xieqi=0
caiduo=0
shazhong=0
other=0
for r in shenruo_heavy:
    qs=r['queries']
    if 'ROOT-STRUCK' in qs:
        root_struck+=1
    elif 'XIEQI-TAIZHONG' in qs:
        xieqi+=1
    elif 'CAIDUO-SHENRUAN' in qs:
        caiduo+=1
    elif 'SHAZHONG-SHENQING' in qs:
        shazhong+=1
    else:
        other+=1

print(f'ROOT-STRUCK: {root_struck}')
print(f'XIEQI-TAIZHONG: {xieqi}')
print(f'CAIDUO-SHENRUAN: {caiduo}')
print(f'SHAZHONG-SHENQING: {shazhong}')
print(f'其他: {other}')
print()

# 看其他案例
print('其他案例:')
for r in shenruo_heavy:
    qs=r['queries']
    if 'ROOT-STRUCK' not in qs and 'XIEQI-TAIZHONG' not in qs and 'CAIDUO-SHENRUAN' not in qs and 'SHAZHONG-SHENQING' not in qs:
        print(f'  {r["chart"]}: {qs[:80]}')
        print(f'    {r["judgment"][:80]}')
