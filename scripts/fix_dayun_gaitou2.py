# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.8: 盖头截脚精细判断 + 身旺食伤泄秀为喜
# 在xiji_label判断逻辑前增加盖头截脚判断
old = """        if has_xi and has_ji:
            # 生扶和克泄同时存在: 用神弱则生扶, 用神强则克泄, 否则生扶优先
            if primary_weak:
                xiji_label = 'SUPPORT_USE_GOD'
            elif primary_strong:
                xiji_label = 'SUPPRESS_USE_GOD'
            else:
                xiji_label = 'SUPPORT_USE_GOD'"""

new = """        # V4.8: 盖头截脚精细判断
        # 盖头: 天干克地支 (如癸未运, 癸水克未土财), 地支喜神力量大减
        # 截脚: 地支克天干 (如丁亥运, 亥水克丁火食伤), 天干喜神力量大减
        gan_ke_zhi = (gan_wx and zhi_wx and KE.get(gan_wx, '') == zhi_wx)
        zhi_ke_gan = (gan_wx and zhi_wx and KE.get(zhi_wx, '') == gan_wx)
        # 天干是忌神且盖头地支喜神: 整体偏忌
        gan_avoid_gaitou = (('GAN_AVOID' in relations or 'GAN_KE_PRIMARY' in relations) and gan_ke_zhi 
                            and ('ZHI_PRIMARY' in relations or hidden_primary_any))
        # 地支是忌神且截脚天干喜神: 整体偏忌
        zhi_avoid_jiejiao = (('ZHI_AVOID' in relations or hidden_avoid_any) and zhi_ke_gan 
                             and ('GAN_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations))
        
        if has_xi and has_ji:
            # V4.8: 盖头截脚优先判断
            if gan_avoid_gaitou or zhi_avoid_jiejiao:
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
print('dayun_xiji.py V4.8完成(盖头截脚精细判断: 天干忌神盖头地支喜神或地支忌神截脚天干喜神时整体偏忌)')
