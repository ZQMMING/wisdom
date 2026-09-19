# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修复has_ji条件: 添加GAN_PRIMARY_SHENG(用神生大运=泄用神)
old = """        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations)"""
new = """        has_ji = ('GAN_AVOID' in relations or 'ZHI_AVOID' in relations or 'GAN_KE_PRIMARY' in relations 
                  or 'GAN_PRIMARY_SHENG' in relations or hidden_avoid_any or chong_primary_any or he_avoid_any or hai_primary_any or xing_primary_any
                  or ten_god_ji or 'MONTH_ROOT_KE' in relations)"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V3.6'", "'module': 'DAYUN_XIJI_V3.7'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V3.7修复完成(has_ji条件添加GAN_PRIMARY_SHENG泄用神)')
