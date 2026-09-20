# -*- coding: utf-8 -*-
"""V4.53: 地支用神得地+天干非忌神时判喜(原典:地支用神得地,天干不克用神则喜)"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """            # V4.41: 生扶和克泄同时存在时, 克泄优先(原典中克泄用神的运通常为忌, 生扶仅在用神极弱时为喜)
            elif primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                xiji_label = 'SUPPRESS_USE_GOD'"""

new = """            # V4.41: 生扶和克泄同时存在时, 克泄优先(原典中克泄用神的运通常为忌, 生扶仅在用神极弱时为喜)
            elif primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.53: 地支用神得地+天干非忌神时判喜(原典:地支用神得地,天干不克用神则喜)
            elif ('ZHI_PRIMARY' in relations and 'GAN_AVOID' not in relations 
                  and 'GAN_KE_PRIMARY' not in relations and 'GAN_PRIMARY_SHENG' not in relations):
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                xiji_label = 'SUPPRESS_USE_GOD'"""

if old in c:
    c = c.replace(old, new)
    print('V4.53修改成功')
else:
    print('未找到目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
