# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 优化: 只有大运藏干本气才计入has_xi/has_ji, 中气和余气不计入
old = """        hidden_primary_any = any('ZHI_HIDDEN_' in r and '_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_' in r and '_AVOID' in r for r in relations)"""

new = """        # V4.6: 只有大运藏干本气才计入has_xi/has_ji, 中气和余气不计入(本气力量远大于中气余气)
        hidden_primary_any = any('ZHI_HIDDEN_BENQI_PRIMARY' in r for r in relations)
        hidden_avoid_any = any('ZHI_HIDDEN_BENQI_AVOID' in r for r in relations)"""
c = c.replace(old, new)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.5'", "'module': 'DAYUN_XIJI_V4.6'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.6完成(只有大运藏干本气才计入has_xi/has_ji, 中气余气不计入)')
