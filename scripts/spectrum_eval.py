# -*- coding: utf-8 -*-
"""日主旺衰七档 vs DTS原文断言 命中率评估.
严格紧邻主语+语境过滤; 按词统计 原文出现数/排除数/实际对比数/命中数, 不靠exclude制造虚高."""
import re,sys,csv;sys.path.insert(0,'.')
DTS=r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines=open(DTS,encoding='utf-8').readlines()
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
WX={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
TERMS=[
 ('旺之极',{'旺极','太旺'},'旺极'),('旺极',{'旺极','太旺'},'旺极'),('极旺',{'旺极','太旺'},'旺极'),('强旺极',{'旺极','太旺'},'旺极'),
 ('太旺',{'太旺','旺极'},'太旺'),('旺甚',{'太旺','旺极','旺'},'太旺'),
 ('身旺',{'旺','太旺','旺极'},'身旺'),('日主旺',{'旺','太旺','旺极'},'身旺'),('日干旺',{'旺','太旺','旺极'},'身旺'),('日元旺',{'旺','太旺','旺极'},'身旺'),
 ('身强',{'旺','太旺','旺极'},'身强'),('日主强',{'旺','太旺','旺极'},'身强'),
 ('衰之极',{'衰极','太衰'},'衰极'),('衰极',{'衰极','太衰'},'衰极'),('弱极',{'衰极','太衰'},'衰极'),('极弱',{'衰极','太衰'},'衰极'),('虚弱极',{'衰极','太衰'},'衰极'),
 ('太弱',{'太衰','衰极'},'太衰'),('过弱',{'太衰','衰极'},'太衰'),('太衰',{'太衰','衰极'},'太衰'),('弱甚',{'太衰','衰极'},'太衰'),
 ('身弱',{'衰','太衰','衰极'},'身弱'),('日主弱',{'衰','太衰','衰极'},'身弱'),('日干弱',{'衰','太衰','衰极'},'身弱'),('日元弱',{'衰','太衰','衰极'},'身弱'),
 ('身衰',{'衰','太衰','衰极'},'身弱'),('日主衰',{'衰','太衰','衰极'},'身弱'),
 # ---- 广义日主力量断语(无身字但指日主总评) ----
 ('身轻',{'衰','太衰','衰极'},'身弱'),('虚弱',{'衰','太衰','衰极'},'身弱'),('气弱',{'衰','太衰','衰极'},'身弱'),
 ('根浅',{'衰','太衰','衰极'},'身弱'),('衰弱',{'衰','太衰','衰极'},'身弱'),('柔弱',{'衰','太衰','衰极'},'身弱'),
 ('泄气太过',{'衰','太衰','衰极'},'身弱'),('泄身太过',{'衰','太衰','衰极'},'身弱'),('泄气太重',{'衰','太衰','衰极'},'身弱'),
 ('身弱不胜',{'衰','太衰','衰极'},'身弱'),('身弱难任',{'衰','太衰','衰极'},'身弱'),
 ('根深',{'旺','太旺','旺极'},'身旺'),('根重',{'旺','太旺','旺极'},'身旺'),('气足',{'旺','太旺','旺极'},'身旺'),
 ('刚健',{'旺','太旺','旺极'},'身旺'),('身轻',{'衰','太衰','衰极'},'身弱'),
 # ---- 结构成语断言(直接断言日主方向; 繁简双体) ----
 ('財多身弱',{'衰','太衰','衰极'},'财多身弱'),('财多身弱',{'衰','太衰','衰极'},'财多身弱'),
 ('殺重身輕',{'衰','太衰','衰极'},'杀重身轻'),('杀重身轻',{'衰','太衰','衰极'},'杀重身轻'),('煞重身輕',{'衰','太衰','衰极'},'杀重身轻'),
 ('身弱難任',{'衰','太衰','衰极'},'身弱难任'),('身弱难任',{'衰','太衰','衰极'},'身弱难任'),
 ('不勝財官',{'衰','太衰','衰极'},'身弱难任'),('不胜财官',{'衰','太衰','衰极'},'身弱难任'),
 ('不任財官',{'衰','太衰','衰极'},'身弱难任'),('不任财官',{'衰','太衰','衰极'},'身弱难任'),
 ('身弱不勝',{'衰','太衰','衰极'},'身弱难任'),('身弱不胜',{'衰','太衰','衰极'},'身弱难任'),
 ('身強殺淺',{'旺','太旺','旺极'},'身强杀浅'),('身强杀浅',{'旺','太旺','旺极'},'身强杀浅'),
 ('身旺任',{'旺','太旺','旺极'},'身旺任财官'),('能任財',{'旺','太旺','旺极'},'身旺任财官'),('能任财',{'旺','太旺','旺极'},'身旺任财官'),
 ('身旺勝',{'旺','太旺','旺极'},'身旺任财官'),('身旺胜',{'旺','太旺','旺极'},'身旺任财官'),
]
NEG=['不旺','不弱','非旺','非弱','未旺','未弱','不致旺','不致弱','不论身强弱','何旺','何弱','岂','焉能','安能','不能言旺','似旺','似弱','假旺','假弱','不可以旺','不可以弱','非身','非论','毋作','勿作']
YUN=re.compile(r'大运|流年|岁运|行运|运中|运里|运入|运至|运逢|交入|一交|行入|初年|晚年|少时|晚运|早年|此后|将来|变旺|变弱')
QUOTE=re.compile(r'不可损|不可益|即余之|此两句|太旺太衰|经云|书云|语云|岂不知|旺之极者不|衰之极者不|以上.{0,4}造|五行极[旺衰]|极旺极衰')
GEN=re.compile(r'(大凡|凡命|凡|假使|假如|设使|盖|所谓须要|须要|必要|必先|俗以|人皆|皆曰|前造|前之|何以|何为|安在|试看)')
TONGDANG=re.compile(r'(比肩|劫财|劫刃|阳刃|比劫|刃|禄)[^，。；,;]{0,3}$')
TASHEN=re.compile(r'(伤官|食神|官星|官杀|七杀|财官|财星|印绶|印星|七[杀煞]|财|官|杀|煞|印|食|伤)[^，。；,;]{0,3}$')
SELF_NEAR=re.compile(r'(日主|日干|日元|元神|命主|我身|元身|此造|身)\s*[之]?\s*$')
DIZHI_NEAR=re.compile(r'地\s*[旺衰极][^，。；,;]{0,2}$|地\s*$')
JUNCHEN=re.compile(r'臣盛君|臣衰君|臣顺君|不能和臣|臣心|君安|君象|臣象|臣盛|君衰极|君盛')
def subject_ok(before,after,dm):
    ctx=before+after
    dwx=WX[dm]; tight=before[-4:]
    if any(n in ctx for n in NEG): return False,'neg'
    if YUN.search(ctx): return False,'yun'
    if QUOTE.search(before): return False,'quote'
    if JUNCHEN.search(ctx): return False,'junchen'
    if ('身旺者' in ctx) and ('身弱者' in ctx): return False,'gen2'
    if GEN.search(tight.strip()): return False,'gen'
    if DIZHI_NEAR.search(before[-6:]): return False,'dizhi'
    if SELF_NEAR.search(tight): return True,'self'
    if TONGDANG.search(tight): return True,'tongdang'
    if TASHEN.search(tight): return False,'tashen'
    gans=re.findall(r'[甲乙丙丁戊己庚辛壬癸]',tight)
    if gans: return (gans[-1]==dm),'gan'
    wxs=re.findall(r'[金木水火土]',tight)
    if wxs: return (wxs[-1]==dwx),'wx'
    if re.search(r'日主|日干|日元|元神|命主|我身|此造|身[旺衰弱极]',before): return True,'self2'
    return True,'default'

stats={}; reasons={}; raw={}; mism=[]; compared=[]; excluded={}
for r in rows:
    ch=r['chart']; dm=ch[4]; spec=r.get('spectrum','')
    if spec in ('ERR','',None): continue
    text=case_text(int(r['line']))
    seen=set()
    for term,want,lvl in TERMS:
        for m in re.finditer(re.escape(term),text):
            before=text[max(0,m.start()-14):m.start()]
            after=text[m.start():m.start()+8]
            ctx=before+after
            ok,why=subject_ok(before,after,dm)
            if not ok:
                reasons.setdefault(lvl,{}); reasons[lvl][why]=reasons[lvl].get(why,0)+1
                excluded.setdefault(why,[]).append((ch,lvl,term,ctx.replace('\n','')))
                continue
            if lvl in seen: break
            seen.add(lvl)
            hit=spec in want
            stats.setdefault(lvl,[0,0]); stats[lvl][1]+=1
            compared.append((ch,lvl,spec,term,ctx.replace('\n','')))
            if hit: stats[lvl][0]+=1
            else: mism.append((lvl,ch,spec,r.get('ratio',''),ctx.replace('\n','')))
            break
# raw 计数(每词在原文案例中出现, 粗计次数)
print('=== 七档 vs 原文日主旺衰断言 (紧邻主语过滤) ===')
TH=tot_n=0
for k in ['旺极','太旺','身旺','身强','衰极','太衰','身弱','财多身弱','杀重身轻','身弱难任','身强杀浅','身旺任财官']:
    if k in stats:
        h,n=stats[k]; TH+=h; tot_n+=n
        ex=sum(reasons.get(k,{}).values())
        print(f'{k:4s}: 命中 {h}/{n}  (原文另排除他神/论述/大运 {ex} 例: {reasons.get(k,{})}) = {h/n*100:.0f}%')
print(f'干净断言合计: {TH}/{tot_n} = {TH/tot_n*100:.1f}%')
print('\n=== 仍不匹配(干净主语) ===')
for x in mism:
    print(f'[{x[0]}] {x[1]} 引擎={x[2]}(r{x[3]}) | {x[4]}')

import sys as _s
if '--detail' in _s.argv:
    print('\n=== 计入对比的全部干净断言明细 ===')
    for ch,lvl,spec,term,ctx in sorted(compared,key=lambda z:z[1]):
        print(f'[{lvl}|{term}] {ch} 引擎={spec} | {ctx}')
    print('\n=== 被排除案例抽查(每原因最多5条, 人工核是否真他神/论述) ===')
    for why,lst in excluded.items():
        print(f'--- {why} ({len(lst)}条) ---')
        for ch,lvl,term,ctx in lst[:5]:
            print(f'   {ch} [{lvl}|{term}] {ctx}')
