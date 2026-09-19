# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在综合判断逻辑前添加多标签计算
old = """        # 综合喜忌标签 (结构判断, 非吉凶)
        chong_primary_any = any('CHONG_' in r and '_PRIMARY' in r for r in relations)
        chong_avoid_any = any('CHONG_' in r and '_AVOID' in r for r in relations)
        hidden_primary_any = any('ZHI_HIDDEN_' in r and '_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_' in r and '_AVOID' in r for r in relations)
        he_primary_any = any('HE_' in r and '_PRIMARY' in r for r in relations)
        he_avoid_any = any('HE_' in r and '_AVOID' in r for r in relations)
        hai_primary_any = any('HAI_' in r and '_PRIMARY' in r for r in relations)
        xing_primary_any = any('XING_' in r and '_PRIMARY' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""

new = """        # 综合喜忌标签 (结构判断, 非吉凶)
        chong_primary_any = any('CHONG_' in r and '_PRIMARY' in r for r in relations)
        chong_avoid_any = any('CHONG_' in r and '_AVOID' in r for r in relations)
        hidden_primary_any = any('ZHI_HIDDEN_' in r and '_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_' in r and '_AVOID' in r for r in relations)
        he_primary_any = any('HE_' in r and '_PRIMARY' in r for r in relations)
        he_avoid_any = any('HE_' in r and '_AVOID' in r for r in relations)
        hai_primary_any = any('HAI_' in r and '_PRIMARY' in r for r in relations)
        xing_primary_any = any('XING_' in r and '_PRIMARY' in r for r in relations)
        
        # V3.2: 多标签输出 - 一个大运可能同时具有多种喜忌属性
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any)
        xiji_labels = []
        if has_xi:
            xiji_labels.append('SUPPORT_USE_GOD')
        if has_ji:
            xiji_labels.append('SUPPRESS_USE_GOD')
        if 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_labels.append('SUPPORT_XI_SHEN')
        if not xiji_labels:
            xiji_labels.append('NEUTRAL')
        
        if has_xi:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif has_ji:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""
c = c.replace(old, new)

# 在输出结构中添加xiji_labels字段
old2 = """            'xiji_label': xiji_label,"""
new2 = """            'xiji_label': xiji_label,
            'xiji_labels': xiji_labels,"""
c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py多标签输出修复完成')
