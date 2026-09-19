# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在六害判断前增加四个地支变量定义
old = """        # V2.4: 六害四支判断 (大运地支与原局任意地支六害)
        hai_target = LIU_HAI.get(zhi, '')
        for pos_name, pos_branch in [('YEAR', year_branch), ('MONTH', month_branch), ('DAY', day_branch), ('HOUR', hour_branch)]:"""
new = """        # V2.4: 六害四支判断 (大运地支与原局任意地支六害)
        year_branch = pillars['year'][1]
        month_branch = pillars['month'][1]
        day_branch = pillars['day'][1]
        hour_branch = pillars['hour'][1]
        hai_target = LIU_HAI.get(zhi, '')
        for pos_name, pos_branch in [('YEAR', year_branch), ('MONTH', month_branch), ('DAY', day_branch), ('HOUR', hour_branch)]:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('修复六害判断中year_branch未定义bug')
