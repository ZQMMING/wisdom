# -*- coding: utf-8 -*-
import re
DTS=r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines=open(DTS,encoding='utf-8').readlines()
GZ=r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ=re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')
def case_text(ln):
    e=ln+1
    while e<len(lines):
        l=lines[e].strip()
        if l.startswith('八字：') or l.startswith('====') or l.startswith('【') or BZ.match(l): break
        e+=1
    return ''.join(lines[ln+1:e])
targets=['壬子丙午壬子丙午','乙卯丁亥戊午丙辰','乙卯乙酉庚寅壬午','壬申壬寅壬申辛丑','丁亥丁未乙亥己卯','丙子庚寅辛巳戊子','戊辰庚申己卯戊辰']
for i,l in enumerate(lines):
    lz=re.sub(r'\s+','',l.strip())
    if lz in targets and BZ.match(l.strip()):
        print('════',lz)
        print(case_text(i)[:520])
        print()
