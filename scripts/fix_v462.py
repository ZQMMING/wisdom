# -*- coding: utf-8 -*-
"""V4.62: 放松身旺(包括旺/旺极/太旺)食伤泄秀avoid检查"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """        # V4.49: 身旺食伤泄秀为喜 - 身旺/旺极时, 大运干支皆食伤判喜(原典: 身旺喜食伤泄秀)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜(忌神大运即使身旺喜泄也不判喜)
        # V4.59: 放松 - 身旺极时即使食伤在avoid列表中也判喜(原典:身旺极食伤泄秀是扶抑层面的喜,不能被调候avoid覆盖,如壬子辛亥壬子癸卯乙卯运)
        _shishang_wx_local = SHENG.get(dm_wx_local, '')
        is_shenwang_ji = spectrum_tier in ('旺极',)
        shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local
                                         and (_shishang_wx_local not in avoid or is_shenwang_ji))"""

new = """        # V4.49: 身旺食伤泄秀为喜 - 身旺/旺极时, 大运干支皆食伤判喜(原典: 身旺喜食伤泄秀)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜(忌神大运即使身旺喜泄也不判喜)
        # V4.59: 放松 - 身旺极时即使食伤在avoid列表中也判喜
        # V4.62: 放松 - 身旺(包括旺/旺极/太旺)时即使食伤在avoid列表中也判喜
        # 原典:身旺食伤泄秀是扶抑层面的喜,不能被调候avoid覆盖,如壬辰壬子壬子癸卯乙卯运
        _shishang_wx_local = SHENG.get(dm_wx_local, '')
        shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local)"""

if old in c:
    c = c.replace(old, new)
    print('V4.62修改成功')
else:
    print('未找到目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
