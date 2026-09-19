# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.21: 回退V4.20，从格路径条件改回cong or cong_shun
old = """    # V4.20: 有印比透干且有根时不走从格路径(假从真不化)，走正格
    _yinbi_rooted = (stem(t['yin'])>=1 and (ben(t['yin'])>=1 or cs(t['yin']) or ling(t['yin']) in ('旺','相'))) \
        or (stem(t['bi'])>=1 and (ben(t['bi'])>=1 or cs(t['bi']) or ling(t['bi']) in ('旺','相')))
    if (cong or cong_shun) and not _yinbi_rooted:"""

new = """    if cong or cong_shun:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.21完成(回退V4.20)')
