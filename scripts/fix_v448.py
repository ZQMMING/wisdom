# -*- coding: utf-8 -*-
"""V4.48: 身衰极官杀克身判忌; 用神为空时不默认判忌"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在 bijie_gaitou_primary 之后, 增加身衰极官杀克身判断
old = """        # V4.46: 比劫盖头用神 - 天干比劫+地支用神时, 判忌(原典: 比劫盖头, 用神无力)
        bijie_gaitou_primary = (gan_wx == dm_wx_local and 'ZHI_PRIMARY' in relations 
                                 and 'GAN_PRIMARY' not in relations and 'GAN_AVOID' not in relations)
        
        if has_xi and has_ji:"""

new = """        # V4.46: 比劫盖头用神 - 天干比劫+地支用神时, 判忌(原典: 比劫盖头, 用神无力)
        bijie_gaitou_primary = (gan_wx == dm_wx_local and 'ZHI_PRIMARY' in relations 
                                 and 'GAN_PRIMARY' not in relations and 'GAN_AVOID' not in relations)
        # V4.48: 身衰极官杀克身 - 日主衰极/太衰时, 官杀克身即使官杀是用神也判忌(原典: 身衰不能承受官杀)
        is_shenshuai = tier in ('衰极', '太衰', '衰')
        _guansha_wx_local = KE_ME.get(dm_wx_local, '')
        shenshuai_guansha_keshen = (is_shenshuai and 
                                     (gan_wx == _guansha_wx_local or zhi_wx == _guansha_wx_local) and
                                     ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations))
        
        if has_xi and has_ji:"""

if old in c:
    c = c.replace(old, new)
    print('V4.48变量添加成功')
else:
    print('未找到目标字符串1')

# 在优先级判断中, 增加身衰极官杀克身
old2 = """            # V4.46: 比劫盖头用神判忌
            elif bijie_gaitou_primary:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

new2 = """            # V4.46: 比劫盖头用神判忌
            elif bijie_gaitou_primary:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.48: 身衰极官杀克身判忌
            elif shenshuai_guansha_keshen:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

if old2 in c:
    c = c.replace(old2, new2)
    print('V4.48优先级添加成功')
else:
    print('未找到目标字符串2')

# 只有 has_xi 时, 也需要检查身衰极官杀克身
old3 = """            # V4.46: 比劫盖头用神即使只有喜也判忌
            elif bijie_gaitou_primary:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

new3 = """            # V4.46: 比劫盖头用神即使只有喜也判忌
            elif bijie_gaitou_primary:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.48: 身衰极官杀克身即使只有喜也判忌
            elif shenshuai_guansha_keshen:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

if old3 in c:
    c = c.replace(old3, new3)
    print('V4.48只有has_xi时的判断添加成功')
else:
    print('未找到目标字符串3')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('V4.48修改完成')
