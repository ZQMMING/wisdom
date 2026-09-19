# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.8: 天干忌神透干优先判断 + 身旺食伤泄秀为喜
old = """        if has_xi and has_ji:
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            if primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

new = """        # V4.8: 天干忌神透干优先判断 (天干主动直接体现, 力量大于地支)
        # 如果天干是忌神(透干直接克用神/生忌神), 即使地支有喜神, 整体也偏忌
        gan_avoid_strong = ('GAN_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or 'GAN_PRIMARY_SHENG' in relations)
        # 身旺食伤泄秀为喜: 原局身旺, 大运食伤透干泄秀, 即使食伤克官用神, 也为喜
        # 需要判断原局是否身旺 (spectrum_tier)
        is_shenwang = tier in ['太旺', '旺极', '旺']
        shishang_wx = SHENG.get(dm_wx_local, '')  # 食伤五行
        gan_shishang = (gan_wx == shishang_wx)
        shenwang_shishang_xiexiu = (is_shenwang and gan_shishang and primary and KE.get(shishang_wx, '') == primary)
        
        if has_xi and has_ji:
            # V4.8: 身旺食伤泄秀为喜优先
            if shenwang_shishang_xiexiu:
                xiji_label = 'SUPPORT_USE_GOD'
            # V4.8: 天干忌神透干优先 (天干主动力量大)
            elif gan_avoid_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            elif primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.7'", "'module': 'DAYUN_XIJI_V4.8'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.8完成(天干忌神透干优先判断+身旺食伤泄秀为喜)')
