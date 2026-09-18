# -*- coding: utf-8 -*-
"""全量断言对齐统计(身旺衰方向 + 日主有根无根): 复用 direction_scan 词表/主语/否定/分层/REVIEWED。
根断言严格区分: 日主根 vs 财官印食伤他神根 vs 岁运根 vs 否定式; 从格日主"无根"按分层一致(事实层微根/格局判从)。"""
import re, sys, csv
sys.path.insert(0, 'scripts')
import direction_scan as ds
rows = list(csv.DictReader(open('scripts/dts_513_output.csv', encoding='utf-8-sig')))

GEN_YOU = ['根深','根重','根坚','通根','得地','有根','本根','根气','坐禄','支坐禄','禄旺','通根身库','得根']
GEN_WU  = ['无根','根浅','根轻','根拔','根枯','根绝','全无根','根气全无','根不固']
SELF_RE = re.compile(r'日主|日元|日干|元神|我身|此造|自身')
# 他神主语: 具体天干+五行(甲木/壬水/丙火)、五行二连(木火/金水/虚火)、十神(财官印食伤杀/弱神)
TA_GAN_RE = re.compile(r'[甲乙丙丁戊己庚辛壬癸][木火土金水]')
TA_WX2_RE = re.compile(r'[木火土金水]{2}|虚[木火土金水]')
TA_SS_RE = re.compile(r'财星|官星|印星|食神|伤官|七杀|七殺|官煞|官杀|弱神|旺财|财|官|煞|杀|印|食|伤')
NEG_ROOT = re.compile(r'不为|不是|并非|非真|岂|焉|那|何|毋|勿|不谓|未为|不失')

def sent_of(text, pos):
    st=max(text.rfind('。',0,pos),text.rfind('；',0,pos),text.rfind(';',0,pos))
    ec=[text.find(c,pos) for c in ('。','；',';') if text.find(c,pos)>=0]
    return text[st+1:min(ec) if ec else len(text)]

def gen_hits(text, terms, dm, is_cong):
    """日主根命中数; 紧邻主语(根词前6字)是他神(财官印食伤/天干五行/非日干裸干/五行二连)即他神;
    句首发语词'此造'不代表根词归日主, 以紧邻主语为准。岁运/否定式排除。"""
    mine=0; excl=[]
    def gan_other(seg):
        return [g for g in re.findall(r'[甲乙丙丁戊己庚辛壬癸]', seg) if g != dm]
    for term in terms:
        for m in re.finditer(re.escape(term), text):
            st=max(text.rfind('。',0,m.start()),text.rfind('；',0,m.start()),text.rfind(';',0,m.start()))
            base=st+1
            s=text[base: (min([text.find(c,m.start()) for c in ('。','；',';') if text.find(c,m.start())>=0]) if any(text.find(c,m.start())>=0 for c in ('。','；',';')) else len(text))]
            pre=text[base:m.start()]; near=pre[-6:]
            after=text[m.end():m.end()+4]
            if ds.YUN.search(s):  excl.append((term,'岁运',s.strip()[:60])); break
            if NEG_ROOT.search(pre[-6:]):  excl.append((term,'否定式',s.strip()[:60])); break
            # 主语后置(紧邻): "无根之土/无根土"、"无根之财" -> 他神(五行非日主)
            _pw=re.match(r'\s*之?([木火土金水])', after)
            if _pw and _pw.group(1) != ds.WX[dm]:
                excl.append((term,'他神后置',s.strip()[:60])); break
            if re.match(r'\s*之?(财星?|官星?|七杀?|煞|印星?|食神|伤官)', after):
                excl.append((term,'他神后置',s.strip()[:60])); break
            ta_near=bool(TA_GAN_RE.search(near) or TA_WX2_RE.search(near) or TA_SS_RE.search(near) or gan_other(near))
            self_near=bool(SELF_RE.search(near) or '身' in near)
            if ta_near:
                excl.append((term,'他神',s.strip()[:60])); break
            if self_near:
                mine+=1; break
            ta_any=bool(TA_GAN_RE.search(pre) or TA_WX2_RE.search(pre) or TA_SS_RE.search(pre) or gan_other(pre))
            self_any=bool(SELF_RE.search(pre) or '身' in pre)
            if ta_any and not self_any:
                excl.append((term,'他神',s.strip()[:60])); break
            mine+=1; break
    return mine, excl

WANG_SET=ds.WANG_SET; SHUAI_SET=ds.SHUAI_SET
stat={'W_only':0,'S_only':0,'both':0,'none':0}
W={'hit':0,'mid':0,'miss':0}; S={'hit':0,'mid':0,'miss':0}; dismissed=0; miss=[]
G={'you_hit':0,'you_miss':0,'wu_hit':0,'wu_miss':0,'wu_cong':0}; g_miss=[]
for r in rows:
    ch=r['chart']; dm=ch[4]; spec=r.get('spectrum','')
    if spec in ('ERR','',None): continue
    text=ds.case_text(int(r['line']))
    w_hits=[];s_hits=[]
    for term in ds.WANG:
        for m in re.finditer(re.escape(term),text):
            b=text[max(0,m.start()-14):m.start()];a=text[m.start():m.start()+8]
            if ds.subj_ok(b,a,dm,sent_of(text,m.start())): w_hits.append((term,(b+a).replace('\n','')));break
    for term in ds.SHUAI:
        for m in re.finditer(re.escape(term),text):
            b=text[max(0,m.start()-14):m.start()];a=text[m.start():m.start()+8]
            if ds.subj_ok(b,a,dm,sent_of(text,m.start())): s_hits.append((term,(b+a).replace('\n','')));break
    nw,ns=len(w_hits),len(s_hits)
    eng='旺' if spec in WANG_SET else ('衰' if spec in SHUAI_SET else '中')
    if (r.get('mu_mie_state') or '').strip()=='CONFIRMED': eng='衰'
    elif (r.get('zhonghe') or '').strip(): eng='中'
    if nw>=1 and ns==0:
        stat['W_only']+=1
        if ch in ds.REVIEWED: dismissed+=1
        else:
            k='hit' if eng=='旺' else ('mid' if eng=='中' else 'miss'); W[k]+=1
            if k=='miss': miss.append(('原文旺/引擎衰',ch,spec,w_hits[:1]))
    elif ns>=1 and nw==0:
        stat['S_only']+=1
        if ch in ds.REVIEWED: dismissed+=1
        else:
            k='hit' if eng=='衰' else ('mid' if eng=='中' else 'miss'); S[k]+=1
            if k=='miss': miss.append(('原文衰/引擎旺',ch,spec,s_hits[:1]))
    elif nw>=1 and ns>=1: stat['both']+=1
    else: stat['none']+=1
    # 日主根断言
    is_cong=bool((r.get('cong') or '').strip())
    rd=r.get('root_detail','') or ''
    has_any=bool(re.search(r'BEN|ZHONG|YU|HEAVY|LIGHT|SPECIAL',rd))
    ny,_=gen_hits(text,GEN_YOU,dm,is_cong)
    nwu,ex=gen_hits(text,GEN_WU,dm,is_cong)
    if ny>=1 and nwu==0:
        if has_any: G['you_hit']+=1
        else: G['you_miss']+=1; g_miss.append(('原文日主有根/引擎无根',ch,spec,rd[:60]))
    elif nwu>=1 and ny==0:
        if is_cong:
            G['wu_cong']+=1   # 从格: 事实层微余气根, 格局判从(原文以无根论), 分层一致
        elif not has_any: G['wu_hit']+=1
        else: G['wu_miss']+=1; g_miss.append(('原文日主无根/引擎有根',ch,spec,rd[:60],ex[:1]))

print('==== 日主旺衰方向断言对齐 ====')
print(f"命例 {len(rows)}; 明确旺向 {stat['W_only']}(命中{W['hit']}/中和{W['mid']}/反向{W['miss']}); 明确衰向 {stat['S_only']}(命中{S['hit']}/中和{S['mid']}/反向{S['miss']}); 人工裁定销项 {dismissed}; 旺衰并见 {stat['both']}; 无断言 {stat['none']}")
det=W['hit']+S['hit']; mid=W['mid']+S['mid']; bad=W['miss']+S['miss']; den=stat['W_only']+stat['S_only']
print(f"严格命中 {det}/{den} = {100*det/den:.1f}%  中和边界 {mid}  真反向 {bad}  (含白名单销项后有效一致 {100*(det+mid+dismissed)/den:.1f}%)\n")
print('==== 日主有根/无根断言对齐 ====')
print(f"有根断言: 引擎有根 {G['you_hit']}, 不符 {G['you_miss']}")
print(f"无根断言: 引擎无根 {G['wu_hit']}, 从格分层一致 {G['wu_cong']}, 不符 {G['wu_miss']}")
gden=G['you_hit']+G['you_miss']+G['wu_hit']+G['wu_miss']+G['wu_cong']; ghit=G['you_hit']+G['wu_hit']+G['wu_cong']
print(f"日主根断言一致 {ghit}/{gden} = {100*ghit/max(1,gden):.1f}%\n")
print('== 旺衰真反向(应0) =='); [print(x) for x in miss]
print('== 根断言不符(应0) =='); [print(x) for x in g_miss]
