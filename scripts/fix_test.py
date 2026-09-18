# -*- coding: utf-8 -*-
f = 'tests/test_daymaster_root_class_golden.py'
c = open(f, encoding='utf-8').read()
old = "('乙', '寅', 'NONE', '寅非四库, 同五行异阴阳不认余气'),"
new = "('乙', '寅', 'HEAVY_WANG', '阴干帝旺位(不论羊刃, 但作重根)'),"
c = c.replace(old, new)
open(f, 'w', encoding='utf-8').write(c)
print('done')
