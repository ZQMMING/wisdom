# -*- coding: utf-8 -*-
import sys,re,csv; sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.special_pattern import build_special_patterns, WUHE_HUASHEN
from engines.common.l0_fact_builder import WUXING
DTS=r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines=open(DTS,encoding='utf-8').readlines()
GZ=r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ=re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')
def case_text(ln):
    e=ln+1
    while e<len(lines):
        l=lines[e].strip()
        if l.startswith('八字') or l.startswith('====') or l.startswith('【') or BZ.match(l): break
        e+=1
    return ''.join(lines[ln+1:e])
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
KEYS=('year','month','day','hour')
def gp(s): return {KEYS[i//2]:[s[i],s[i+1]] for i in range(0,8,2)}
NOISE=re.compile(r'从[九七八六五四品]|从副|从藩|从臬|陪从|侍从|随从|跟从|自从|从此|顺从|依从|从事|从政|从军|从教|从来|从化令|从化州|从化縣')
# 明确从格词
CONG_W={'从财':'从财','从妻':'从财','从杀':'从杀','从煞':'从杀','从官':'从官','从儿':'从儿','从食伤':'从儿','从子':'从儿',
        '从势':'从势','从气':'从势','从弱':'从势'}
# 专旺: 格名/从强从旺/方局类象直接词
ZW_DIRECT=['曲直','炎上','稼穡','稼穑','從革','从革','潤下','润下','从强','从旺','一方秀气','得一方','成方','会方','方局',
           '类象','類象','一神','独象','獨象','一行得气','一行得氣','气偏于一','氣偏於一','三朋']
# X局: 仅当X=命主本行才算专旺; X是财官食伤(克泄方)则是从格所从之神成局
ZW_JU={'木局':'木','火局':'火','土局':'土','金局':'金','水局':'水'}
HUA=['化木','化火','化土','化金','化水','化氣','化气','真化']
def day_master_hua(ch):
    """日干与紧邻(月index2/时index6)五合 -> 化神五行字(木火土金水)或None"""
    dm=ch[4]; near=[ch[2],ch[6]]
    wxcn={'木':'木','火':'火','土':'土','金':'金','水':'水'}
    for x in near:
        hs=WUHE_HUASHEN.get((dm,x))
        if hs: return hs
    return None
miss_cong=[]; miss_zw=[]; miss_hua=[]; other_hua=[]; fp=[]
n_cong_hit=n_zw_hit=n_hua_hit=0
for r in rows:
    ch=r['chart'].replace(' ',''); p=gp(ch); f=l0build(p); th=build_tian_he(p,f)
    wp=build_wuxing_power(p,f,th); sp=build_special_patterns(p,f,wp,th)
    txt=case_text(int(r['line']))
    eng_cong=sp['cong_type'] or ''; eng_zw=sp['zhuanwang'] or ''; eng_hua=sp['hua_qi'] or ''
    # 原典从格
    cl_cong=set()
    for w,c in CONG_W.items():
        if w in txt and not NOISE.search(txt[max(0,txt.find(w)-3):txt.find(w)+4]): cl_cong.add(c)
    # 原典专旺同义
    cl_zw=set(w for w in ZW_DIRECT if w in txt)
    for w,wx in ZW_JU.items():
        if w in txt and wx==WUXING[ch[4]]: cl_zw.add(w)
    # 原典化
    cl_hua=set(w for w in HUA if w in txt)
    # 引擎命中判定
    if cl_cong:
        if any(c[:2] in eng_cong or c in eng_cong for c in cl_cong): n_cong_hit+=1
        else: miss_cong.append((ch,r['spectrum'],sorted(cl_cong),eng_cong or '无'))
    if cl_zw:
        zwmap=any(any(k in eng_zw for k in ['曲直','炎上','稼','从革','润下']) for _ in [0])
        if eng_zw: n_zw_hit+=1
        else: miss_zw.append((ch,r['spectrum'],sorted(cl_zw),eng_zw or '无'))
    if cl_hua:
        dh=day_master_hua(ch)
        # 日干紧邻五合且原文化X = 日干化气(应识别); 否则他干/地支/大运合化(task#50)
        ri_hua = dh and any(('化'+dh) in w for w in cl_hua)
        if ri_hua:
            if eng_hua: n_hua_hit+=1
            else: miss_hua.append((ch,r['spectrum'],sorted(cl_hua),'日干化'+dh,eng_hua or '无'))
        else:
            other_hua.append((ch,sorted(cl_hua),'日干'+ch[4]+('紧邻化'+dh if dh else '不紧邻合')))
    # CONFIRMED 疑似误报(原文无任何特殊格词)
    allwords=set(CONG_W.values())|set(ZW_DIRECT)|set(ZW_JU)|set(HUA)|{'弃命','棄命','真从','假从','从象','從象','顺其','順其'}
    conf=[]
    if sp['cong_state']=='CONFIRMED': conf.append(eng_cong)
    if eng_zw:
        zwstate=[x['state'] for x in sp['patterns'] if x['pattern_id']=='ZP-SPECIAL-ZHUANWANG']
        if zwstate and zwstate[0]=='CONFIRMED': conf.append(eng_zw)
    huastate=[x['state'] for x in sp['patterns'] if x['pattern_id']=='ZP-SPECIAL-HUAQI']
    if eng_hua and huastate and huastate[0]=='CONFIRMED': conf.append(eng_hua)
    if conf and not (cl_cong or cl_zw or cl_hua or any(w in txt for w in ['弃命','棄命','真从','假从','从象','從象'])):
        seg=re.sub(r'\s+','',txt)[:90]
        fp.append((ch,r['spectrum'],conf,seg))
print('── 命中: 从格%d例 / 专旺%d例 / 日干化气%d例'%(n_cong_hit,n_zw_hit,n_hua_hit))
print('\n== 漏报从格 %d =='%len(miss_cong))
for z in miss_cong: print(z[0],z[1],z[2],'引擎:',z[3])
print('\n== 漏报专旺(含从强从旺方局类象) %d =='%len(miss_zw))
for z in miss_zw: print(z[0],z[1],z[2],'引擎:',z[3])
print('\n== 漏报日干化气 %d =='%len(miss_hua))
for z in miss_hua: print(z[0],z[1],z[2],z[3],'引擎:',z[4])
print('\n== 他干/地支/大运合化(交task#50,非日干化气格) %d =='%len(other_hua))
for z in other_hua: print(z[0],z[1],z[2])
print('\n== CONFIRMED疑似误报(原文无词,附片段) %d =='%len(fp))
for z in fp: print(z[0],z[1],z[2],'|',z[3])
