# -*- coding: utf-8 -*-
"""V4.55: 身衰极时扶抑喜神优先级高于调候忌神(原典:身衰极喜比劫帮身/食伤泄秀,即使在调候avoid中也判喜)"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改1: 身旺食伤泄秀为喜 - 身旺时保持avoid检查
old1 = """        # V4.49: 身旺食伤泄秀为喜 - 身旺/旺极时, 大运干支皆食伤判喜(原典: 身旺喜食伤泄秀)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜(忌神大运即使身旺喜泄也不判喜)
        _shishang_wx_local = SHENG.get(dm_wx_local, '')
        shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local
                                         and _shishang_wx_local not in avoid)"""

new1 = """        # V4.49: 身旺食伤泄秀为喜 - 身旺/旺极时, 大运干支皆食伤判喜(原典: 身旺喜食伤泄秀)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜(忌神大运即使身旺喜泄也不判喜)
        _shishang_wx_local = SHENG.get(dm_wx_local, '')
        shenwang_shishang_xiexiu_v2 = (is_shenwang and gan_wx == _shishang_wx_local and zhi_wx == _shishang_wx_local
                                         and _shishang_wx_local not in avoid)"""

# 修改2: 身衰比劫帮身为喜 - 身衰极时放松avoid检查(原典:身衰极喜比劫帮身,即使在调候avoid中也判喜)
old2 = """        # V4.49: 身衰比劫帮身为喜 - 身衰/衰极时, 大运干支皆比劫判喜(原典: 身衰喜比劫帮身)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local
                                      and dm_wx_local not in avoid)"""

new2 = """        # V4.49: 身衰比劫帮身为喜 - 身衰/衰极时, 大运干支皆比劫判喜(原典: 身衰喜比劫帮身)
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        # V4.55: 身衰极时放松avoid检查(原典:身衰极喜比劫帮身,扶抑喜神优先级高于调候忌神)
        is_shenshuai_ji = spectrum_tier in ('衰极', '太衰')
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local
                                      and (dm_wx_local not in avoid or is_shenshuai_ji))"""

# 修改3: 身旺比劫+食伤为喜 - 保持avoid检查
old3 = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2
                                     and dm_wx_local not in avoid and _shishang_wx_local2 not in avoid)"""

new3 = """        # V4.51: 身旺比劫+食伤 - 身旺时, 大运天干比劫+地支食伤(比劫帮身+食伤泄秀), 判喜
        # V4.54: 收紧 - 只有大运干支不在avoid列表中时才判喜
        _shishang_wx_local2 = SHENG.get(dm_wx_local, '')
        shenwang_bijie_shishang = (is_shenwang and gan_wx == dm_wx_local and zhi_wx == _shishang_wx_local2
                                     and dm_wx_local not in avoid and _shishang_wx_local2 not in avoid)"""

# 修改4: 身衰极食伤泄秀为喜 - 新增(原典:身衰极时食伤运也可能是喜,因为食伤生财财生官杀官杀生印印生身)
# 在shenshuai_bijie_bangshen后面添加
old4 = """        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local
                                      and (dm_wx_local not in avoid or is_shenshuai_ji))"""

new4 = """        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local
                                      and (dm_wx_local not in avoid or is_shenshuai_ji))
        # V4.55: 身衰极食伤泄秀为喜 - 身衰极时, 大运干支皆食伤也判喜(原典:身衰极食伤生财财生官杀官杀生印印生身,流通有情)
        _shishang_wx_local3 = SHENG.get(dm_wx_local, '')
        shenshuai_shishang_xiexiu = (is_shenshuai_ji and gan_wx == _shishang_wx_local3 and zhi_wx == _shishang_wx_local3)"""

# 修改5: 在has_ji分支中添加shenshuai_shishang_xiexiu判喜
old5 = """        elif has_ji:
            # V4.49: 身旺食伤泄秀为喜(即使只有忌也可能判喜)
            if shenwang_shishang_xiexiu_v2:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'"""

new5 = """        elif has_ji:
            # V4.49: 身旺食伤泄秀为喜(即使只有忌也可能判喜)
            if shenwang_shishang_xiexiu_v2:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.55: 身衰极食伤泄秀为喜
            elif shenshuai_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'"""

# 修改6: 在has_xi and has_ji分支中也添加shenshuai_shishang_xiexiu判喜
old6 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.50: 身衰财多身弱判忌"""

new6 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.55: 身衰极食伤泄秀为喜
            elif shenshuai_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.50: 身衰财多身弱判忌"""

changes = 0
for i, (old, new, name) in enumerate([
    (old2, new2, '修改2: 身衰比劫帮身身衰极放松avoid'),
    (old4, new4, '修改4: 新增身衰极食伤泄秀为喜'),
    (old5, new5, '修改5: has_ji分支添加身衰极食伤泄秀'),
    (old6, new6, '修改6: has_xi_and_has_ji分支添加身衰极食伤泄秀'),
]):
    if old in c:
        c = c.replace(old, new)
        changes += 1
        print(f'{name}成功')
    else:
        print(f'{name}未找到')

print(f'\n共修改{changes}处')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
