# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在build_dayun_xiji函数中, 增加月令五行获取
old1 = """    dm = pillars['day'][0]
    dmw = WX[dm]
    
    primary = yongshen_result.get('yongshen_primary') or ''"""
new1 = """    dm = pillars['day'][0]
    dmw = WX[dm]
    month_branch = pillars['month'][1]
    month_wx = {'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'}.get(month_branch, '')
    
    primary = yongshen_result.get('yongshen_primary') or ''"""
c = c.replace(old1, new1)

# 在综合喜忌标签前, 增加月令力量修正
old2 = """        # 综合喜忌标签 (结构判断, 非吉凶)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
new2 = """        # V1.3: 月令力量修正 - 大运五行得月令生扶则力量强
        # 大运天干/地支五行与月令五行相同或月令生大运, 则大运力量强
        dayun_power_strong = False
        if month_wx:
            if gan_wx == month_wx or zhi_wx == month_wx:
                dayun_power_strong = True
            elif SHENG.get(month_wx) == gan_wx or SHENG.get(month_wx) == zhi_wx:
                dayun_power_strong = True
        
        # 综合喜忌标签 (结构判断, 非吉凶)
        # V1.3: 如果大运力量强且生扶用神, 更确定为SUPPORT_USE_GOD
        # 如果大运力量强且克泄用神, 更确定为SUPPRESS_USE_GOD
        xi_relations = {'GAN_PRIMARY', 'ZHI_PRIMARY', 'GAN_SHENG_PRIMARY', 'WUHE_PRIMARY', 'SANHE_PRIMARY'}
        ji_relations = {'GAN_AVOID', 'ZHI_AVOID', 'GAN_KE_PRIMARY'}
        xi_sec = {'GAN_SECONDARY', 'ZHI_SECONDARY'}
        
        has_xi = any(r in xi_relations for r in relations)
        has_ji = any(r in ji_relations for r in relations)
        has_sec = any(r in xi_sec for r in relations)
        
        if has_xi and (not has_ji or dayun_power_strong):
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif has_ji and (not has_xi or dayun_power_strong):
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif has_sec:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.2'", "'module': 'DAYUN_XIJI_V1.3'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V1.3优化完成(增加月令力量修正)')
