# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from engines.common.dayun_summary import dayun_summary
tests = [
    ({'year':['癸','酉'],'month':['甲','子'],'day':['癸','亥'],'hour':['辛','酉']}, ['丙寅']),
    ({'year':['甲','寅'],'month':['丙','寅'],'day':['甲','寅'],'hour':['丁','卯']}, ['丙午']),
    ({'year':['乙','酉'],'month':['丁','巳'],'day':['乙','酉'],'hour':['丁','巳']}, ['己丑']),
]
for p, dy in tests:
    r = dayun_summary(p, dy)
    print('大运', dy[0], 'sanhe=', r['sanhe_ju'], 'sanhui=', r['sanhui_ju'])
