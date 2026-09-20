# -*- coding: utf-8 -*-
"""V4.57: 收紧V4.51逻辑: 身旺财生官杀/比劫+食伤增加avoid检查(忌神大运即使符合结构也不判喜)"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改1: 身旺财生官杀为喜 - 增加avoid检查
old1 = """        # V4.51: 身旺财生官杀 - 身旺时, 大运天干财+地支官杀(财生官杀制比劫), 判喜(原典: 身旺喜财官)
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        shenwang_cai_sheng_guansha = (is_shenwang and gan_wx == _cai_wx_local and zhi_wx == _guansha_wx_local)"""

new1 = """        # V4.51: 身旺财生官杀 - 身旺时, 大运天干财+地支官杀(财生官杀制比劫), 判喜(原典: 身旺喜财官)
        # V4.57: 收紧 - 只有大运干支不在avoid列表中时才判喜(忌神大运即使符合结构也不判喜)
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        _cai_guansha_not_avoid = (_cai_wx_local not in avoid and _guansha_wx_local not in avoid)
        shenwang_cai_sheng_guansha = (is_shenwang and gan_wx == _cai_wx_local and zhi_wx == _guansha_wx_local and _cai_guansha_not_avoid)"""

# 修改2: 身旺比劫+食伤为喜 - 增加avoid检查
old2 = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2
                                     and dm_wx_local not in avoid and _shishang_wx_local2 not in avoid)"""

new2 = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        # V4.57: 已经有avoid检查,保持不变
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2
                                     and dm_wx_local not in avoid and _shishang_wx_local2 not in avoid)"""

changes = 0
if old1 in c:
    c = c.replace(old1, new1)
    changes += 1
    print('修改1成功: 身旺财生官杀增加avoid检查')
else:
    print('修改1未找到')

print(f'\n共修改{changes}处')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
