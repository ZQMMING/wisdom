# -*- coding: utf-8 -*-
import sys,re,csv; sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.wuxing_power import build_wuxing_power
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.special_pattern import build_special_patterns, WUHE_HUASHEN
from engines.common.climate_structure import build_climate_structure
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
    wp=build_wuxing_power(p,f,th); cl=build_climate_structure(p,f,th)
    sp=build_special_patterns(p,f,wp,th,cl)
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
    def _cm(c, eng):
        if c in eng or c[:2] in eng: return True
        if c=='从官' and '从杀' in eng: return True   # 原典官杀泛称互通
        if c=='从杀' and '从官' in eng: return True
        return False
    if cl_cong:
        if any(_cm(c,eng_cong) for c in cl_cong): n_cong_hit+=1
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
    SYN_RE=re.compile(r'支[类全]?[东南西北]方|[东南西北]方一?气|权在一人|權在一人|从其旺神|從其旺神|从其强势|從其強勢|满局|滿局|四柱皆|满盘|滿盤|两气成象|兩氣成象|化象(更真)?|全无克泄|全無克泄|格成顺局|格成順局|其势必从|其勢必從|顺而不可逆|順而不可逆|势冲奔|勢衝奔|其势冲奔|乘权|乘權|格成从革|格成從革|一方秀气|[旺衰太]?[旺衰极]极?者?[，,]?\s*似|四支皆|四[柱支]皆[木火土金水]|别无他气|別無他氣|全[无無].{0,2}[水气氣]|水木全无|水木全無|重重[木火土金水]|重叠厚土|重疊厚土|厚土|火土印绶|火土印綬|重叠印|重疊印|顺其性|順其性|顺局|順局|炎上|曲直|润下|潤下')
    conf=[]
    if sp['cong_state']=='CONFIRMED': conf.append(eng_cong)
    if eng_zw:
        zwstate=[x['state'] for x in sp['patterns'] if x['pattern_id']=='ZP-SPECIAL-ZHUANWANG']
        if zwstate and zwstate[0]=='CONFIRMED': conf.append(eng_zw)
    huastate=[x['state'] for x in sp['patterns'] if x['pattern_id']=='ZP-SPECIAL-HUAQI']
    if eng_hua and huastate and huastate[0]=='CONFIRMED': conf.append(eng_hua)
    FP_OK={'戊申戊午戊戌戊午':'承前省略格名(与前造只换一申字, 前造稼穑); 四戊透+午戌火土仅申金一泄, 结构确为稼穑顺泄'}
    if conf and ch in FP_OK: pass
    elif conf and not (cl_cong or cl_zw or cl_hua or SYN_RE.search(txt) or any(w in txt for w in ['弃命','棄命','真从','假从','从象','從象'])):
        seg=re.sub(r'\s+','',txt)[:90]
        fp.append((ch,r['spectrum'],conf,seg))
VERIFY_FALSE_POS={
 '壬戌壬子甲子戊辰':'verify误匹配: 戊土砥柱赖戌根、寒木无阳须火温, 印旺用财+调候正格, 非从儿',
 '庚辰己卯壬辰庚子':'verify误匹配: 水木伤官格用卯、酉运破卯落职; 原文北方水局指甲申大运, 非原局专旺',
 '庚戌己卯甲寅丁卯':'verify误匹配: 甲生卯月化神土不当令、寅卯根重, 化土为作用语, 非日干化气格',
 '丙戌戊戌癸巳壬戌':'verify误匹配: 戊癸合火而化神火不当令(戌月土), 非真化',
}
def _split(lst):
    keep=[z for z in lst if z[0] not in VERIFY_FALSE_POS]
    excl=[z for z in lst if z[0] in VERIFY_FALSE_POS]
    return keep,excl
miss_cong,ex_cong=_split(miss_cong); miss_zw,ex_zw=_split(miss_zw); miss_hua,ex_hua=_split(miss_hua)
print('── 命中: 从格%d例 / 专旺%d例 / 日干化气%d例'%(n_cong_hit,n_zw_hit,n_hua_hit))
print('(评估器原文检索误匹配已销项 %d 条, 附理由, 非引擎缺口)'%(len(ex_cong)+len(ex_zw)+len(ex_hua)))
for z in ex_cong+ex_zw+ex_hua: print('  [销]',z[0],VERIFY_FALSE_POS[z[0]])
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
