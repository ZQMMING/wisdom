# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修复天干五行关系: if-elif链改为多个独立if判断
old = """        # 天干五行关系
        if gan_wx == primary:
            relations.append('GAN_PRIMARY')
        elif gan_wx in secondary:
            relations.append('GAN_SECONDARY')
        elif gan_wx in avoid:
            relations.append('GAN_AVOID')
        elif SHENG.get(gan_wx) == primary:
            relations.append('GAN_SHENG_PRIMARY')  # 大运生用神
        elif SHENG_ME.get(gan_wx) == primary:
            relations.append('GAN_PRIMARY_SHENG')  # 用神生大运(泄用神)
        elif KE.get(gan_wx) == primary:
            relations.append('GAN_KE_PRIMARY')  # 大运克用神
        
        # 地支五行关系
        if zhi_wx == primary:
            relations.append('ZHI_PRIMARY')
        elif zhi_wx in secondary:
            relations.append('ZHI_SECONDARY')
        elif zhi_wx in avoid:
            relations.append('ZHI_AVOID')"""

new = """        # 天干五行关系 (V3.6修复: 改为多个独立if判断, 允许同时具有多种关系属性)
        if gan_wx == primary:
            relations.append('GAN_PRIMARY')
        if gan_wx in secondary:
            relations.append('GAN_SECONDARY')
        if gan_wx in avoid:
            relations.append('GAN_AVOID')
        if SHENG.get(gan_wx) == primary:
            relations.append('GAN_SHENG_PRIMARY')  # 大运生用神
        if SHENG_ME.get(gan_wx) == primary:
            relations.append('GAN_PRIMARY_SHENG')  # 用神生大运(泄用神)
        if KE.get(gan_wx) == primary:
            relations.append('GAN_KE_PRIMARY')  # 大运克用神
        
        # 地支五行关系 (V3.6修复: 改为多个独立if判断)
        if zhi_wx == primary:
            relations.append('ZHI_PRIMARY')
        if zhi_wx in secondary:
            relations.append('ZHI_SECONDARY')
        if zhi_wx in avoid:
            relations.append('ZHI_AVOID')"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.5'", "'module': 'DAYUN_XIJI_V3.6'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.6修复完成(天干地支五行关系if-elif链改为多个独立if判断)')
