# -*- coding: utf-8 -*-
"""V4.45: 增加比劫夺财、官杀克身等特殊判断"""
import re

p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在 shenwang_shishang_xiexiu 之后, if has_xi and has_ji 之前, 增加特殊判断
old = """        shenwang_shishang_xiexiu = (is_shenwang and gan_shishang and primary and KE.get(shishang_wx, '') == primary)
        
        if has_xi and has_ji:"""

new = """        shenwang_shishang_xiexiu = (is_shenwang and gan_shishang and primary and KE.get(shishang_wx, '') == primary)
        
        # V4.45: 比劫夺财 - 大运天干比劫坐财星且财星是用神/喜神时, 判忌(原典: 比劫夺财, 比劫坐财为忌)
        _cai_wx = KE.get(dm_wx_local, '')
        bijie_duocai = (gan_wx == dm_wx_local and zhi_wx == _cai_wx 
                        and ('ZHI_PRIMARY' in relations or 'ZHI_SECONDARY' in relations or 'GAN_PRIMARY' in relations))
        # V4.45: 官杀克身 - 大运干支皆官杀且身弱时, 判忌(原典: 官杀克身, 身弱忌官杀)
        _guansha_wx = KE_ME.get(dm_wx_local, '')
        guansha_keshen_shenruo = (gan_wx == _guansha_wx and zhi_wx == _guansha_wx and not is_shenwang)
        # V4.45: 食伤泄秀太过 - 大运干支皆食伤且身弱时, 判忌(原典: 食伤泄气太过, 身弱忌食伤)
        _shishang_wx = SHENG.get(dm_wx_local, '')
        shishang_xiexiu_taiguo = (gan_wx == _shishang_wx and zhi_wx == _shishang_wx and not is_shenwang)
        
        if has_xi and has_ji:"""

if old in c:
    c = c.replace(old, new)
    print('V4.45特殊判断添加成功')
else:
    print('未找到目标字符串1')

# 在 xiji_label 判断中, 增加特殊情况的优先级(在 shenwang_shishang_xiexiu 之后)
old2 = """        if has_xi and has_ji:
            # V4.8: 身旺食伤泄秀为喜优先
            if shenwang_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.8: 天干忌神透干优先 (天干主动力量大)
            elif gan_avoid_strong:
                xiji_label = 'SUPPRESS_USE_GOD'"""

new2 = """        if has_xi and has_ji:
            # V4.45: 比劫夺财优先判忌
            if bijie_duocai:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌
            elif guansha_keshen_shenruo:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 食伤泄秀太过(身弱)优先判忌
            elif shishang_xiexiu_taiguo:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.8: 身旺食伤泄秀为喜优先
            elif shenwang_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.8: 天干忌神透干优先 (天干主动力量大)
            elif gan_avoid_strong:
                xiji_label = 'SUPPRESS_USE_GOD'"""

if old2 in c:
    c = c.replace(old2, new2)
    print('V4.45优先级添加成功')
else:
    print('未找到目标字符串2')

# 只有 has_xi 时, 也需要检查比劫夺财等特殊情况
old3 = """        elif has_xi:
            xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:"""

new3 = """        elif has_xi:
            # V4.45: 比劫夺财即使只有喜也判忌
            if bijie_duocai:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'
        elif has_ji:"""

if old3 in c:
    c = c.replace(old3, new3)
    print('V4.45只有has_xi时的特殊判断添加成功')
else:
    print('未找到目标字符串3')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('V4.45修改完成')
