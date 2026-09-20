# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""

new = """    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')
        # V4.36: 调候路径同步设置忌神(克调候用神的五行为忌), 避免avoid为空导致大运喜忌误判
        _ke_of_hou = KE_ME.get(hou[0])
        if _ke_of_hou:
            A(_ke_of_hou,'克调候用神为忌')"""

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.36完成: 调候路径设置忌神')
