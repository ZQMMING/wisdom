# -*- coding: utf-8 -*-
"""V4.50: 身衰财多身弱判忌(即使财星是用神/喜神); 身旺比劫+官杀时比劫盖头用神判忌"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在 shenshuai_bijie_bangshen 之后, 增加身衰财多身弱判断
old = """        # V4.49: 身衰比劫帮身为喜 - 身衰/衰极时, 大运干支皆比劫, 即使比劫不在secondary列表也判喜(原典: 身衰喜比劫帮身)
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local)
        
        if has_xi and has_ji:"""

new = """        # V4.49: 身衰比劫帮身为喜 - 身衰/衰极时, 大运干支皆比劫, 即使比劫不在secondary列表也判喜(原典: 身衰喜比劫帮身)
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local)
        # V4.50: 身衰财多身弱 - 身衰/衰极时, 大运干支皆财, 即使财星是用神/喜神也判忌(原典: 财多身弱)
        _cai_wx_local = KE.get(dm_wx_local, '')
        shenshuai_cai_duo_shen_ruo = (is_shenshuai and gan_wx == _cai_wx_local and zhi_wx == _cai_wx_local)
        
        if has_xi and has_ji:"""

if old in c:
    c = c.replace(old, new)
    print('V4.50变量添加成功')
else:
    print('未找到目标字符串1')

# 在优先级判断中, 增加身衰财多身弱
old2 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

new2 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.50: 身衰财多身弱判忌
            elif shenshuai_cai_duo_shen_ruo:
                xiji_label = 'SUPPRESS_USE_GOD'
            # V4.45: 官杀克身(身弱)优先判忌"""

if old2 in c:
    c = c.replace(old2, new2)
    print('V4.50优先级添加成功')
else:
    print('未找到目标字符串2')

# 只有 has_xi 时, 也需要检查身衰财多身弱
old3 = """            # V4.49: 身衰比劫帮身即使只有喜也判喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

new3 = """            # V4.49: 身衰比劫帮身即使只有喜也判喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.50: 身衰财多身弱即使只有喜也判忌
            elif shenshuai_cai_duo_shen_ruo:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

if old3 in c:
    c = c.replace(old3, new3)
    print('V4.50只有has_xi时的判断添加成功')
else:
    print('未找到目标字符串3')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('V4.50修改完成')
