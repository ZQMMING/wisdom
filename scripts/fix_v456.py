# -*- coding: utf-8 -*-
"""V4.56: 身衰极时调候用神是克泄则跳过调候路径(原典:身衰极优先扶抑,调候克泄会进一步削弱日主)"""
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """        # V4.38: 身旺命局中, 若调候用神是印星(生扶日主), 则跳过调候路径(扶抑用神应为克泄)
        # 原典: 身旺喜克泄, 调候用神若为生扶则与扶抑冲突, 应以扶抑为主
        _is_yin = hou[0] == SHENG_ME.get(dmw)
        _is_bijie = hou[0] == dmw
        _is_shengfu = _is_yin or _is_bijie
        _is_shenwang = tier in ('旺', '旺极', '太旺')
        if not (_is_shenwang and _is_shengfu):"""

new = """        # V4.38: 身旺命局中, 若调候用神是印星(生扶日主), 则跳过调候路径(扶抑用神应为克泄)
        # 原典: 身旺喜克泄, 调候用神若为生扶则与扶抑冲突, 应以扶抑为主
        _is_yin = hou[0] == SHENG_ME.get(dmw)
        _is_bijie = hou[0] == dmw
        _is_shengfu = _is_yin or _is_bijie
        _is_shenwang = tier in ('旺', '旺极', '太旺')
        # V4.56: 身衰极命局中, 若调候用神是克泄(官杀/食伤/财), 则跳过调候路径
        # 原典: 身衰极优先扶抑(印星比劫), 调候克泄会进一步削弱日主(如DT-0386火虚木嫩用木不用水)
        _is_guansha = hou[0] == KE_ME.get(dmw)
        _is_shishang = hou[0] == SHENG.get(dmw)
        _is_cai = hou[0] == KE.get(dmw)
        _is_kexie = _is_guansha or _is_shishang or _is_cai
        _is_shenshuai_ji = tier in ('衰极', '太衰')
        if not (_is_shenwang and _is_shengfu) and not (_is_shenshuai_ji and _is_kexie):"""

if old in c:
    c = c.replace(old, new)
    print('V4.56修改成功: 身衰极调候是克泄则跳过')
else:
    print('未找到目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
