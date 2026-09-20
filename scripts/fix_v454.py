# -*- coding: utf-8 -*-
"""V4.54: 收紧V4.49/V4.51逻辑: 只有大运干支不在avoid列表中时才判喜"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改1: 身旺食伤泄秀为喜 - 增加avoid检查
old1 = """        # V4.49: 身旺食伤泄秀为喜 - 身旺/旺极时, 大运干支皆食伤, 即使食伤在avoid列表也判喜(原典: 身旺喜食伤泄秀)
        _shishang_wx_local = SHENG.get(dm_wx_local, '')
        shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local)"""

new1 = """        # V4.49: 身旺食伤泄秀为喜 - 身旺/旺极时, 大运干支皆食伤判喜(原典: 身旺喜食伤泄秀)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜(忌神大运即使身旺喜泄也不判喜)
        _shishang_wx_local = SHENG.get(dm_wx_local, '')
        shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local
                                         and _shishang_wx_local not in avoid)"""

# 修改2: 身衰比劫帮身为喜 - 增加avoid检查
old2 = """        # V4.49: 身衰比劫帮身为喜 - 身衰/衰极时, 大运干支皆比劫, 即使比劫不在secondary列表也判喜(原典: 身衰喜比劫帮身)
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local)"""

new2 = """        # V4.49: 身衰比劫帮身为喜 - 身衰/衰极时, 大运干支皆比劫判喜(原典: 身衰喜比劫帮身)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local
                                      and dm_wx_local not in avoid)"""

# 修改3: 身旺比劫+食伤为喜 - 增加avoid检查
old3 = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2)"""

new3 = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2
                                     and dm_wx_local not in avoid and _shishang_wx_local2 not in avoid)"""

changes = 0
if old1 in c:
    c = c.replace(old1, new1)
    changes += 1
    print('修改1成功: 身旺食伤泄秀增加avoid检查')
else:
    print('修改1未找到')

if old2 in c:
    c = c.replace(old2, new2)
    changes += 1
    print('修改2成功: 身衰比劫帮身增加avoid检查')
else:
    print('修改2未找到')

if old3 in c:
    c = c.replace(old3, new3)
    changes += 1
    print('修改3成功: 身旺比劫+食伤增加avoid检查')
else:
    print('修改3未找到')

print(f'\n共修改{changes}处')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
