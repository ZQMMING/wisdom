# -*- coding: utf-8 -*-
"""003B-04 修正：按 text_layer 补 attribution（ORIGINAL→ORIGINAL_AUTHOR；ANNOTATION→ORIGINAL_ANNOTATION）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json'
data = json.load(io.open(P, encoding='utf-8'))

TL_ATTR = {
    'ORIGINAL': 'ORIGINAL_AUTHOR',
    'ANNOTATION': 'ORIGINAL_ANNOTATION',
    'LATER_COMMENTARY': 'LATER_COMMENTARY',
    'UNVERIFIED': 'UNKNOWN',
}

filled = 0
for dk, dom in data.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            at = c.get('attribution')
            if at in (None, '', '—', 'UNKNOWN', 'TO_VERIFY'):
                tl = c.get('text_layer') or '—'
                if tl in TL_ATTR:
                    c['attribution'] = TL_ATTR[tl]
                    filled += 1

json.dump(data, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'按 text_layer 补 attribution：{filled} cell')

# 复检
missing = 0
for dk, dom in data.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            if c.get('attribution') in (None, '', '—', 'UNKNOWN', 'TO_VERIFY'):
                missing += 1
                print(f'  ⚠️ {dk}/{b}/{c.get("source_id")} attribution={c.get("attribution")}')
print(f'仍缺失：{missing}')
