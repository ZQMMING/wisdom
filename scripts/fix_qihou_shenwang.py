# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')
        # V4.36: 调候路径同步设置忌神(克调候用神的五行为忌), 避免avoid为空导致大运喜忌误判
        _ke_of_hou = KE_ME.get(hou[0])
        if _ke_of_hou:
            A(_ke_of_hou,'克调候用神为忌')"""

new = """    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        # V4.38: 身旺命局中, 若调候用神是印星(生扶日主), 则跳过调候路径(扶抑用神应为克泄)
        # 原典: 身旺喜克泄, 调候用神若为生扶则与扶抑冲突, 应以扶抑为主
        _is_yin = hou[0] == SHENG_ME.get(dmw)
        _is_shenwang = tier in ('旺', '旺极', '太旺')
        if not (_is_shenwang and _is_yin):
            P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')
            # V4.36: 调候路径同步设置忌神(克调候用神的五行为忌), 避免avoid为空导致大运喜忌误判
            _ke_of_hou = KE_ME.get(hou[0])
            if _ke_of_hou:
                A(_ke_of_hou,'克调候用神为忌')"""

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.38完成: 身旺调候印星跳过')
