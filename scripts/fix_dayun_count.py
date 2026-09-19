# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改综合喜忌标签逻辑, 增加计数机制
old = """        hidden_primary_any = any('ZHI_HIDDEN_' in r and '_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_' in r and '_AVOID' in r for r in relations)
        hai_primary_any = any('HAI_' in r and '_PRIMARY' in r for r in relations)
        if 'GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif 'GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""

new = """        # V2.5: 综合计数判断 (生扶关系数量 vs 克泄关系数量)
        # 生扶关系: 任何包含_PRIMARY的关系(除了冲/害/合的_AVOID)
        xi_count = 0
        ji_count = 0
        for r in relations:
            if '_PRIMARY' in r and 'CHONG_' not in r and 'HAI_' not in r and 'HE_' not in r:
                xi_count += 1
            elif '_AVOID' in r and ('CHONG_' in r or 'HAI_' in r or 'HE_' in r):
                ji_count += 1
            elif '_PRIMARY' in r and ('CHONG_' in r or 'HAI_' in r):
                ji_count += 1
            elif '_AVOID' in r and 'GAN_' in r or '_AVOID' in r and 'ZHI_AVOID' in r:
                ji_count += 1
            elif 'GAN_KE_PRIMARY' in r:
                ji_count += 1
        
        hidden_primary_any = any('ZHI_HIDDEN_' in r and '_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_' in r and '_AVOID' in r for r in relations)
        hai_primary_any = any('HAI_' in r and '_PRIMARY' in r for r in relations)
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                   or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                   or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any)
        
        # 综合判断: 如果生扶和克泄同时存在, 用计数决定
        if has_xi and has_ji:
            if xi_count > ji_count:
                xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
            elif ji_count > xi_count:
                xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
            else:
                # 计数相等时, 生扶优先(保守)
                xiji_label = 'SUPPORT_USE_GOD'
        elif has_xi:
            xiji_label = 'SUPPORT_USE_GOD'  # 生扶用神
        elif has_ji:
            xiji_label = 'SUPPRESS_USE_GOD'  # 克泄用神
        elif 'GAN_SECONDARY' in relations or 'ZHI_SECONDARY' in relations:
            xiji_label = 'SUPPORT_XI_SHEN'  # 生扶喜神
        else:
            xiji_label = 'NEUTRAL'  # 中性"""

c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V2.4'", "'module': 'DAYUN_XIJI_V2.5'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V2.5优化完成(综合计数判断)')
