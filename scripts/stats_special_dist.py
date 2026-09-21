# -*- coding: utf-8 -*-
"""统计引擎special字段分布"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from scripts.dayun_align import cases, pai_pan, get_wangshuai, get_qiangruo

# 统计special分布
special_dist = {}
total = 0

for li, fp, dy, txt in cases:
    if len(dy) < 4:
        continue
    total += 1
    
    # 简化: 直接从dayun_align的输出中提取
    # 这里需要完整引擎调用, 先跳过

print('总案例数: %d' % total)
print('special分布统计需要完整引擎调用')
print('注: 下一步从dayun_align输出中grep')
