# -*- coding: utf-8 -*-
"""003B-04 补全 2 条短定义"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
d = json.load(io.open(P, encoding='utf-8'))
n = 0
for dk, dom in d.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            if c.get('source_id') in ('YHZP-016-001', 'SFTK-062-050') and c.get('semantic_definition') == '十二宫定名':
                c['semantic_definition'] = '十二长生十二宫定名（长生沐浴冠带临官帝旺衰病死墓绝胎养，阳顺阴逆）'
                n += 1
json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'补全：{n} 条')
