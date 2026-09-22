# -*- coding: utf-8 -*-
"""找li=66的八字"""
import json
from pathlib import Path
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

cases = json.loads(Path(r'D:\shuntian-ziping-p0\scripts\dts_cases_extracted.json').read_text(encoding='utf-8'))
print(f'总案例数: {len(cases)}')
print()

# 找庚申乙酉庚戌庚辰这个案例
for i, c in enumerate(cases):
    pillars = c['pillars']
    # 庚申乙酉庚戌庚辰
    if (pillars[0][0] == '庚' and pillars[0][1] == '申' and
        pillars[1][0] == '乙' and pillars[1][1] == '酉' and
        pillars[2][0] == '庚' and pillars[2][1] == '戌' and
        pillars[3][0] == '庚' and pillars[3][1] == '辰'):
        print(f'找到li=66:')
        print(f'  索引: {i}')
        print(f'  src_line: {c["src_line"]}')
        print(f'  四柱: {pillars}')
        print(f'  日主: {pillars[2][0]}')
        break
else:
    print('未找到庚申乙酉庚戌庚辰')
    # 打印前10条看看结构
    print()
    print('前10条案例:')
    for i, c in enumerate(cases[:10]):
        print(f'  {i}: src_line={c["src_line"]}, pillars={c["pillars"]}')
