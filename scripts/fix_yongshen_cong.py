# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.12: 从格路径条件改用cong or cong_shun，确保所有从格都走从格路径
old = """    if cong_shun:
        if '从财' in cong:"""

new = """    if cong or cong_shun:
        if '从财' in cong:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.12完成(从格路径条件改用cong or cong_shun)')
