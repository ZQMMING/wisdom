# -*- coding: utf-8 -*-
"""V4.65修正: 在两个分支中增加shenshuai_shishang_bijie判断"""
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在has_xi and has_ji分支中增加
old1 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.55: 身衰极食伤泄秀为喜"""

new1 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.65: 身衰食伤+比劫为喜
            elif shenshuai_shishang_bijie:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.55: 身衰极食伤泄秀为喜"""

if old1 in c:
    c = c.replace(old1, new1)
    print('has_xi and has_ji分支修改成功')
else:
    print('未找到has_xi and has_ji目标字符串')

# 在has_ji only分支中增加
old2 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.55: 身衰极食伤泄秀为喜
            elif shenshuai_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.51: 身旺财生官杀为喜"""

new2 = """            # V4.49: 身衰比劫帮身为喜
            elif shenshuai_bijie_bangshen:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.65: 身衰食伤+比劫为喜
            elif shenshuai_shishang_bijie:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.55: 身衰极食伤泄秀为喜
            elif shenshuai_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.51: 身旺财生官杀为喜"""

if old2 in c:
    c = c.replace(old2, new2)
    print('has_ji only分支修改成功')
else:
    print('未找到has_ji only目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
