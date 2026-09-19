# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修复tier变量未定义的bug: 从yongshen_result中获取spectrum_tier
old = """        # V4.8: 天干忌神透干优先判断 (天干主动直接体现, 力量大于地支)
        # 如果天干是忌神(透干直接克用神/生忌神), 即使地支有喜神, 整体也偏忌
        gan_avoid_strong = ('GAN_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'GAN_PRIMARY_SHENG' in relations)
        # 身旺食伤泄秀为喜: 原局身旺, 大运食伤透干泄秀, 即使食伤克官用神, 也为喜
        # 需要判断原局是否身旺 (spectrum_tier)
        is_shenwang = tier in ['太旺', '旺极', '旺']"""

new = """        # V4.8: 天干忌神透干优先判断 (天干主动直接体现, 力量大于地支)
        # 如果天干是忌神(透干直接克用神/生忌神), 即使地支有喜神, 整体也偏忌
        gan_avoid_strong = ('GAN_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'GAN_PRIMARY_SHENG' in relations)
        # 身旺食伤泄秀为喜: 原局身旺, 大运食伤透干泄秀, 即使食伤克官用神, 也为喜
        # 需要判断原局是否身旺 (从yongshen_result中获取spectrum_tier)
        spectrum_tier = yongshen_result.get('spectrum_tier', '')
        is_shenwang = spectrum_tier in ['太旺', '旺极', '旺']"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('修复tier变量未定义bug: 从yongshen_result中获取spectrum_tier')
