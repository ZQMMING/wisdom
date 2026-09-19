# -*- coding: utf-8 -*-
# 合局化去身根/印根(T32): 日主或印的【当前有效本气根(root_detail仍标BEN)】入完整三合/三会局、
# 局化神为财或官杀(克泄方), 则该根从合化神、不复为身根(巳酉丑金财局化去巳中丙火比劫根), 从格门折减。
# 已被合局归化(root_detail非BEN, 如申子辰水局之辰土)不重复折, 免误降CONFIRMED。
# L623 辛巳丁酉丁酉辛丑: 巳火root_detail=BEN、在巳酉丑金财局内化去 -> 从财CANDIDATE。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
s=io.open(fp,encoding='utf-8').read()
old="""    dm_ben_eff = max(0, dm_ben - len(_ben_branches(pw, dm_wx) & struck))
    yin_ben_eff = max(0, yin_ben - len(_ben_branches(pw, yin_wx) & struck))
    root_struck = bool(struck)
    rootless = (dm_ben_eff == 0 and yin_ben_eff == 0)"""
assert s.count(old)==1, s.count(old)
new="""    dm_ben_eff = max(0, dm_ben - len(_ben_branches(pw, dm_wx) & struck))
    yin_ben_eff = max(0, yin_ben - len(_ben_branches(pw, yin_wx) & struck))
    root_struck = bool(struck)
    # 合局化去身根/印根: 仍为有效本气根(BEN)的支入完整三合/三会、化神为财或官杀(克泄方), 该根从化神(T32)
    _hh_dm, _hh_yin = set(), set()
    _cf0 = facts.get('combination_facts', {}) or {}
    for _items in (_cf0.get('sanhe', []), _cf0.get('sanhui', [])):
        for _it in _items:
            _mm = re.match(r'^([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥]).*?([金木水火土])', str(_it))
            if not _mm: continue
            _g = _mm.groups(); _jwx = _g[3]
            if _jwx not in (cai_wx, gs_wx): continue
            for _br in _g[:3]:
                if BRANCH_WX.get(_br) == dm_wx and str(dm.get('root_detail', {}).get(_br, '')).startswith('BEN'):
                    _hh_dm.add(_br)
                elif BRANCH_WX.get(_br) == yin_wx and str(yin.get('root_detail', {}).get(_br, '')).startswith('BEN'):
                    _hh_yin.add(_br)
    if _hh_dm or _hh_yin:
        dm_ben_eff = max(0, dm_ben_eff - len(_hh_dm))
        yin_ben_eff = max(0, yin_ben_eff - len(_hh_yin))
        root_struck = root_struck or bool(_hh_dm or _hh_yin)
    rootless = (dm_ben_eff == 0 and yin_ben_eff == 0)"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched hehua qu root v2 (BEN-only)')
