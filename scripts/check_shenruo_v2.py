# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

def check_shenruo(r):
    qs=r['queries']
    root=r['root_class']
    if 'LIGHT-ROOT' in qs or 'JIRUO-WUGEN' in qs or 'JISHUAI-CONGSHENG' in qs or 'CAIDUO-SHENRUAN' in qs or 'SHAZHONG-SHENQING' in qs:
        return True
    if 'ROOT-STRUCK' in qs and root=='HEAVY':
        return True
    return False

shenruo_mismatch=[]
for r in rows:
    text = r.get('judgment','')
    if '身弱' in text:
        idx = text.find('身弱')
        context = text[max(0,idx-20):idx+len('身弱')+20]
        exclude=['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不', '非身弱', '不论身', '身弱者']
        if any(ex in context for ex in exclude):
            continue
        if not check_shenruo(r):
            shenruo_mismatch.append(r)

print(f'身弱不匹配: {len(shenruo_mismatch)}')
print()
for r in shenruo_mismatch:
    print(f'{r["chart"]}: root={r["root_class"]}')
    print(f'  queries: {r["queries"][:100]}')
    print(f'  judgment: {r["judgment"][:100]}')
    print()
