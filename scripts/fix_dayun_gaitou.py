# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在has_xi/has_ji条件中增加盖头截脚+天干地支配合的判断
old = """        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi or pattern_xi)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations or pattern_ji)"""

new = """        # V4.1: 盖头截脚+天干地支配合判断 (基于滴天髓岁运章)
        # 天干生地支而荫厚(吉), 地支生天干而气泄(力减)
        # 盖头: 天干克地支(吉凶减半), 截脚: 地支克天干(十年皆否)
        ganzhi_relation = ''
        if gan_wx and zhi_wx:
            if SHENG.get(gan_wx) == zhi_wx:  # 天干生地支
                ganzhi_relation = 'TIANGAN_SHENG_DIZHI'  # 荫厚
            elif SHENG.get(zhi_wx) == gan_wx:  # 地支生天干
                ganzhi_relation = 'DIZHI_SHENG_TIANGAN'  # 气泄
            elif KE.get(gan_wx) == zhi_wx:  # 天干克地支(盖头)
                ganzhi_relation = 'GAITOU'
            elif KE.get(zhi_wx) == gan_wx:  # 地支克天干(截脚)
                ganzhi_relation = 'JIEJIAO'
        
        # 如果大运天干是用神, 但地支生天干(气泄), 则用神力量大减, has_xi可能被覆盖
        use_god_qi_xie = False
        if primary and gan_wx == primary and ganzhi_relation == 'DIZHI_SHENG_TIANGAN':
            use_god_qi_xie = True
        # 如果大运地支是用神, 但天干克地支(盖头), 则用神力量减半
        use_god_gaitou = False
        if primary and zhi_wx == primary and ganzhi_relation == 'GAITOU':
            use_god_gaitou = True
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi or pattern_xi)
        # 用神气泄或盖头: has_xi被覆盖(用神力量大减)
        if use_god_qi_xie or use_god_gaitou:
            has_xi = False
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations or pattern_ji or use_god_qi_xie or use_god_gaitou)"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.0'", "'module': 'DAYUN_XIJI_V4.1'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.1完成(增加盖头截脚+天干地支配合判断:地支生天干气泄/天干克地支盖头则用神力量大减)')
