# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open(r'D:\shuntian\data\heluo\canping\raw_shici_p24-58.json', encoding='utf-8'))
for p in d['pages']:
    if p['page'] == 24:
        for i, c in enumerate(p['cols']):
            print('c%d header=%r mark=%r 首句=%r' % (i, c['header'], c.get('mark',''), c['lines'][0]))
