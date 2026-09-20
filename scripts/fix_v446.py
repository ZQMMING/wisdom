# -*- coding: utf-8 -*-
"""V4.46: 天干用神优先于地支忌神; 比劫盖头用神判忌"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在 shenwang_shishang_xiexiu 之后, 增加天干用神优先和比劫盖头判断
old = """        # V4.45: 食伤泄秀太过 - 大运干支皆食伤且身弱时, 判忌(原典: 食伤泄气太过, 身弱忌食伤)
        _shishang_wx = SHENG.get(dm_wx_local, '')
        shishang_xiexiu_taiguo = (gan_wx == _shishang_wx and zhi_wx == _shishang_wx and not is_shenwang)
        
        if has_xi and has_ji:"""

new = """        # V4.45: 食伤泄秀太过 - 大运干支皆食伤且身弱时, 判忌(原典: 食伤泄气太过, 身弱忌食伤)
        _shishang_wx = SHENG.get(dm_wx_local, '')
        shishang_xiexiu_taiguo = (gan_wx == _shishang_wx and zhi_wx == _shishang_wx and not is_shenwang)
        
        # V4.46: 天干用神优先 - 天干透用神且天干不是忌神时, 优先判喜(原典: 天干主动力量大于地支)
        gan_primary_strong = ('GAN_PRIMARY' in relations and 'GAN_AVOID' not in relations 
                               and 'GAN_KE_PRIMARY' not in relations and 'GAN_PRIMARY_SHENG' not in relations)
        # V4.46: 比劫盖头用神 - 天干比劫+地支用神时, 判忌(原典: 比劫盖头, 用神无力)
        bijie_gaitou_primary = (gan_wx == dm_wx_local and 'ZHI_PRIMARY' in relations 
                                 and 'GAN_PRIMARY' not in relations and 'GAN_AVOID' not in relations)
        
        if has_xi and has_ji:"""

if old in c:
    c = c.replace(old, new)
    print('V4.46变量添加成功')
else:
    print('未找到目标字符串1')

# 在优先级判断中, 增加天干用神优先和比劫盖头
old2 = """        if has_xi and has_ji:
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
                xiji_label = 'SUPPORT_USE_GOD'"""

new2 = """        if has_xi and has_ji:
            # V4.45: 比劫夺财优先判忌
            if bijie_duocai:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.46: 比劫盖头用神判忌
            elif bijie_gaitou_primary:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌
            elif guansha_keshen_shenruo:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 食伤泄秀太过(身弱)优先判忌
            elif shishang_xiexiu_taiguo:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.46: 天干用神优先判喜(天干透用神力量大于地支忌神)
            elif gan_primary_strong:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.8: 身旺食伤泄秀为喜优先
            elif shenwang_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'"""

if old2 in c:
    c = c.replace(old2, new2)
    print('V4.46优先级添加成功')
else:
    print('未找到目标字符串2')

# 只有 has_xi 时, 也需要检查比劫盖头
old3 = """        elif has_xi:
            # V4.45: 比劫夺财即使只有喜也判忌
            if bijie_duocai:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

new3 = """        elif has_xi:
            # V4.45: 比劫夺财即使只有喜也判忌
            if bijie_duocai:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.46: 比劫盖头用神即使只有喜也判忌
            elif bijie_gaitou_primary:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

if old3 in c:
    c = c.replace(old3, new3)
    print('V4.46只有has_xi时的判断添加成功')
else:
    print('未找到目标字符串3')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('V4.46修改完成')
