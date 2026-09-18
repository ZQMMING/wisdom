# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\wuxing_power.py'
s=io.open(p,encoding='utf-8').read()

# ---- 替换1: _root_raw_for_wx 支持 branch_convert ----
old1='''def _root_raw_for_wx(wx: str, pillars, hidden_by_pillar: Dict[str, List[str]]) -> Dict[str, Any]:
    """某五行在四支按本气/中气/余气层级的原始根分(未乘月令系数)."""
    ben_n = zhong_n = yu_n = 0
    detail = {}
    for k in PILLAR_KEYS:
        z = pillars[k][1]
        stems = hidden_by_pillar.get(k, [])
        hit = None
        for idx, h in enumerate(stems):
            if WUXING.get(h) == wx:
                if idx == 0:
                    hit = 'BEN'; break
                elif idx == 1:
                    hit = 'ZHONG'
                elif idx == 2 and hit is None:
                    hit = 'YU'
        if hit == 'BEN':
            ben_n += 1; detail[z] = 'BEN'
        elif hit == 'ZHONG':
            zhong_n += 1; detail[z] = 'ZHONG'
        elif hit == 'YU':
            yu_n += 1; detail[z] = 'YU'
    raw = W_BENQI * ben_n + W_ZHONGQI * zhong_n + W_YUQI * yu_n
    return {'raw': raw, 'ben_n': ben_n, 'zhong_n': zhong_n, 'yu_n': yu_n, 'detail': detail}'''
new1='''def _root_raw_for_wx(wx: str, pillars, hidden_by_pillar: Dict[str, List[str]],
                     branch_convert: Dict[str, str] = None) -> Dict[str, Any]:
    """某五行在四支按本气/中气/余气层级的原始根分(未乘月令系数).

    branch_convert: 三会方/三合局成局后四季土(辰戌丑未)本气归化会神五行,
    如 亥子丑三会水 -> 丑本气己土不再计土, 归化计水(T32/T33 会局改变根气归属).
    """
    branch_convert = branch_convert or {}
    ben_n = zhong_n = yu_n = 0
    detail = {}
    for k in PILLAR_KEYS:
        z = pillars[k][1]
        stems = hidden_by_pillar.get(k, [])
        if z in branch_convert:
            cwx = branch_convert[z]
            if wx == cwx:
                ben_n += 1; detail[z] = 'BEN_JU'
            for idx, h in enumerate(stems[1:], start=1):
                if WUXING.get(h) == wx:
                    if idx == 1:
                        zhong_n += 1; detail.setdefault(z, 'ZHONG')
                    elif idx == 2:
                        yu_n += 1; detail.setdefault(z, 'YU')
            continue
        hit = None
        for idx, h in enumerate(stems):
            if WUXING.get(h) == wx:
                if idx == 0:
                    hit = 'BEN'; break
                elif idx == 1:
                    hit = 'ZHONG'
                elif idx == 2 and hit is None:
                    hit = 'YU'
        if hit == 'BEN':
            ben_n += 1; detail[z] = 'BEN'
        elif hit == 'ZHONG':
            zhong_n += 1; detail[z] = 'ZHONG'
        elif hit == 'YU':
            yu_n += 1; detail[z] = 'YU'
    raw = W_BENQI * ben_n + W_ZHONGQI * zhong_n + W_YUQI * yu_n
    return {'raw': raw, 'ben_n': ben_n, 'zhong_n': zhong_n, 'yu_n': yu_n, 'detail': detail}'''
assert old1 in s, 'old1 not found'
s=s.replace(old1,new1)

# ---- 替换2: 解析成局建 branch_convert 并传入 ----
old2='''    ju_wx = []
    if tian_he:
        for ju in (tian_he.get('sanhe_ju', []) or []) + (tian_he.get('sanhui_ju', []) or []):
            wx = None
            if isinstance(ju, dict):
                wx = ju.get('wuxing') or ju.get('huashen') or ju.get('element')
            elif isinstance(ju, (list, tuple)) and ju:
                wx = ju[-1]
            if wx in WX_LIST:
                ju_wx.append(wx)

    power = {}
    for wx in WX_LIST:
        root = _root_raw_for_wx(wx, pillars, hidden_by_pillar)'''
new2='''    ju_wx = []
    branch_convert = {}
    TU_BRANCHES = {'辰', '戌', '丑', '未'}
    def _absorb_ju(ju):
        wx = None; brs = []
        if isinstance(ju, dict):
            wx = ju.get('wuxing') or ju.get('huashen') or ju.get('element')
            brs = ju.get('branches') or ju.get('branches_char') or []
            nm = ju.get('name') or ''
            if not brs:
                brs = [c for c in nm if c in BRANCH_WX]
            if not wx:
                for c in reversed(nm):
                    if c in WX_LIST:
                        wx = c; break
        elif isinstance(ju, (list, tuple)) and ju:
            wx = ju[-1]; brs = list(ju[:-1])
        elif isinstance(ju, str):
            brs = [c for c in ju if c in BRANCH_WX]
            for c in reversed(ju):
                if c in WX_LIST:
                    wx = c; break
        if wx in WX_LIST:
            ju_wx.append(wx)
            for z in brs:
                if z in TU_BRANCHES:
                    branch_convert[z] = wx   # 四季土本气归化会神
    if tian_he:
        for ju in (tian_he.get('sanhe_ju', []) or []) + (tian_he.get('sanhui_ju', []) or []):
            _absorb_ju(ju)

    power = {}
    for wx in WX_LIST:
        root = _root_raw_for_wx(wx, pillars, hidden_by_pillar, branch_convert)'''
assert old2 in s, 'old2 not found'
s=s.replace(old2,new2)

io.open(p,'w',encoding='utf-8',newline='').write(s)
print('patched, branch_convert for ju installed')
