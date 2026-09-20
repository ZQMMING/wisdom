# -*- coding: utf-8 -*-
"""V4.63: 放松身旺比劫+食伤avoid检查"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2
                                     and dm_wx_local not in avoid and _shishang_wx_local2 not in avoid)"""

new = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        # V4.63: 放松 - 身旺时即使比劫和食伤在avoid列表中也判喜
        # 原典:身旺比劫帮身+食伤泄秀是扶抑层面的喜,不能被调候avoid覆盖,如己丑丙子辛酉壬辰癸酉运
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2)"""

if old in c:
    c = c.replace(old, new)
    print('V4.63修改成功')
else:
    print('未找到目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
