# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, 'src')
os.environ['TONGSHU_ALLOW_ZIWEI_STUB'] = '1'
from tongshu.engines.ziwei_engine import ZiweiEngine
eng = ZiweiEngine()
chart = eng.full_chart((1980, 6, 22), 12, 'male')
items = list(chart.palaces.items())
for i, (pname, pdata) in enumerate(items):
    op_idx = (i + 6) % 12
    op_name = items[op_idx][0]
    branch = str(pdata.get('branch','')).strip("'\"")
    op_branch = str(items[op_idx][1].get('branch','')).strip("'\"")
    major = pdata.get('major',[])
    op_major = items[op_idx][1].get('major',[])
    print('%d: %s[%s] -> opposite(%d): %s[%s] majors=%s <-> %s' % (
        i, pname, branch, op_idx, op_name, op_branch, major, op_major))
