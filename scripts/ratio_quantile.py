# -*- coding: utf-8 -*-
import sys,csv,re,statistics;sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_from_power

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

ratios=[]
recs=[]
for r in rows:
    ch=r['chart']
    p={'year':list(ch[0:2]),'month':list(ch[2:4]),'day':list(ch[4:6]),'hour':list(ch[6:8])}
    try:
        f=build(p);th=build_tian_he(p,f)
        wp=build_wuxing_power(p,f,th);sp=build_spectrum_from_power(wp)
    except Exception: continue
    ratios.append(sp['daymaster_ratio'])
    recs.append((ch,sp['daymaster_ratio'],case_text(int(r['line']))))

ratios.sort()
n=len(ratios)
def q(p): return ratios[min(n-1,int(n*p))]
print(f'n={n} min={ratios[0]:.2f} max={ratios[-1]:.2f} 中位={statistics.median(ratios):.2f}')
for p in [0.05,0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90,0.95]:
    print(f'p{int(p*100):02d}={q(p):.2f}',end='  ')
print()
# 日主五行字 -> 五行, 识别"X太旺者似Y"主语=日主
wxmap={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
print('\n=== 日主太旺(X太旺者似/太旺者似, X=日主五行) ===')
for ch,ratio,text in recs:
    dwx=wxmap[ch[4]]
    for m in re.finditer(r'([金木水火土])太旺',text):
        if m.group(1)==dwx:
            print(f'{ch} 日主{dwx} ratio={ratio:.2f}  ...{text[max(0,m.start()-8):m.start()+12]}...')
print('\n=== 衰极(原文"衰极") ===')
c=0
for ch,ratio,text in recs:
    if '衰极' in text:
        i=text.find('衰极');print(f'{ch} 日主{wxmap[ch[4]]} ratio={ratio:.2f} ...{text[max(0,i-10):i+6]}...');c+=1
print(f'衰极共{c}')
