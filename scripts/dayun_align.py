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
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, BRANCH_WX, SHENG, KE
from engines.common.daymaster_power_network import build_power_network
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine
from engines.common.transit_power import build_transit_power, transit_clash_verdicts, element_power_tier
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
JI=['科甲连登','大魁天下','登科','登第','发甲','中乡榜','乡榜','南宫报捷','南宫','报捷','采芹','攀桂','月桂','撞破烟楼','高攀月桂','高躔','入泮','补廪','补禀','入词林','点中','仕版连登','仁版连登','连登甲第','连登','出仕','琴堂','知县','郡守','州牧','县令','封疆','发财','获利万金','获利','发福','发巨万','发财数万','发财十余万','大得际遇','得际遇','际遇','成家','立业','娶妻生子','生子','荫庇','荫疪','丰存','仕途坦平','坦平','顺遂','太平相业','宦海无波','无波','富贵','名利两全','名利','大好','丰盈','兴家','创业','起家','获一衿','可获一衿','一衿','秋闱有望','棘闱奏捷','奏捷','仕路','遂仕路','仕至','擢','丰厚','大利','事业巍峨','腾身','登月殿','月殿','琼林','庆集','云程','安享','其乐自如','琴书','家业日增','日增','病药相济','药病相济','有病得药','去病','吉','亨通','平宁','宁谧','升迁','举于乡','县宰','无恙']
XIONG=['家破身亡','破财而亡','家业破尽','破尽而亡','而亡','死于','死矣','病死','不禄','寿元有碍','丁艰','丁外艰','丁内艰','刑丧','刑伤','刑耗','刑克','克妻','克子','克夫','刑妻','刑耗并见','破财','破耗','耗散','家业渐消','家业消亡','家业耗散','家业破','家道日落','日落','蹭蹬','不捷','秋闱不捷','落职','诖误','大病','危险','犯事落职','贫乏不堪','贫困','贫乏','流为乞丐','乞丐','父母双亡','大凶','患难','病患','得病','血症','孤苦','削发为僧','一败如灰','倾家荡产','冻饿','嫖赌','祝融','骨肉之变','茕茕','只影','阻云程','一阻云程','多滞','少成','一败而尽','一败涂地','艰难']
LAO=re.compile(r'寿[已至]?\s*[七八九]?\s*旬|[七八九]旬(而|矣|，|,)?$|寿元已?高')
QUBING=re.compile(r'病药相济|药病相济|有病得药|克去|破其|冲去|制去|合去|去其|拔去|去病')
GUIYIN=re.compile(r'退归|致仕|归田|休官|告老|林下|挂冠|归老|退隐')
ANXIANG=re.compile(r'安享|琴书|其乐|自若|安闲|优游|无恙|颐养|安逸|安享余年|乐享')
def seg_sent(t): return [x for x in re.split(r'[。；！\n]',t) if x]
def luck_verdict(txt,g,z):
    sents=[st for st in seg_sent(txt) if len(GZ.findall(st))<3]
    hits=[st for st in sents if (g+z in st or g+'运' in st or z+'运' in st)]
    if not hits: return None,''
    blob=' '.join(hits)
    if LAO.search(blob) and not re.search(r'家破|破尽|横|刑丧|克妻|克子|贫乏|乞丐',blob):
        return 'lao',blob[:70]
    # 归隐安乐(退归/致仕+安享琴书其乐): 非仕途升迁之吉, 亦非灾亡之凶, 属归隐安乐中性, 不计成败分母(L889甲申乙酉退归安享琴书其乐自如)
    if GUIYIN.search(blob) and ANXIANG.search(blob) and not re.search(r'家破|破尽|刑丧|克妻|克子|贫乏|乞丐|不禄|蹭蹬|亡|死',blob):
        return 'lao',blob[:70]
    b=blob
    m=re.search(r'而([^，。；,；]{2,12})$',b)
    if m and not re.search(r'亡|死|丧|败|耗|乏|困|滞',m.group(1)): b=m.group(1)
    nj=sum(b.count(w) for w in JI); nx=sum(b.count(w) for w in XIONG)
    if QUBING.search(b) and nx==0: return 'ji',b[:70]
    if nj>0 and nx==0: return 'ji',b[:70]
    if nx>0 and nj==0: return 'xiong',b[:70]
    if nj>0 and nx>0: return 'hun',b[:70]
    return None,b[:70]
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
    """该运新成完整三合/三会(ju_n增量)的化神五行; 六合BEN_HE偏宽(力弱/化神须透干当令无克)不采。"""
    w0=tp0['wuxing_power']['wuxing_power']; w1=tp['wuxing_power']['wuxing_power']; out=[]
    for wx in '木火土金水':
        if int(w1[wx].get('ju_n',0))>int(w0[wx].get('ju_n',0)): out.append(wx)
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
        # g类噪声: 断语窗以《原注》标记开头=章末通用泛论(非本命任注断语), 不入对齐分母; 本命断语不以【原注】开头
        if blob and blob.lstrip().startswith('【原注】'):
            v=None
        if not v or v=='hun' or v=='lao':
            if v=='lao': st['neutral']+=1
            continue
        st['text_hit']+=1
        gc=cls_w(GAN_WX[g],fav,av); zc=cls_w(BRANCH_WX[z],fav,av)
        lc=None; ju=''
        # 新增会局/合化化神(会局成势主导)
        tp=build_transit_power(p,[gz])
        new_hs=new_huashen(tp0,tp)
        if new_hs:
            _zwx=BRANCH_WX[z]; _KEME={vv:kk for kk,vv in KE.items()}
            new_hs=[w for w in new_hs if not (
                tp0['wuxing_power']['wuxing_power'][w].get('ling_state') in ('休','囚','死')
                and _KEME.get(w)==_zwx and _zwx in fav)]
        # 运支临完整三合/三会局成员、化神成势 -> 从化神判喜忌(合化加力)
        _jjcf=tp.get('combination_facts',{}) if isinstance(tp,dict) else {}
        for _pr in (list(_jjcf.get('sanhe',[]))+list(_jjcf.get('sanhui',[]))):
            _m=re.match(r'^([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥]).*?([金木水火土])',str(_pr))
            if _m and z in (_m.group(1),_m.group(2),_m.group(3)) and element_power_tier(tp['wuxing_power'],_m.group(4))['tier']>=2:
                zc=cls_w(_m.group(4),fav,av); break
        # 虚喜犯旺(微神入旺乡): 命局太旺/旺极、生扶方P(比劫或印)成势tier>=2, 运上与P相克(财/官, 非顺泄秀神)的喜神复合仍虚tier<=1,
        # 则微财微官无力为用、反激旺神/被旺神所灭, 降判忌; 喜神得根成党tier>=2为真用神不犯。有序枚举+比重, # PCT-MARK
        _spec=ye.get('spectrum_tier') or ''
        if _spec in ('太旺','旺极'):
            _SHENG_ME={v:k for k,v in SHENG.items()}; _dmw=WUXING[dm]
            _KE_ME={v:k for k,v in KE.items()}
            _P=max('木火土金水', key=lambda x: element_power_tier(tp0['wuxing_power'],x)['tier'])
            _ke_set={KE.get(_dmw), _KE_ME.get(_dmw)}  # 仅财(我克)+官杀(克我)为逆神; 食伤顺泄秀、印比不犯旺
            if _P in (_dmw, _SHENG_ME.get(_dmw)) and element_power_tier(tp0['wuxing_power'],_P)['tier']>=2:
                def _xufan(w):
                    # 完全无本气根的虚透(tier0衰)方为微神犯旺; 有一根(含运柱得禄/通根,tier>=1)即能立, 不犯。根被冲拔/合化折减另见合化刀
                    return bool(w) and w in _ke_set and element_power_tier(tp['wuxing_power'],w)['tier']==0
                if gc=='fav' and _xufan(GAN_WX[g]): gc='av'
                if zc=='fav' and not new_hs and _xufan(BRANCH_WX[z]): zc='av'
        # 虚官不犯(虚忌不凶, 对称虚喜犯旺): 专旺顺用、运干官杀复合tier0无根、运支非官杀根而为喜(比劫当令官绝/印化官)、非新会局化神,
        # 则虚官坐本方被化/绝不能克旺反不犯(任注: 金不通根、支逢生旺), 干降闲以支喜主导; 会局化神虚干无依直冲(如寅午戌)仍由化神块判凶
        if not new_hs:
            _dmw0=WUXING[dm]; _gw0={v:k for k,v in KE.items()}.get(_dmw0); _yw0={v:k for k,v in SHENG.items()}.get(_dmw0)
            _yp=ye.get('yongshen_paths') or []
            _zw_shun=any('ZHUANWANG' in x for x in _yp) and not any('LIANGQI' in x for x in _yp)  # 仅专旺顺用; 两气/伤官格虚官坐食伤=伤官见官混局仍病(L360庚午降)
            if _gw0 and _zw_shun and gc=='av' and GAN_WX.get(g)==_gw0 and zc=='fav' \
                    and BRANCH_WX.get(z) in (_dmw0,_yw0) \
                    and element_power_tier(tp['wuxing_power'],_gw0)['tier']==0:
                gc='xian'
        if new_hs:
            hf=[w for w in new_hs if w in fav]; ha=[w for w in new_hs if w in av]
            ju='化神%s'%''.join(new_hs)
            _shun=any(x in ('ZHUANWANG','LIANGQI') for x in (ye.get('yongshen_paths') or []))  # 从儿/从格会方顺神、干逆神坐化神多被顺化(吾儿又见儿), 不援虚干犯旺例
            if ha and not hf: lc='av'
            elif hf and not ha:
                # 顺用格会顺神方局(化神喜)而运干为逆神: 运支入会局被化, 干逆神在原局无本气根=虚透犯旺主凶(任注: 虚神犯旺/激其冲奔); 有本气根则相争混。正格身弱会印局(杀印相生)paths非顺用, 不触发
                if _shun and gc=='av' and int(tp0['wuxing_power']['wuxing_power'][GAN_WX[g]].get('ben_n',0))==0:
                    lc='av'
                elif _shun and gc=='av':
                    lc='mix'
                else:
                    lc='fav'
            else: lc='mix'
            if lc in ('fav','av'): st['by_ju']+=1
        # 身衰正格、运支财/官杀成势压虚透喜干(非食伤) -> 支凶主导(身弱难任财官, 优先级非数量)
        if lc is None and _spec in ('衰极','太衰','衰') and gc=='fav' and zc!='fav':
            _dmwZ=GAN_WX[dm]; _KEMEZ={vv:kk for kk,vv in KE.items()}
            _ppZ='/'.join(ye.get('yongshen_paths') or [])
            if (BRANCH_WX[z] in (KE.get(_dmwZ), _KEMEZ.get(_dmwZ))
                    and GAN_WX[g] != SHENG.get(_dmwZ)
                    and not any(x in _ppZ for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI'))
                    and element_power_tier(tp['wuxing_power'],BRANCH_WX[z])['tier']>=2
                    and element_power_tier(tp['wuxing_power'],GAN_WX[g])['tier']<=1):
                lc='av_l'
        # V5.1: 身弱印比修正 - 原局身弱时, 印比(生扶日主)大运即使克调候用神被判为忌, 也应判为喜(身弱喜印比)
        # 原典: 身弱喜印比; 调候忌神判断不能覆盖身弱生扶需求(优先级非数量, 布尔+多态枚举)
        if lc is None and _spec in ('衰极','太衰','衰'):
            _dmwW=WUXING[dm]; _SHENG_ME_W={v:k for k,v in SHENG.items()}
            _yinbi={_dmwW, _SHENG_ME_W.get(_dmwW)}  # 比劫(同我)+印(生我)
            _ppY='/'.join(ye.get('yongshen_paths') or [])
            if not any(x in _ppY for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI')):  # 非从格/专旺/化气/两气
                if gc=='av' and GAN_WX.get(g) in _yinbi: gc='fav'  # 天干印比升为喜
                if zc=='av' and BRANCH_WX.get(z) in _yinbi: zc='fav'  # 地支印比升为喜
        # V5.3: 身旺克泄耗修正 - 原局身旺时, 食伤/财/官杀(克泄耗日主)大运即使是调候忌神也应判为喜(身旺喜克泄耗)
        # 原典: 身旺喜克泄耗; 调候忌神判断不能覆盖身旺泄秀需求(优先级非数量, 布尔+多态枚举)
        if lc is None and _spec in ('旺','太旺','旺极'):
            _dmwS=WUXING[dm]; _KE_ME_S={v:k for k,v in KE.items()}
            _kexiehao={SHENG.get(_dmwS), KE.get(_dmwS), _KE_ME_S.get(_dmwS)}  # 食伤(我生)+财(我克)+官杀(克我)
            _ppS='/'.join(ye.get('yongshen_paths') or [])
            if not any(x in _ppS for x in ('CONG','ZHUANWANG','HUA_QI','LIANGQI')):  # 非从格/专旺/化气/两气
                if gc=='av' and GAN_WX.get(g) in _kexiehao: gc='fav'  # 天干克泄耗升为喜
                if zc=='av' and BRANCH_WX.get(z) in _kexiehao: zc='fav'  # 地支克泄耗升为喜
        # V5.2: 流通修正 - 大运五行生扶用神(即大运为用神之印)时, 即使大运本身在avoid中, 也降为中性
        # 原典: 五行流通, 忌神生用神则化忌为喜(如木生火, 木虽为忌但生火用神); 布尔+多态枚举+网络拓扑
        if lc is None and prim and prim in WUXING:
            _SHENG_ME_L={v:k for k,v in SHENG.items()}  # 生我者(印)
            _sheng_of_prim = _SHENG_ME_L.get(prim)  # 生用神的五行(用神之印)
            if _sheng_of_prim:
                # 大运天干/地支是用神之印, 且当前判为忌 -> 降为中性(流通生用神)
                if gc=='av' and GAN_WX.get(g)==_sheng_of_prim: gc='xian'
                if zc=='av' and BRANCH_WX.get(z)==_sheng_of_prim: zc='xian'
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
