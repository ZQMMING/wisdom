# -*- coding: utf-8 -*-
"""V4.51: 身旺财生官杀为喜; 身旺比劫+食伤为喜"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在 shenshuai_cai_duo_shen_ruo 之后, 增加身旺财生官杀和身旺比劫+食伤判断
old = """        # V4.50: 身衰财多身弱 - 身衰/衰极时, 大运干支皆财, 即使财星是用神/喜神也判忌(原典: 财多身弱)
        _cai_wx_local = KE.get(dm_wx_local, '')
        shenshuai_cai_duo_shen_ruo = (is_shenshuai and gan_wx == _cai_wx_local and zhi_wx == _cai_wx_local)
        
        if has_xi and has_ji:"""

new = """        # V4.50: 身衰财多身弱 - 身衰/衰极时, 大运干支皆财, 即使财星是用神/喜神也判忌(原典: 财多身弱)
        _cai_wx_local = KE.get(dm_wx_local, '')
        shenshuai_cai_duo_shen_ruo = (is_shenshuai and gan_wx == _cai_wx_local and zhi_wx == _cai_wx_local)
        # V4.51: 身旺财生官杀 - 身旺时, 大运天干财+地支官杀(财生官杀制比劫), 判喜(原典: 身旺喜财官)
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        shenwang_cai_sheng_guansha = (is_shenwang and gan_wx == _cai_wx_local and zhi_wx == _guansha_wx_local)
        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2)
        
        if has_xi and has_ji:"""

if old in c:
    c = c.replace(old, new)
    print('V4.51变量添加成功')
else:
    print('未找到目标字符串1')

# 在优先级判断中, 增加身旺财生官杀和身旺比劫+食伤
old2 = """            # V4.50: 身衰财多身弱判忌
            elif shenshuai_cai_duo_shen_ruo:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

new2 = """            # V4.50: 身衰财多身弱判忌
            elif shenshuai_cai_duo_shen_ruo:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.51: 身旺财生官杀为喜
            elif shenwang_cai_sheng_guansha:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.51: 身旺比劫+食伤为喜
            elif shenwang_bijie_shishang:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

if old2 in c:
    c = c.replace(old2, new2)
    print('V4.51优先级添加成功')
else:
    print('未找到目标字符串2')

# 只有 has_ji 时, 也需要检查身旺财生官杀和身旺比劫+食伤
old3 = """        elif has_ji:
            # V4.49: 身旺食伤泄秀为喜(即使只有忌也可能判喜)
            if shenwang_shishang_xiexiu_v2:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                # V4.37: 只有克泄直接判忌, 移除'用神强时克泄为喜'的激进逻辑(原典中克泄用神的运通常为忌)
                xiji_label = 'SUPPRESS_USE_GOD'"""

new3 = """        elif has_ji:
            # V4.49: 身旺食伤泄秀为喜(即使只有忌也可能判喜)
            if shenwang_shishang_xiexiu_v2:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.51: 身旺财生官杀为喜
            elif shenwang_cai_sheng_guansha:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.51: 身旺比劫+食伤为喜
            elif shenwang_bijie_shishang:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                # V4.37: 只有克泄直接判忌, 移除'用神强时克泄为喜'的激进逻辑(原典中克泄用神的运通常为忌)
                xiji_label = 'SUPPRESS_USE_GOD'"""

if old3 in c:
    c = c.replace(old3, new3)
    print('V4.51只有has_ji时的判断添加成功')
else:
    print('未找到目标字符串3')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('V4.51修改完成')
