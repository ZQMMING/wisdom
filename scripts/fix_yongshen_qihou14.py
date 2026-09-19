# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.27: B0调候路径只排除真从(CONFIRMED)，不排除假从(CANDIDATE)
# 问题: QT-0734从官格CANDIDATE(假从)，B0调候路径被not (cong or cong_shun)排除了，导致走扶抑用金而非调候用丙火
old = """    if primary is None and hou and hou[0] and not (cong or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""

new = """    # V4.27: B0调候路径只排除真从(CONFIRMED)和cong_shun，不排除假从(CANDIDATE)
    _cong_confirmed = bool(cong) and (cong_state or '') == 'CONFIRMED'
    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.27完成(B0调候只排除真从，不排除假从)')
