# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

checks = [
    ('身旺', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '身旺者', '身旺逢', '必要身旺']),
    ('身强', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '身强者']),
    ('身弱', ['LIGHT-ROOT', 'JIRUO-WUGEN', 'JISHUAI-CONGSHENG', 'CAIDUO-SHENRUAN', 'SHAZHONG-SHENQING'], ['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不', '非身弱', '不论身', '身弱者']),
    ('日主旺', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
    ('日主弱', ['LIGHT-ROOT', 'JIRUO-WUGEN', 'JISHUAI-CONGSHENG', 'CAIDUO-SHENRUAN', 'SHAZHONG-SHENQING'], ['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不', '非身弱', '不论身']),
    ('中和', ['ZHONG-HE'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
    ('旺极', ['JIWANG-HUAIJI'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '地旺极', '火旺极', '土旺极', '金旺极', '水旺极', '木旺极', '财旺极', '印旺极', '官旺极', '杀旺极', '偏财旺极', '伤官旺极', '食神旺极', '比劫旺极', '羊刃旺极', '旺极反衰', '旺极所化', '旺极矣']),
    ('衰极', ['JISHUAI-CONGSHENG'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '天衰极', '火衰极', '土衰极', '金衰极', '水衰极', '木衰极']),
    ('弱极', ['JIRUO-WUGEN'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
]

kw_stats={}
for kw,_,_ in checks:
    kw_stats[kw]={'total':0,'match':0,'mismatch':0}

for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    
    for kw, engine_qs, exclude in checks:
        if kw in text:
            idx = text.find(kw)
            context = text[max(0,idx-10):idx+len(kw)+10]
            if any(ex in context for ex in exclude):
                continue
            kw_stats[kw]['total']+=1
            if any(eq in qs for eq in engine_qs):
                kw_stats[kw]['match']+=1
            else:
                kw_stats[kw]['mismatch']+=1

print('关键词准确率分布:')
total_match=0
total_all=0
for kw,s in kw_stats.items():
    if s['total']>0:
        rate=s['match']/s['total']*100
        print(f'  {kw:6s}: {s["match"]}/{s["total"]} = {rate:.1f}% (不匹配{s["mismatch"]})')
        total_match+=s['match']
        total_all+=s['total']
print(f'\n总计: {total_match}/{total_all} = {total_match/total_all*100:.1f}%')
