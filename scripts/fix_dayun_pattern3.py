# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化印格用官中财运反吉的判断, 增加大运藏干中财的判断
old = """        # 印格用官: 财运反吉(财生官→官生印)
        if is_yin_yongguan:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True"""

new = """        # 印格用官: 财运反吉(财生官→官生印), 包括大运藏干中的财
        if is_yin_yongguan:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True
            else:
                # 检查大运藏干中是否有财
                for h in zhi_hidden:
                    if WX.get(h, '') == cai_wx:
                        pattern_xi = True
                        break"""
c = c.replace(old, new)

# 优化阳刃格中财乡为喜的判断, 增加大运藏干中财的判断
old2 = """        # 阳刃格: 财乡为喜(财生官煞制刃)
        if is_yangren_month:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True"""
new2 = """        # 阳刃格: 财乡为喜(财生官煞制刃), 包括大运藏干中的财
        if is_yangren_month:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True
            else:
                # 检查大运藏干中是否有财
                for h in zhi_hidden:
                    if WX.get(h, '') == cai_wx:
                        pattern_xi = True
                        break"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.9'", "'module': 'DAYUN_XIJI_V4.0'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.0完成(优化印格用官/阳刃格中财运反吉,增加大运藏干中财的判断)')
