# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.22: 从财/从官/从杀格有印比透干且有根时不走从格路径，从儿格不受此限制
# 问题: QT-0137从财有印癸水透干且亥水为根，QT-0734从官有比劫壬水透干且辰为余气根
old = """    if cong or cong_shun:
        if '从财' in cong:"""

new = """    # V4.22: 从财/从官/从杀格有印比透干且有根时不走从格(假从真不化)，从儿格不受此限
    _yinbi_rooted = (stem(t['yin'])>=1 and (ben(t['yin'])>=1 or cs(t['yin']) or ling(t['yin']) in ('旺','相'))) \
        or (stem(t['bi'])>=1 and (ben(t['bi'])>=1 or cs(t['bi']) or ling(t['bi']) in ('旺','相')))
    _skip_cong = _yinbi_rooted and cong and ('从财' in cong or '从官' in cong or '从杀' in cong or '从煞' in cong)
    if (cong or cong_shun) and not _skip_cong:
        if '从财' in cong:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.22完成(从财/从官/从杀格有印比有根不走从格，从儿格不受限)')
