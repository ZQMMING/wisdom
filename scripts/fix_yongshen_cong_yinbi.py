# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.20: 从格路径增加印比有根判断：有印比透干且有根时不走从格路径，走正格
# 问题: QT-0137有印癸水透干且亥水为根，QT-0734有比劫壬水透干且辰为余气根，都不应从
old = """    if cong or cong_shun:"""

new = """    # V4.20: 有印比透干且有根时不走从格路径(假从真不化)，走正格
    _yinbi_rooted = (stem(t['yin'])>=1 and (ben(t['yin'])>=1 or cs(t['yin']) or ling(t['yin']) in ('旺','相'))) \
        or (stem(t['bi'])>=1 and (ben(t['bi'])>=1 or cs(t['bi']) or ling(t['bi']) in ('旺','相')))
    if (cong or cong_shun) and not _yinbi_rooted:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.20完成(从格路径增加印比有根判断，有印比有根不走从格)')
