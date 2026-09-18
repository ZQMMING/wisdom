# -*- coding: utf-8 -*-
"""DTS 原局主用神 ground truth: 收作者定论取用信号, 排除讨论/否定/破格/泛论句。
STRONG=高精度强信号(默认); wide=True 追加 WIDE_PAT 放宽召回(用于防过拟合的大样本整体核对)。
输出每例主用神五行集 + 原句。"""
import re, sys, csv
sys.path.insert(0,'scripts')
import direction_scan as ds
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
WX={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
WUX='木火土金水'; GAN='甲乙丙丁戊己庚辛壬癸'
SHENG={'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
SS_PAT=r'(?:食神|伤官|食伤|正财|偏财|正官|偏官|七杀|七殺|官杀|官殺|官星|财星|印绶|印星|枭神|比肩|劫财|比劫|财|官|杀|殺|煞|印|食|伤|儿)'
def ss_wx(tok,dm):
    w=WX[dm]
    if tok in ('比肩','劫财','比劫','刃','禄'): return w
    if tok in ('食神','伤官','食伤','伤','食','儿'): return SHENG[w]
    if tok in ('财','正财','偏财','财星'): return KE[w]
    if tok in ('官','杀','官杀','官星','七杀','煞','正官','偏官'): return [x for x in WUX if KE[x]==w][0]
    if tok in ('印','印绶','印星','正印','偏印','枭','枭神'): return [x for x in WUX if SHENG[x]==w][0]
    return None
TOK=r'([甲乙丙丁戊己庚辛壬癸]['+WUX+r']?|'+WUX+r'|'+SS_PAT+r')'
STRONG=[
 re.compile(r'用'+TOK+r'明矣'),
 re.compile(r'(?:必|专|專|須|须|宜|重|当|當)用'+TOK),
 re.compile(r'取'+TOK+r'[^，。；,;]{0,8}为用'),
 re.compile(r'为用[^，。；,;]{0,4}'+TOK),
 re.compile(r'身(?:旺|强|強|衰|弱)用'+TOK),
 re.compile(r'最喜'+TOK), re.compile(r'所喜(?:者|在|得)?'+TOK),
 re.compile(r'顺其(['+WUX+r'])之?性'),
 re.compile(r'必[要须須]'+TOK),
 re.compile(r'用'+TOK+r'(?:滋杀|滋殺|制杀|制殺|化杀|化殺|泄秀|生身|扶身|培之|润之|潤之|照暖|疏土|劈|涤|滌)'),
 re.compile(r'取'+TOK+r'(?:伤官|食神|秀气)[^，。；,;]{0,6}为用'),
 re.compile(r'以'+TOK+r'为用'),
 re.compile(r'用神(?:在|是)'+TOK),
 re.compile(r'喜'+TOK),
 re.compile(r'(?:宜|要|当取|當取|专赖|專賴|全赖|全賴|端赖|端賴|必藉|必借|专恃|專恃|所恃|须赖|須賴|全恃|恃|赖|賴|需)'+TOK),
 re.compile(r'以'+TOK+r'(?:为命|為命|为根|為根|为主|為主|为先|為先|为急|為急|为美|為美|为妙|為妙|制之|化之|泄之|生之)'),
 re.compile(r'取'+TOK+r'(?:为命|為命|为根|為根|为主|為主|为急|為急|为美|為美|为妙|為妙)'),
]
# 宽口径追加(仍是作者定论取用, 措辞更宽; 病药"以X制Y"取X为药)
WIDE_PAT=[
 re.compile(r'以'+TOK+r'为用神'),
 re.compile(r'用神(?:惟|唯|在|取|宜|当|當|须|須|专|專)'+TOK),
 re.compile(r'(?:专|專|惟|唯)喜'+TOK),
 re.compile(r'喜(?:其|得|用)'+TOK), re.compile(r'喜用'+TOK),
 re.compile(r'(?:宜用|须用|須用|当用|當用|重用|取用在?|用在)'+TOK),
 re.compile(r'(?:当|當|须|須)以'+TOK),
 re.compile(r'不可无'+TOK), re.compile(r'不可無'+TOK),
 re.compile(r'(?:岂|豈)可无?'+TOK),
 re.compile(r'全(?:赖|賴|恃|藉|借)'+TOK),
 re.compile(r'以'+TOK+r'(?:制|化|生|扶|泄|克|培|补|補|润|潤|暖|照|疏|劈)'),
 re.compile(r'取'+TOK+r'(?:为|為|以|去|制|化|生)'),
 re.compile(r'用'+TOK+r'(?:为|為|以|生|制|化)'),
 re.compile(r'(?:得|逢)'+TOK+r'(?:而|则|則|为|為|方)'),
 re.compile(r'惟'+TOK+r'(?:为|為|可|足)'),
 re.compile(r'妙在'+TOK), re.compile(r'全在'+TOK+r'[，。；,;]?'),
 re.compile(r'(?:不如|不若)[用取]?'+TOK),
 re.compile(r'自[应應宜]'+TOK),
 re.compile(r'以'+TOK+r'为君'),
 re.compile(r'药[在惟]'+TOK), re.compile(r'去病[在须須]'+TOK),
 re.compile(r'喜[见見逢得]'+TOK),
 re.compile(r'宜[见見逢得]'+TOK),
 re.compile(r'以'+TOK+r'济[之]?'), re.compile(r'济[之以]?'+TOK),
 re.compile(r'急[于於在]'+TOK),
 re.compile(r'要[在惟]'+TOK),
 re.compile(r'得'+TOK+r'[^，。；,;]{0,5}(?:发[福达達]|有[功济]|为[功济]|有功)'),
 re.compile(r'惟[赖賴藉恃喜]'+TOK),
 re.compile(r'专[用取於于]'+TOK),
 re.compile(r'首[取在]'+TOK),
]
BAN=re.compile(r'不足为用|無所著落|无所着落|用神無所|用神无所|用之則|用之则|若用|雖用|虽用|可用.{0,3}乎|豈用|岂用|何用|何必用|不可以用|不堪为用|何能为用|安能为用|假用|误用|谬|不喜|非所喜|何喜|岂喜|豈喜|不宜|不可用|何赖|赖何|岂赖|毋用|勿用|无用之|非取以为用|非所以|何以又取|反取|无凭|無憑|不足凭|書曰|书曰|書云|书云|二曰|一曰|何必定|岂所以|豈所以|非用神|格也|$格|此不易之法|不易之法|旺则宜|衰则宜|不易之論|不易之论|何劳|何勞|何必|安用|乌用|烏用|岂须|豈須|何须|何須|置之度外|置諸度外|贪合忘|貪合忘|合而化印|合化印|暗化财|暗化財|合而化')
def sent_of(text,pos):
    st=max(text.rfind('。',0,pos),text.rfind('；',0,pos),text.rfind(';',0,pos))
    ec=[text.find(c,pos) for c in ('。','；',';') if text.find(c,pos)>=0]
    return text[st+1:min(ec) if ec else len(text)]
def norm(tok,dm):
    if tok and tok[0] in WX: return WX[tok[0]]
    return tok if tok in WUX else ss_wx(tok,dm)
def extract(text,dm,wide=False):
    out=[]
    pats=STRONG+(WIDE_PAT if wide else [])
    for pat in pats:
        for m in re.finditer(pat,text):
            s=sent_of(text,m.start())
            if BAN.search(s): continue
            if re.search(r'俗|庸师|庸師|人皆谓|人皆謂|假使|假如|设使|設使|尝谓|嘗謂|或谓|或謂|古以|古人',s): continue
            tok=m.group(1); w=norm(tok,dm)
            if w: out.append((w,tok,s.strip()[:74]))
    seen=set(); uniq=[]
    for w,t,s in out:
        if w not in seen: seen.add(w); uniq.append((w,t,s))
    return uniq
if __name__=='__main__':
    wide=('--wide' in sys.argv)
    n=0; multi=0; recs=[]
    for r in rows:
        dm=r['chart'][4]; text=ds.case_text(int(r['line']))
        f=extract(text,dm,wide)
        if f:
            n+=1; recs.append((r['chart'],r['spectrum'],r.get('cong',''),r.get('zhuanwang',''),f))
            if len(f)>1: multi+=1
    print(f'{"宽口径" if wide else "高精度"}用神断言例: {n}/{len(rows)} (多候选 {multi})')
