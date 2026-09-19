# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.30: _yinbi_rooted增加余气根检查
old = """    # V4.22: 从财/从官/从杀格有印比透干且有根时不走从格(假从真不化)，从儿格不受此限
    _yinbi_rooted = (stem(t['yin'])>=1 and (ben(t['yin'])>=1 or cs(t['yin']) or ling(t['yin']) in ('旺','相')))         or (stem(t['bi'])>=1 and (ben(t['bi'])>=1 or cs(t['bi']) or ling(t['bi']) in ('旺','相')))"""

new = """    # V4.30: 从财/从官/从杀格有印比透干且有根(本气/余气)时不走从格(假从真不化)，从儿格不受此限
    _yinbi_rooted = (stem(t['yin'])>=1 and (ben(t['yin'])>=1 or cs(t['yin']) or ling(t['yin']) in ('旺','相') or int(d(t['yin']).get('yu_n',0))>=1)) \\
                     or (stem(t['bi'])>=1 and (ben(t['bi'])>=1 or cs(t['bi']) or ling(t['bi']) in ('旺','相') or int(d(t['bi']).get('yu_n',0))>=1))"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.30完成(_yinbi_rooted增加余气根检查)')
