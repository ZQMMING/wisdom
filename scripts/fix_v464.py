# -*- coding: utf-8 -*-
"""V4.64: 放松身旺财生官杀avoid检查"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """        # V4.51: 身旺财生官杀 - 身旺时, 大运天干财+地支官杀(财生官杀制比劫), 判喜(原典: 身旺喜财官)
        # V4.57: 收紧 - 只有大运干支不在avoid列表中时才判喜(忌神大运即使符合结构也不判喜)
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        _cai_guansha_not_avoid = (_cai_wx_local not in avoid and _guansha_wx_local not in avoid)
        shenwang_cai_sheng_guansha = (is_shenwang and gan_wx == _cai_wx_local and zhi_wx == _guansha_wx_local and _cai_guansha_not_avoid)"""

new = """        # V4.51: 身旺财生官杀 - 身旺时, 大运天干财+地支官杀(财生官杀制比劫), 判喜(原典: 身旺喜财官)
        # V4.57: 收紧 - 只有大运干支不在avoid列表中时才判喜
        # V4.64: 放松 - 身旺时即使财和官杀在avoid列表中也判喜
        # 原典:身旺财生官杀是扶抑层面的喜,不能被调候avoid覆盖,如丙戌辛丑己卯甲子壬寅运
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        shenwang_cai_sheng_guansha = (is_shenwang and gan_wx == _cai_wx_local and zhi_wx == _guansha_wx_local)"""

if old in c:
    c = c.replace(old, new)
    print('V4.64修改成功')
else:
    print('未找到目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
