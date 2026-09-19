# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 放宽用神过旺反忌的条件: 用神>35%+日主>25%+大运干支都是用神五行
old = """        # 用神过旺反忌的精细条件
        primary_too_strong_reverse = (primary_power_ratio > 0.40 and daymaster_power_ratio > 0.30 
                                       and dayun_all_primary and primary_strong)"""

new = """        # 用神过旺反忌的精细条件 (放宽: 用神>35%+日主>25%+大运干支都是用神五行)
        primary_too_strong_reverse = (primary_power_ratio > 0.35 and daymaster_power_ratio > 0.25 
                                       and dayun_all_primary and primary_strong)"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py用神过旺反忌条件放宽完成(用神>35%+日主>25%)')
