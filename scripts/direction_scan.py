# -*- coding: utf-8 -*-
"""宽口径日主旺衰方向扫描: 从513全量中初筛'原文方向 vs 引擎七档方向'疑似相反例.
只做强方向词(身旺身弱/成语/根深根浅/任不任), 不含得令有根等弱信号(得时可不旺)."""
import re,sys,csv
sys.path.insert(0,'.')
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
WANG=['旺之极','旺极','极旺','極旺','强旺','強旺','太旺','旺甚','身旺','身强','身強','日主旺','日干旺','日元旺','健旺','根深','根重','气足','氣足','刚健','剛健','身旺任','能任','胜财','勝財','身强杀浅','身強殺淺','旺相','發越','发越']
SHUAI=['衰之极','衰极','弱极','弱極','极弱','極弱','虚弱极','虛弱極','太弱','太衰','过弱','過弱','弱甚','身弱','身衰','日主弱','日干弱','日元弱','虚弱','虛弱','身轻','身輕','气弱','氣弱','根浅','根淺','根轻','根輕','柔弱','泄气太过','洩氣太過','泄身太过','洩身太過','泄气太重','洩氣太重','财多身弱','財多身弱','杀重身轻','殺重身輕','煞重身輕','身弱难任','身弱難任','不胜财官','不勝財官','不任财官','不任財官','身弱不胜','身弱不勝','孤弱','衰弱','气怯','氣怯','无力','無力']
NEG=['不旺','不弱','非旺','非弱','未旺','未弱','不致旺','不致弱','不论身强弱','不論身強弱','何旺','何弱','岂','豈','焉能','安能','不能言旺','似旺','似弱','假旺','假弱','不可以旺','不可以弱','非身','非论','毋作','勿作']
YUN=re.compile(r'大运|流年|岁运|行运|运中|运里|运入|运至|运逢|交入|一交|行入|初年|晚年|少时|晚运|早年|此后|將來|将来|变旺|變旺|变弱|變弱|運走|运走')
QUOTE=re.compile(r'不可损|不可益|即余之|此两句|太旺太衰|经云|經云|书云|書云|语云|語云|岂不知|豈不知|旺之极者不|衰之极者不|以上.{0,4}造|五行极[旺衰]|極旺極衰')
GEN=re.compile(r'(大凡|凡命|凡|假使|假如|设使|蓋|盖|所谓须要|所謂須要|须要|須要|必要|必先|俗以|人皆|皆曰|前造|前之|何以|何為|何为|安在|试看|試看)')
TONGDANG=re.compile(r'(比肩|劫财|劫財|劫刃|阳刃|陽刃|比劫|刃|禄|祿)[^，。；,;]{0,3}$')
TASHEN=re.compile(r'(伤官|傷官|食神|官星|官杀|官殺|七杀|七殺|财官|財官|财星|財星|印绶|印綬|印星|财|財|官|杀|殺|煞|印|食|伤|傷)[^，。；,;]{0,3}$')
SELF_NEAR=re.compile(r'(日主|日干|日元|元神|命主|我身|元身|此造|身)\s*[之]?\s*$')
DIZHI_NEAR=re.compile(r'地\s*[旺衰极][^，。；,;]{0,2}$|地\s*$')
JUNCHEN=re.compile(r'臣盛君|臣衰君|臣顺君|臣順君|不能和臣|臣心|君安|君象|臣象|臣盛|君衰极|君衰極|君盛')
def subj_ok(before,after,dm):
    ctx=before+after; dwx=WX[dm]; tight=before[-4:]
    if any(n in ctx for n in NEG): return False
    if re.search(r'似乎[^，。；,;]{0,2}(旺|强|強)|好像[^，。；,;]{0,2}旺',ctx): return False
    if YUN.search(ctx): return False
    if QUOTE.search(before): return False
    if JUNCHEN.search(ctx): return False
    if ('身旺者' in ctx) and ('身弱者' in ctx): return False
    if GEN.search(tight.strip()): return False
    if DIZHI_NEAR.search(before[-6:]): return False
    if SELF_NEAR.search(tight): return True
    if TONGDANG.search(tight): return True
    if TASHEN.search(tight): return False
    gans=re.findall(r'[甲乙丙丁戊己庚辛壬癸]',tight)
    if gans: return gans[-1]==dm
    wxs=re.findall(r'[金木水火土]',tight)
    if wxs: return wxs[-1]==dwx
    if re.search(r'日主|日干|日元|元神|命主|我身|此造|身[旺衰弱极]',before): return True
    return True
WANG_SET={'旺极','太旺','旺'}; SHUAI_SET={'衰极','太衰','衰'}
sus=[]
for r in rows:
    ch=r['chart']; dm=ch[4]; spec=r.get('spectrum','')
    if spec in ('ERR','',None): continue
    text=case_text(int(r['line']))
    w_hits=[]; s_hits=[]
    for term in WANG:
        for m in re.finditer(re.escape(term),text):
            b=text[max(0,m.start()-14):m.start()]; a=text[m.start():m.start()+8]
            if subj_ok(b,a,dm): w_hits.append((term,(b+a).replace('\n',''))); break
    for term in SHUAI:
        for m in re.finditer(re.escape(term),text):
            b=text[max(0,m.start()-14):m.start()]; a=text[m.start():m.start()+8]
            if subj_ok(b,a,dm): s_hits.append((term,(b+a).replace('\n',''))); break
    eng='旺' if spec in WANG_SET else ('衰' if spec in SHUAI_SET else '中')
    nw,ns=len(w_hits),len(s_hits)
    flag=None
    if nw>=1 and ns==0 and eng=='衰': flag='原文旺向/引擎衰'
    elif ns>=1 and nw==0 and eng=='旺': flag='原文衰向/引擎旺'
    elif nw-ns>=2 and eng=='衰': flag='原文偏旺/引擎衰'
    elif ns-nw>=2 and eng=='旺': flag='原文偏衰/引擎旺'
    elif eng=='中' and nw>=1 and ns==0: flag='引擎中和/原文旺向'
    elif eng=='中' and ns>=1 and nw==0: flag='引擎中和/原文衰向'
    if flag:
        sus.append((flag,ch,spec,r.get('ratio',''),w_hits[:3],s_hits[:3]))
print(f'疑似方向相反: {len(sus)} 例\n')
for flag,ch,spec,ratio,wh,sh in sus:
    print(f'【{flag}】{ch} 引擎={spec}(r{ratio})')
    for t,c in wh: print(f'   旺向[{t}] {c}')
    for t,c in sh: print(f'   衰向[{t}] {c}')
    print()
