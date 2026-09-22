#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('tests/cases_l1_v1.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

print('=== 全部化气型用例 ===')
for c in data:
    if c['expect_type'] == '化气型':
        has_chen = '辰' in c['key']
        note = c.get('note', c.get('provenance_note', ''))[:80]
        print(f"{c['id']:8} {c['key']:15} {c['expect_confidence']:10} 辰={has_chen}")
        if note:
            print(f"         note: {note}")

print()
print('=== 地支含辰的化气型用例（排除乙庚化金日主庚）===')
for c in data:
    if c['expect_type'] == '化气型' and '辰' in c['key']:
        # 判断是不是乙庚化金
        key = c['key']
        # 日柱是第3个柱
        day = key.split()[2]
        day_stem = day[0]
        if day_stem not in ('庚', '辛'):  # 不是乙庚化金日主金
            print(f"{c['id']:8} {c['key']:15} {c['expect_confidence']:10}")
