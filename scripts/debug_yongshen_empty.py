# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.yongshen_engine import build_yongshen

# 测试第一个不匹配案例
with open(r'D:\shuntian-ziping-p0\scripts\yuanju_yongshen_mismatch.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

for i, case in enumerate(cases[:3]):
    chart = case.get('chart', '')
    print('=== 案例 %d: %s ===' % (i+1, chart))
    print('book:', case.get('book',''))
    print('raw_yongshen:', case.get('raw_yongshen',''))
    try:
        pillars = {
            'year': chart[0:2], 'month': chart[2:4],
            'day': chart[4:6], 'hour': chart[6:8]
        }
        f = build(pillars)
        ys = build_yongshen(f, pillars)
        print('yongshen type:', type(ys))
        if isinstance(ys, dict):
            print('keys:', list(ys.keys()))
            for k, v in ys.items():
                if k != 'details':
                    print('  %s: %s' % (k, v))
        else:
            print('yongshen:', ys)
    except Exception as e:
        import traceback
        traceback.print_exc()
    print()
