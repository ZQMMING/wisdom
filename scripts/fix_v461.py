# -*- coding: utf-8 -*-
"""V4.61: 放松身衰比劫帮身avoid检查"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """        # V4.55: 身衰极时放松avoid检查(原典:身衰极喜比劫帮身,扶抑喜神优先级高于调候忌神)
        is_shenshuai_ji = spectrum_tier in ('衰极', '太衰')
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local
                                      and (dm_wx_local not in avoid or is_shenshuai_ji))"""

new = """        # V4.55: 身衰极时放松avoid检查(原典:身衰极喜比劫帮身,扶抑喜神优先级高于调候忌神)
        # V4.61: 放松 - 身衰(包括衰/衰极/太衰)时即使比劫在avoid列表中也判喜
        # 原典:身衰比劫帮身是扶抑层面的喜,不能被调候avoid覆盖,如壬申甲辰丙寅丙申丙午运
        is_shenshuai_ji = spectrum_tier in ('衰极', '太衰')
        shenshuai_bijie_bangshen = (is_shenshuai and gan_wx == dm_wx_local and zhi_wx == dm_wx_local)"""

if old in c:
    c = c.replace(old, new)
    print('V4.61修改成功')
else:
    print('未找到目标字符串')
    # 尝试查找类似的字符串
    import re
    m = re.search(r'shenshuai_bijie_bangshen = \(is_shenshuai.*?\)', c, re.DOTALL)
    if m:
        print(f'找到: {m.group(0)[:100]}')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
