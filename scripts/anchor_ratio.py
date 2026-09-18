# -*- coding: utf-8 -*-
import sys,csv,re;sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power,build_spectrum_from_power
lines=open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt',encoding='utf-8').readlines()
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
GZ=r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ_RE=re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')
def case_text(ln):
    e=ln+1
    while e<len(lines):
        l=lines[e].strip()
        if l.startswith('八字：') or l.startswith('====') or l.startswith('【') or BZ_RE.match(l): break
        e+=1
    return ''.join(lines[ln+1:e])
wxmap={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
def ratio_of(p):
    f=build(p);th=build_tian_he(p,f)
    wp=build_wuxing_power(p,f,th);sp=build_spectrum_from_power(wp)
    return sp['daymaster_ratio'],wp
print('=== 日主太旺锚点 ratio ===')
for r in rows:
    ch=r['chart'];text=case_text(int(r['line']));dwx=wxmap[ch[4]]
    for m in re.finditer(r'([金木水火土])太旺',text):
        if m.group(1)==dwx:
            p={'year':list(ch[0:2]),'month':list(ch[2:4]),'day':list(ch[4:6]),'hour':list(ch[6:8])}
            ratio,wp=ratio_of(p)
            print(f'{ch} {dwx} ratio={ratio:.2f}')
print('=== 日主衰极锚点 ratio ===')
for r in rows:
    ch=r['chart'];text=case_text(int(r['line']));dwx=wxmap[ch[4]]
    for m in re.finditer(r'([金木水火土])衰极',text):
        if m.group(1)==dwx:
            p={'year':list(ch[0:2]),'month':list(ch[2:4]),'day':list(ch[4:6]),'hour':list(ch[6:8])}
            ratio,wp=ratio_of(p)
            print(f'{ch} {dwx} ratio={ratio:.2f}')
