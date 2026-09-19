# -*- coding: utf-8 -*-
# 假从回正格门收窄: 日支自坐本气身库根, 虽会局不夺(保守留正格);
# 他柱(年月时)本气根若入完整三合/三会、化神为财或官杀(克泄方)而被合化, 则从合化、不回正格。
# L623 丁火日支酉(财)无身根, 年支巳火本气在巳酉丑金财局内化去 -> 不回正, 顺入从财。
# 戊土坐戌逢申酉戌(化神金=食伤非财官)不在此列, 身库本根保留不退化。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()
old="""    raw_ben_branch=[]
    for _i,_k in enumerate(_pks):
        _hs=facts.get('hidden_stems',{}).get(_k) or []
        if _hs and _ganwx.get(_hs[0])==dmw: raw_ben_branch.append(brs[_i])
    dm_ben_real=bool(raw_ben_branch)"""
assert s.count(old)==1, s.count(old)
new="""    # 完整三合/三会化神为财或官杀时, 局内他柱(非日支自坐)日主本气根从合化, 不回正格
    _hhbr=set()
    _cfy=facts.get('combination_facts',{}) or {}
    for _items in (_cfy.get('sanhe',[]),_cfy.get('sanhui',[])):
        for _it in _items:
            _mm=re.match(r'^([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥]).*?([金木水火土])',str(_it))
            if not _mm: continue
            _gg=_mm.groups()
            if _gg[3] in (t['cai'],t['guan']):
                for _br in _gg[:3]:
                    if BRANCH_WX.get(_br)==dmw: _hhbr.add(_br)
    raw_ben_branch=[]
    for _i,_k in enumerate(_pks):
        _hs=facts.get('hidden_stems',{}).get(_k) or []
        _br=brs[_i]
        if _hs and _ganwx.get(_hs[0])==dmw and (_k=='day' or _br not in _hhbr):
            raw_ben_branch.append(_br)
    dm_ben_real=bool(raw_ben_branch)"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched cong hehua gen_zheng narrow')
