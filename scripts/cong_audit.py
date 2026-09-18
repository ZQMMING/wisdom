# -*- coding: utf-8 -*-
"""审计 DTS 从格/专旺/化气命例 vs 引擎七档."""
import re,sys,csv; sys.path.insert(0,'.')
DTS=r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines=open(DTS,encoding='utf-8').readlines()
rows={r['chart']:r for r in csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig'))}
GZ=r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ=re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')
def case_text(ln):
    e=ln+1
    while e<len(lines):
        l=lines[e].strip()
        if l.startswith('八字') or l.startswith('====') or l.startswith('【') or BZ.match(l): break
        e+=1
    return ''.join(lines[ln+1:e])
CONG=re.compile(r'从[財财杀官兒儿食伤强旺气势其]?|捨命|弃命|真从|假从|曲直|炎上|稼穡|稼穑|從革|从革|潤下|润下|化氣|化气|化[木火土金水]|真化|合化|化象|順其|顺其')
hits=[]
for r in rows.values():
    txt=case_text(int(r['line']))
    ms=set(m.group(0) for m in CONG.finditer(txt))
    if ms:
        # 取紧邻上下文
        ctxs=[]
        for m in CONG.finditer(txt):
            ctxs.append(txt[max(0,m.start()-8):m.start()+10].replace('\n',''))
        hits.append((r['chart'],r['daymaster'],r.get('spectrum'),r.get('ratio'),r.get('root'),'|'.join(sorted(ms)),' ; '.join(ctxs[:3])))
print(f'含从/化/专旺关键词命例: {len(hits)}')
for ch,dm,sp,rt,root,kw,ctx in sorted(hits,key=lambda z:z[2]):
    print(f'{ch} {dm} 引擎={sp}(r{rt},根{root}) [{kw}] {ctx}')
