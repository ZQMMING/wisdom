# -*- coding: utf-8 -*-
"""V4.65: 增加身衰食伤+比劫为喜的逻辑"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """        # V4.61: 放松 - 身衰(包括衰/衰极/太衰)时即使比劫在avoid列表中也判喜
        # 原典:身衰比劫帮身是扶抑层面的喜,不能被调候avoid覆盖,如壬申甲辰丙寅丙申丙午运
        is_shenshuai_ji = spectrum_tier in ('衰极', '太衰')
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local)"""

new = """        # V4.61: 放松 - 身衰(包括衰/衰极/太衰)时即使比劫在avoid列表中也判喜
        # 原典:身衰比劫帮身是扶抑层面的喜,不能被调候avoid覆盖,如壬申甲辰丙寅丙申丙午运
        is_shenshuai_ji = spectrum_tier in ('衰极', '太衰')
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local)
        # V4.65: 身衰食伤+比劫为喜 - 身衰时, 大运天干食伤+地支比劫(比劫帮身为主,食伤泄秀为辅), 判喜
        # 原典:身衰喜比劫帮身,即使天干是食伤也不影响比劫帮身的喜,如癸亥癸亥丙辰甲午戊午运
        _shishang_wx_local3 = SHENG.get(dm_wx_local, '')
        shenshuai_shishang_bijie = (is_shenshuai and gan_wx == _shishang_wx_local3 and zhi_wx == dm_wx_local)"""

if old in c:
    c = c.replace(old, new)
    print('V4.65修改成功')
else:
    print('未找到目标字符串')

# 在has_xi的判断中增加shenshuai_shishang_bijie
old2 = "shenshuai_bijie_bangshen or shenwang_cai_sheng_guansha or shenwang_bijie_shishang"
new2 = "shenshuai_bijie_bangshen or shenshuai_shishang_bijie or shenwang_cai_sheng_guansha or shenwang_bijie_shishang"
if old2 in c:
    c = c.replace(old2, new2)
    print('has_xi增加shenshuai_shishang_bijie成功')
else:
    print('未找到has_xi目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
