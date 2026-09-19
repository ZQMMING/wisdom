# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()

# A. 词表+判词: 去裸单字, 加科举成语/终老/去病/转折
old_a = r"""JI=['科甲连登','大魁天下','登科','登第','发甲','中乡榜','乡榜','南宫报捷','报捷','采芹','攀桂','入泮','补廪','补禀','入词林','点中','仕版连登','仁版连登','连登甲第','连登','出仕','琴堂','知县','郡守','封疆','发财','获利万金','获利','发福','发巨万','发财数万','发财十余万','大得际遇','得际遇','际遇','成家','娶妻生子','生子','荫庇','荫疪','丰存','仕途坦平','坦平','顺遂','富贵','名利两全','名利','大好','丰盈','兴家','创业','起家','获一衿','可获一衿','一衿','秋闱有望','棘闱奏捷','奏捷','仕路','擢','美','丰厚','大利','吉','亨','安','宁','平宁','事业巍峨','高攀月桂','高躔']
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
    return None,blob[:70]"""
new_a = r"""JI=['科甲连登','大魁天下','登科','登第','发甲','中乡榜','乡榜','南宫报捷','南宫','报捷','采芹','攀桂','月桂','撞破烟楼','高攀月桂','高躔','入泮','补廪','补禀','入词林','点中','仕版连登','仁版连登','连登甲第','连登','出仕','琴堂','知县','郡守','州牧','县令','封疆','发财','获利万金','获利','发福','发巨万','发财数万','发财十余万','大得际遇','得际遇','际遇','成家','立业','娶妻生子','生子','荫庇','荫疪','丰存','仕途坦平','坦平','顺遂','太平相业','宦海无波','无波','富贵','名利两全','名利','大好','丰盈','兴家','创业','起家','获一衿','可获一衿','一衿','秋闱有望','棘闱奏捷','奏捷','仕路','遂仕路','仕至','擢','丰厚','大利','事业巍峨','腾身','登月殿','月殿','琼林','庆集','云程','安享','其乐自如','琴书','家业日增','日增','病药相济','药病相济','有病得药','去病','吉','亨通','平宁','宁谧','无恙']
XIONG=['家破身亡','破财而亡','家业破尽','破尽而亡','而亡','死于','死矣','病死','不禄','寿元有碍','丁艰','丁外艰','丁内艰','刑丧','刑伤','刑耗','刑克','克妻','克子','克夫','刑妻','刑耗并见','破财','破耗','耗散','家业渐消','家业消亡','家业耗散','家业破','家道日落','日落','蹭蹬','不捷','秋闱不捷','落职','诖误','大病','危险','犯事落职','贫乏不堪','贫困','贫乏','流为乞丐','乞丐','父母双亡','大凶','患难','病患','得病','血症','孤苦','削发为僧','一败如灰','倾家荡产','冻饿','嫖赌','祝融','骨肉之变','茕茕','只影','阻云程','一阻云程','多滞','少成','艰难']
LAO=re.compile(r'寿[已至]?\s*[七八九]?\s*旬|[七八九]旬(而|矣|，|,)?$|寿元已?高')
QUBING=re.compile(r'病药相济|药病相济|有病得药|克去|破其|冲去|制去|合去|去其|拔去|去病')
def seg_sent(t): return [x for x in re.split(r'[。；！\n]',t) if x]
def luck_verdict(txt,g,z):
    sents=[st for st in seg_sent(txt) if len(GZ.findall(st))<3]
    hits=[st for st in sents if (g+z in st or g+'运' in st or z+'运' in st)]
    if not hits: return None,''
    blob=' '.join(hits)
    if LAO.search(blob) and not re.search(r'家破|破尽|横|刑丧|克妻|克子|贫乏|乞丐',blob):
        return 'lao',blob[:70]
    b=blob
    m=re.search(r'而([^，。；,；]{2,12})$',b)
    if m and not re.search(r'亡|死|丧|败|耗|乏|困|滞',m.group(1)): b=m.group(1)
    nj=sum(b.count(w) for w in JI); nx=sum(b.count(w) for w in XIONG)
    if QUBING.search(b) and nx==0: return 'ji',b[:70]
    if nj>0 and nx==0: return 'ji',b[:70]
    if nx>0 and nj==0: return 'xiong',b[:70]
    if nj>0 and nx>0: return 'hun',b[:70]
    return None,b[:70]"""
assert s.count(old_a)==1, ('A',s.count(old_a))
s=s.replace(old_a,new_a)

# B. new_huashen 撤六合BEN_HE, 只认完整三合三会ju_n增量
old_b = r'''def new_huashen(tp0,tp):
    """该运新成三合/三会(ju_n增量)或紧贴六合归化(BEN_HE新支)的化神五行。"""
    w0=tp0['wuxing_power']['wuxing_power']; w1=tp['wuxing_power']['wuxing_power']; out=[]
    for wx in '木火土金水':
        if int(w1[wx].get('ju_n',0))>int(w0[wx].get('ju_n',0)): out.append(wx)
        d0=w0[wx].get('root_detail',{}) or {}; d1=w1[wx].get('root_detail',{}) or {}
        for z,lab in d1.items():
            if z not in d0 and 'BEN_HE' in str(lab): out.append(wx)
    return out'''
new_b = r'''def new_huashen(tp0,tp):
    """该运新成完整三合/三会(ju_n增量)的化神五行; 六合BEN_HE偏宽(力弱/化神须透干当令无克)不采。"""
    w0=tp0['wuxing_power']['wuxing_power']; w1=tp['wuxing_power']['wuxing_power']; out=[]
    for wx in '木火土金水':
        if int(w1[wx].get('ju_n',0))>int(w0[wx].get('ju_n',0)): out.append(wx)
    return out'''
assert s.count(old_b)==1, ('B',s.count(old_b))
s=s.replace(old_b,new_b)

# C. lao 归中性
old_c = "        if not v or v=='hun': continue\n        st['text_hit']+=1"
new_c = "        if not v or v=='hun' or v=='lao':\n            if v=='lao': st['neutral']+=1\n            continue\n        st['text_hit']+=1"
assert s.count(old_c)==1, ('C',s.count(old_c))
s=s.replace(old_c,new_c)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('dayun_align v3 重放 done')
