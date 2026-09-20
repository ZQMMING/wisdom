# -*- coding: utf-8 -*-
"""V4.49: 身旺食伤泄秀为喜(即使食伤在avoid列表); 身衰比劫帮身为喜"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在 shenshuai_guansha_keshen 之后, 增加身旺食伤泄秀和身衰比劫帮身判断
old = """        # V4.48: 身衰极官杀克身 - 日主衰极/太衰时, 官杀克身即使官杀是用神也判忌(原典: 身衰不能承受官杀)
        is_shenshuai = spectrum_tier in ('衰极', '太衰', '衰')
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        shenshuai_guansha_keshen = (is_shenshuai and 
                                     (gan_wx == _guansha_wx_local or zhi_wx == _guansha_wx_local) and
                                     ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations))
        
        if has_xi and has_ji:"""

new = """        # V4.48: 身衰极官杀克身 - 日主衰极/太衰时, 官杀克身即使官杀是用神也判忌(原典: 身衰不能承受官杀)
        is_shenshuai = spectrum_tier in ('衰极', '太衰', '衰')
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        shenshuai_guansha_keshen = (is_shenshuai and 
                                     (gan_wx == _guansha_wx_local or zhi_wx == _guansha_wx_local) and
                                     ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations))
        # V4.49: 身旺食伤泄秀为喜 - 身旺/旺极时, 大运干支皆食伤, 即使食伤在avoid列表也判喜(原典: 身旺喜食伤泄秀)
        _shishang_wx_local = SHENG.get(dm_wx_local, '')
        shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local
                                         and 'GAN_AVOID' not in relations and 'ZHI_AVOID' not in relations)
        # V4.49: 身衰比劫帮身为喜 - 身衰/衰极时, 大运干支皆比劫, 即使比劫不在secondary列表也判喜(原典: 身衰喜比劫帮身)
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local
                                     and 'GAN_AVOID' not in relations and 'ZHI_AVOID' not in relations)
        
        if has_xi and has_ji:"""

if old in c:
    c = c.replace(old, new)
    print('V4.49变量添加成功')
else:
    print('未找到目标字符串1')

# 在优先级判断中, 增加身旺食伤泄秀和身衰比劫帮身
old2 = """            # V4.48: 身衰极官杀克身判忌
            elif shenshuai_guansha_keshen:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

new2 = """            # V4.48: 身衰极官杀克身判忌
            elif shenshuai_guansha_keshen:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.49: 身旺食伤泄秀为喜
            elif shenwang_shishang_xiexiu_v2:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

if old2 in c:
    c = c.replace(old2, new2)
    print('V4.49优先级添加成功')
else:
    print('未找到目标字符串2')

# 只有 has_ji 时, 也需要检查身旺食伤泄秀和身衰比劫帮身
old3 = """        elif has_ji:
            # V4.37: 只有克泄直接判忌, 移除'用神强时克泄为喜'的激进逻辑(原典中克泄用神的运通常为忌)
            xiji_label = 'SUPPRESS_USE_GOD'"""

new3 = """        elif has_ji:
            # V4.49: 身旺食伤泄秀为喜(即使只有忌也可能判喜)
            if shenwang_shishang_xiexiu_v2:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                # V4.37: 只有克泄直接判忌, 移除'用神强时克泄为喜'的激进逻辑(原典中克泄用神的运通常为忌)
                xiji_label = 'SUPPRESS_USE_GOD'"""

if old3 in c:
    c = c.replace(old3, new3)
    print('V4.49只有has_ji时的判断添加成功')
else:
    print('未找到目标字符串3')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('V4.49修改完成')
