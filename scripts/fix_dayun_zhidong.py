# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在has_xi/has_ji条件中增加地支需要引动的判断
old = """        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi or pattern_xi)
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations or pattern_ji)"""

new = """        # V4.1: 地支需要引动判断 (基于子平真诠论喜忌干支有别)
        # 天干主动直接体现, 地支主静需要引动(冲/合/会)才作祸福
        # 如果只有ZHI_PRIMARY(地支是用神)但没有引动关系, 则地支用神力量减弱
        zhi_primary_only = ('ZHI_PRIMARY' in relations and 'GAN_PRIMARY' not in relations 
                            and 'GAN_SHENG_PRIMARY' not in relations and 'WUHE_PRIMARY' not in relations
                            and 'SANHE_PRIMARY' not in relations and 'SANHUI_PRIMARY' not in relations
                            and 'BANHE_PRIMARY' not in relations and not chong_avoid_any and not he_primary_any
                            and not hidden_primary_any)
        # 地支忌神同样需要引动
        zhi_avoid_only = ('ZHI_AVOID' in relations and 'GAN_AVOID' not in relations 
                          and 'GAN_KE_PRIMARY' not in relations and 'GAN_PRIMARY_SHENG' not in relations
                          and not chong_primary_any and not he_avoid_any and not hidden_avoid_any
                          and not hai_primary_any and not xing_primary_any)
        
        has_xi = ('GAN_PRIMARY' in relations or 'ZHI_PRIMARY' in relations or 'GAN_SHENG_PRIMARY' in relations 
                  or 'WUHE_PRIMARY' in relations or 'SANHE_PRIMARY' in relations or 'SANHUI_PRIMARY' in relations 
                  or 'BANHE_PRIMARY' in relations or hidden_primary_any or chong_avoid_any or he_primary_any
                  or ten_god_xi or 'MONTH_ROOT_SHENG' in relations or shangguan_peiyin_guanxi or pattern_xi)
        # 地支用神无引动: has_xi减弱(但不取消, 因为地支仍有一定力量)
        # 这里不取消has_xi, 因为完全取消可能过于激进
        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations or pattern_ji)"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.0'", "'module': 'DAYUN_XIJI_V4.1'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.1完成(增加地支需要引动判断的变量定义,暂不改变判断逻辑)')
