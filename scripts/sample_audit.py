# -*- coding: utf-8 -*-
"""分层随机抽样: 七档每档抽N例, 输出原文含力量关键词的句子供人工整体核对."""
import re,sys,csv,random; sys.path.insert(0,'.')
DTS=r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines=open(DTS,encoding='utf-8').readlines()
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
GZ=r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ=re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')
def case_text(ln):
    e=ln+1
    while e<len(lines):
        l=lines[e].strip()
        if l.startswith('八字') or l.startswith('====') or l.startswith('【') or BZ.match(l): break
        e+=1
    return ''.join(lines[ln+1:e])
KEY=re.compile(r'旺|衰|强|弱|根|令|得时|失时|得地|得势|身|财多|杀重|煞重|泄|从|化|中和|纯粹|有余|不足|虚|浮|实|厚|薄|助|生扶|克|党|众|寡')
def sents(t):
    ss=re.split(r'[。；！\n]',t)
    out=[s.strip() for s in ss if KEY.search(s) and 4<len(s.strip())<60]
    return out
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 20260918)
N=int(sys.argv[1]) if len(sys.argv)>1 else 6
order=['旺极','太旺','旺','中和','衰','太衰','衰极']
for sp in order:
    grp=[r for r in rows if r.get('spectrum')==sp]
    random.shuffle(grp)
    print('\n'+'='*70+f' 【{sp}】抽{min(N,len(grp))}/{len(grp)}')
    for r in grp[:N]:
        t=case_text(int(r['line']))
        ss=sents(t)[:4]
        print(f"\n●{r['chart']} {r['daymaster']}日 {r.get('month_god','')}月 r{r['ratio']} 根{r['root']}")
        for s in ss: print('   '+s)
