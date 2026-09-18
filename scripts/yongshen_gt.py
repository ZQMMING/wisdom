# -*- coding: utf-8 -*-
"""DTS 原局主用神高精度 ground truth: 只收作者定论强信号, 排除讨论/否定/破格句。
输出每例主用神五行集 + 原句, 作为用神引擎命中率评估集。"""
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
TOK=r'([甲乙丙丁戊己庚辛壬癸]|'+WUX+r'|'+SS_PAT+r')'
# 定论强信号(作者明确取用)
STRONG=[
 re.compile(r'用'+TOK+r'明矣'),
 re.compile(r'(?:必|专|須|须|宜|重|当)用'+TOK),
 re.compile(r'取'+TOK+r'[^，。；,;]{0,8}为用'),
 re.compile(r'为用[^，。；,;]{0,4}'+TOK),
 re.compile(r'身(?:旺|强|強|衰|弱)用'+TOK),
 re.compile(r'最喜'+TOK), re.compile(r'所喜(?:者|在|得)?'+TOK),
 re.compile(r'顺其(['+WUX+r'])之?性'),
 re.compile(r'必[要须]'+TOK),
 re.compile(r'用'+TOK+r'(?:滋杀|滋殺|制杀|制殺|化杀|化殺|泄秀|生身|扶身|培之|润之|潤之|照暖|疏土|劈|涤|滌)'),
 re.compile(r'取'+TOK+r'(?:伤官|食神|秀气)[^，。；,;]{0,6}为用'),
 re.compile(r'以'+TOK+r'为用'),
 re.compile(r'用神(?:在|是)'+TOK),
]
# 否定/讨论/破格(整句命中则弃)
BAN=re.compile(r'不足为用|無所著落|无所着落|用神無所|用神无所|用之則|用之则|若用|雖用|虽用|可用.{0,3}乎|豈用|岂用|何用|何必用|不可以用|不堪为用|何能为用|安能为用|假用|误用|谬')
def sent_of(text,pos):
    st=max(text.rfind('。',0,pos),text.rfind('；',0,pos),text.rfind(';',0,pos))
    ec=[text.find(c,pos) for c in ('。','；',';') if text.find(c,pos)>=0]
    return text[st+1:min(ec) if ec else len(text)]
def norm(tok,dm):
    return WX.get(tok) if tok in WX else (tok if tok in WUX else ss_wx(tok,dm))
def extract(text,dm):
    out=[]
    for pat in STRONG:
        for m in re.finditer(pat,text):
            s=sent_of(text,m.start())
            if BAN.search(s): continue
            if re.search(r'俗|庸师|人皆谓|假使|假如|设使',s): continue
            tok=m.group(1); w=norm(tok,dm)
            if w: out.append((w,tok,s.strip()[:74]))
    # 去重保序
    seen=set(); uniq=[]
    for w,t,s in out:
        if w not in seen: seen.add(w); uniq.append((w,t,s))
    return uniq
n=0; multi=0; recs=[]
for r in rows:
    dm=r['chart'][4]; text=ds.case_text(int(r['line']))
    f=extract(text,dm)
    if f:
        n+=1; recs.append((r['chart'],r['spectrum'],r.get('cong',''),r.get('zhuanwang',''),f))
        if len(f)>1: multi+=1
print(f'高精度用神断言例: {n}/{len(rows)} (其中多候选 {multi})')
for ch,sp,cong,zw,f in recs:
    tag=('专旺:'+zw) if zw else (('从:'+cong) if cong else sp)
    print(f"{ch} [{tag}] 用神={[w for w,_,_ in f]}")
    for w,t,s in f[:2]: print('    ',s)
