# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.18: 从格路径只有真从(CONFIRMED)才走，假从(CANDIDATE)走正格
# 问题: QT-0137/QT-0734都是假从(CANDIDATE)，有印比透干有根，不应走从格路径
old = """    if cong or cong_shun:"""

new = """    # V4.18: 只有真从(CONFIRMED)才走从格路径，假从(CANDIDATE)走正格(有印比透干有根)
    _cong_real = bool(cong) and (cong_state or '') == 'CONFIRMED'
    if _cong_real or cong_shun:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.18完成(从格路径只有真从CONFIRMED才走，假从走正格)')
