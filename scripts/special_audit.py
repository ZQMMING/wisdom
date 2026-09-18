# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.special_pattern import build_special_patterns
import csv
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
KEYS=('year','month','day','hour')
def gp(s):
    return {KEYS[i//2]:[s[i],s[i+1]] for i in range(0,8,2)}
from collections import Counter
cc=Counter(); zwc=Counter(); huac=Counter(); mumie=[]
recs=[]
for r in rows:
    p=gp(r['chart'].replace(' ','')); f=l0build(p); th=build_tian_he(p,f)
    wp=build_wuxing_power(p,f,th); sp=build_special_patterns(p,f,wp,th)
    ct=sp['cong_type']; zw=sp['zhuanwang']; hq=sp['hua_qi']; mm=sp['mu_mie']
    if ct: cc[ct]+=1
    if zw: zwc[zw]+=1
    if hq: huac[hq]+=1
    if mm: mumie.append(r['chart'].replace(' ',''))
    recs.append((r['chart'].replace(' ',''),ct,zw,hq,mm,r['spectrum']))
print('从格分布:',dict(cc),'合计',sum(cc.values()))
print('专旺分布:',dict(zwc),'合计',sum(zwc.values()))
print('化气分布:',dict(huac),'合计',sum(huac.values()))
print('母多灭子候选:',len(mumie),mumie[:20])
anchors=['丙寅庚寅壬午乙巳','己卯丁卯壬午癸卯','戊辰壬戌甲辰己巳','戊戌丙辰辛丑戊戌','己亥丙子乙丑壬午',
         '甲午丁丑甲午丙寅','丁卯壬寅癸卯丙辰','癸亥乙卯己未丁卯','庚戌甲申甲戌乙丑','己巳辛未丙午丁酉','辛卯辛卯辛卯辛卯']
print('--- 锚点 ---')
for a in anchors:
    for z in recs:
        if z[0]==a: print(a,z[5],'| 从:',z[1],'专旺:',z[2],'化:',z[3],'母灭:',z[4])
