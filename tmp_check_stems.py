# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, 'src')
os.environ['TONGSHU_ALLOW_ZIWEI_STUB'] = '1'
from tongshu.engines.ziwei_engine import ZiweiEngine, GAN_SIHUA

eng = ZiweiEngine()
chart = eng.full_chart((1980, 6, 22), 12, 'male')

print('=== Palace Stems & SiHua ===')
for pname, pdata in chart.palaces.items():
    stem = pdata.get('stem', '')
    branch = str(pdata.get('branch', '')).strip("'\"")
    sihua = GAN_SIHUA.get(stem, ('','','',''))
    sihua_strs = []
    for i, s in enumerate(sihua):
        if s:
            sihua_strs.append('%s化%s' % (s, ['禄','权','科','忌'][i]))
    print('  %s[%s] stem=%s sihua=%s' % (pname, branch, stem, sihua_strs))
