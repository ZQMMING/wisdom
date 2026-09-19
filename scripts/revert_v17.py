# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 回退天干五合月令判断
old = """        # V1.8: 天干五合月令判断 (大运天干与月令天干五合)
        month_stem = pillars['month'][0]
        wuhe_month_info = WU_HE.get(gan, ('', ''))
        wuhe_month_huashen = wuhe_month_info[0]
        wuhe_month_target = wuhe_month_info[1]
        if wuhe_month_target == month_stem:
            relations.append('GAN_WUHE_MONTH')
            if wuhe_month_huashen == primary:
                relations.append('WUHE_MONTH_PRIMARY')  # 天干合月令化用神, 喜
            if avoid and wuhe_month_huashen == avoid[0]:
                relations.append('WUHE_MONTH_AVOID')  # 天干合月令化忌神, 忌
        
        # V1.2: 三合判断"""
new = """        # V1.2: 三合判断"""
c = c.replace(old, new)

# 回退综合喜忌标签逻辑中的wuhe_avoid_any
old2 = """        chong_primary_any = any('CHONG_' in r and '_PRIMARY' in r for r in relations)
        chong_avoid_any = any('CHONG_' in r and '_AVOID' in r for r in relations)
        wuhe_primary_any = any('WUHE' in r and '_PRIMARY' in r for r in relations)
        wuhe_avoid_any = any('WUHE' in r and '_AVOID' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or wuhe_primary_any or 'SANHE_PRIMARY' in relations or chong_avoid_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or chong_primary_any or wuhe_avoid_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
new2 = """        chong_primary_any = any('CHONG_' in r and '_PRIMARY' in r for r in relations)
        chong_avoid_any = any('CHONG_' in r and '_AVOID' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or chong_avoid_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or chong_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V1.8'", "'module': 'DAYUN_XIJI_V1.7'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('回退到V1.7完成')
