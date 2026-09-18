# -*- coding: utf-8 -*-
"""大运应验对齐v2(外部gt, 引擎只输出结构喜忌, 吉凶映射在本核对层):
每步大运喜忌 = 运干支静态五行 + 新增会局/合化化神(会局成势主导) vs 引擎喜用/忌;
原典断语该运吉凶词 -> 喜用运应吉、忌神运应凶; 混合/闲/未点明不计入分母。"""
import re, sys
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, BRANCH_WX
from engines.common.daymaster_power_network import build_power_network
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine
from engines.common.transit_power import build_transit_power, transit_clash_verdicts
path=r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines=open(path,encoding='utf-8').read().splitlines()
GZ=re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')
GAN_WX={}
for _gs,_wx in [('甲乙','木'),('丙丁','火'),('戊己','土'),('庚辛','金'),('壬癸','水')]:
    for _c in _gs: GAN_WX[_c]=_wx
LH={frozenset(('子','丑')):'土',frozenset(('寅','亥')):'木',frozenset(('卯','戌')):'火',
    frozenset(('辰','酉')):'金',frozenset(('巳','申')):'水',frozenset(('午','未')):'土'}
raw=[]
for i,ln in enumerate(lines):
    s=ln.strip(); fp=None
    if s.startswith('八字'):
        b=s.split('：',1)[-1].split(':',1)[-1].strip()
        if len(GZ.findall(b))==4: fp=GZ.findall(b)
    elif len(GZ.findall(s))==4 and len(s)<60:
        c=GZ.sub('',s).replace(' ','').replace('　','')
        if c=='': fp=GZ.findall(s)
    if fp: raw.append((i,fp))
def parse_dayun(i):
    for off in (1,2):
        if i+off>=len(lines): continue
        nl=lines[i+off]; gz=GZ.findall(nl)
        c=GZ.sub('',nl).replace(' ','').replace('　','').replace('大运','').replace('：','').replace(':','').strip()
        if len(gz)>=5 and c=='': return [a+b for a,b in gz]
    return []
def strip_dayun_line(nl):
    ms=list(GZ.finditer(nl))
    if len(ms)>=5: return nl[ms[-1].end():].strip()
    return nl.strip()
cases=[]
for k,(i,fp) in enumerate(raw):
    end=raw[k+1][0] if k+1<len(raw) else len(lines)
    dy=parse_dayun(i); prose=[]
    for j in range(i+1,end):
        t=strip_dayun_line(lines[j])
        if t: prose.append(t)
    cases.append((i,fp,dy,'\n'.join(prose)))
JI=['科甲连登','大魁天下','登科','登第','发甲','中乡榜','乡榜','南宫报捷','报捷','采芹','攀桂','入泮','补廪','补禀','入词林','点中','仕版连登','仁版连登','连登甲第','连登','出仕','琴堂','知县','郡守','封疆','发财','获利万金','获利','发福','发巨万','发财数万','发财十余万','大得际遇','得际遇','际遇','成家','娶妻生子','生子','荫庇','荫疪','丰存','仕途坦平','坦平','顺遂','富贵','名利两全','名利','大好','丰盈','兴家','创业','起家','获一衿','可获一衿','一衿','秋闱有望','棘闱奏捷','奏捷','仕路','擢','美','丰厚','大利','吉','亨','安','宁','平宁','事业巍峨','高攀月桂','高躔']
XIONG=['家破身亡','破财而亡','家业破尽','破尽而亡','而亡','死于','死矣','病死','不禄','寿元有碍','丁艰','丁外艰','丁内艰','刑丧','刑伤','刑耗','刑克','克妻','克子','克夫','刑妻','破财','破耗','耗散','家业渐消','家业消亡','家业耗散','家业破','家道日落','日落','蹭蹬','不捷','秋闱不捷','落职','诖误','大病','危险','犯事落职','贫乏不堪','贫困','贫乏','流为乞丐','乞丐','父母双亡','不吉','大凶','患难','病患','得病','血症','孤苦','削发为僧','一败如灰','家业渐消','凶','晦','破','败','亡','丧','困','灾','艰','危','倾','罢','谪','死','多滞','少成','艰难']
def seg_sent(t): return [x for x in re.split(r'[。；！\n]',t) if x]
def luck_verdict(txt,g,z):
    sents=[st for st in seg_sent(txt) if len(GZ.findall(st))<3]
    hits=[st for st in sents if (g+z in st or g+'运' in st or z+'运' in st)]
    if not hits: return None,''
    blob=' '.join(hits)
    nj=sum(blob.count(w) for w in JI); nx=sum(blob.count(w) for w in XIONG)
    if nj>0 and nx==0: return 'ji',blob[:70]
    if nx>0 and nj==0: return 'xiong',blob[:70]
    if nj>0 and nx>0: return 'hun',blob[:70]
    return None,blob[:70]
_cache={}
def huashen(comb):
    hs=[]
    for s in comb.get('sanhe',[])+comb.get('sanhui',[]):
        m=re.search(r'([木火土金水])',str(s))
        if m: hs.append(m.group(1))
    for pair in comb.get('liuhe',[]):
        try:
            _w=LH.get(frozenset((pair[0],pair[1])))
            if _w: hs.append(_w)
        except Exception: pass
    return hs
def engine(fp):
    key=tuple(fp)
    if key in _cache: return _cache[key]
    p={'year':list(fp[0]),'month':list(fp[1]),'day':list(fp[2]),'hour':list(fp[3])}
    f=l0build(p); ds=f['day_stem']
    hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
    pa=build_power_structure(p); rc=build_root_classes(p,hst); tc=build_tou_cang(f)
    wxo=build_wang_xiang(f,ds); rr=build_root_relations(rc,f['combination_facts'])
    ts=build_two_side(rc,tc,rr); bt=build_branch_tiers(p,f); th=build_tian_he(p,f)
    wp=build_wuxing_power(p,f,th)
    net=build_power_network(pa,rc,tc,wxo,rr,ts,branch_tier=bt,tian_he=th,facts=f)
    net.setdefault('facts',{})['daymaster_element']=WUXING[ds]
    sp=build_spectrum_topology(net,wp)
    clc=build_climate_candidates(f); cls=build_climate_structure(p,f,th)
    spp=build_special_patterns(p,f,wp,th,cls)
    ye=build_yongshen_engine(p,f,wp,sp,spp,clc)
    tp0=build_transit_power(p,[])
    _cache[key]=(p,f,ye,tp0)
    return _cache[key]
def new_huashen(tp0,tp):
    """该运新成三合/三会(ju_n增量)或紧贴六合归化(BEN_HE新支)的化神五行。"""
    w0=tp0['wuxing_power']['wuxing_power']; w1=tp['wuxing_power']['wuxing_power']; out=[]
    for wx in '木火土金水':
        if int(w1[wx].get('ju_n',0))>int(w0[wx].get('ju_n',0)): out.append(wx)
        d0=w0[wx].get('root_detail',{}) or {}; d1=w1[wx].get('root_detail',{}) or {}
        for z,lab in d1.items():
            if z not in d0 and 'BEN_HE' in str(lab): out.append(wx)
    return out
def cls_w(w,fav,av):
    return 'fav' if w in fav else ('av' if w in av else 'xian')
st={'steps':0,'text_hit':0,'judgable':0,'agree':0,'dis':0,'neutral':0,'by_ju':0}
dislist=[]
for li,fp,dy,txt in cases:
    if len(dy)<4: continue
    try: p,f,ye,tp0=engine(fp)
    except Exception: continue
    prim=ye.get('yongshen_primary') or ''
    fav=set([prim])|set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av=set(ye.get('yongshen_avoid') or [])
    dm=f['day_stem']
    for gz in dy:
        g,z=gz[0],gz[1]; st['steps']+=1
        v,blob=luck_verdict(txt,g,z)
        if not v or v=='hun': continue
        st['text_hit']+=1
        gc=cls_w(GAN_WX[g],fav,av); zc=cls_w(BRANCH_WX[z],fav,av)
        lc=None; ju=''
        # 新增会局/合化化神(会局成势主导)
        tp=build_transit_power(p,[gz])
        new_hs=new_huashen(tp0,tp)
        if new_hs:
            hf=[w for w in new_hs if w in fav]; ha=[w for w in new_hs if w in av]
            ju='化神%s'%''.join(new_hs)
            if ha and not hf: lc='av'
            elif hf and not ha: lc='fav'
            else: lc='mix'
            if lc in ('fav','av'): st['by_ju']+=1
        if lc is None:
            ss={gc,zc}
            if ss=={'xian'}: lc='xian'
            elif 'av' in ss and 'fav' not in ss: lc='av' if ss=={'av'} else 'av_l'
            elif 'fav' in ss and 'av' not in ss: lc='fav' if 'xian' not in ss else 'fav_l'
            else: lc='mix'
        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
        if lc in ('mix','xian'): st['neutral']+=1; continue
        st['judgable']+=1
        expect='ji' if lc.startswith('fav') else 'xiong'
        if expect==v: st['agree']+=1
        else:
            st['dis']+=1
            ch=''.join(a+b for a,b in fp)
            dislist.append((li+1,ch,gz,lc,GAN_WX[g],BRANCH_WX[z],ju,v,ye.get('yongshen_primary'),sorted(fav),sorted(av),blob,';'.join(clash)))
print(st)
if st['judgable']:
    print('可判 %d 一致 %d (%.1f%%) 不一致 %d (%.1f%%) 中性 %d 其中会局主导 %d'%(
        st['judgable'],st['agree'],100*st['agree']/st['judgable'],st['dis'],100*st['dis']/st['judgable'],st['neutral'],st['by_ju']))
print('\n=== 不一致(前45) ===')
for x in dislist[:45]:
    print(' L%d %s 运%s[%s %s] 原文%s 主%s 喜%s 忌%s 冲[%s] | %s'%(x[0],x[1],x[2],x[3],x[6],x[7],x[8],x[9],x[10],x[12],x[11]))
