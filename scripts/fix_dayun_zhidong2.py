# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化: 地支需要引动 - 如果只有地支用神但没有引动关系, 则在has_xi和has_ji同时存在时优先选择has_ji
old = """        if has_xi and has_ji:
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            if primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

new = """        if has_xi and has_ji:
            # V4.6: 地支需要引动 - 如果只有地支用神但没有引动关系, 则优先选择has_ji(地支主静需要引动)
            if zhi_primary_only and not zhi_avoid_only:
                xiji_label = 'SUPPRESS_USE_GOD'
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            elif primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.5'", "'module': 'DAYUN_XIJI_V4.6'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.6完成(地支需要引动: 只有地支用神无引动时优先选择has_ji)')
