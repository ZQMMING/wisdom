# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.dayun_summary import dayun_summary

pillars = {
    'year': ['辛', '卯'],
    'month': ['丁', '酉'],
    'day': ['庚', '午'],
    'hour': ['丙', '子'],
}

# 大运列表
dayun = ['丙申','乙未','癸巳','壬辰','庚寅','己丑','戊子','丁亥']

dy = dayun_summary(pillars, dayun)
print('=== dayun_summary 输出 ===')
for k, v in dy.items():
    if isinstance(v, list):
        print('%s (list, len=%d):' % (k, len(v)))
        for item in v[:3]:
            print('  %s' % str(item)[:300])
    elif isinstance(v, dict):
        print('%s (dict):' % k)
        for kk, vv in list(v.items())[:5]:
            print('  %s: %s' % (kk, str(vv)[:200]))
    else:
        print('%s: %s' % (k, v))
