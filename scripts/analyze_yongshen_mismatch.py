# -*- coding: utf-8 -*-
import json

with open(r'D:\shuntian-ziping-p0\scripts\yuanju_yongshen_mismatch.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

print('不匹配案例数:', len(cases))
print()

# 按书籍分类
by_book = {}
for c in cases:
    book = c.get('book', 'unknown')
    by_book.setdefault(book, []).append(c)

print('=== 按书籍 ===')
for book, cs in sorted(by_book.items(), key=lambda x: -len(x[1])):
    print('%s: %d个' % (book, len(cs)))

print()
print('=== 全部案例 ===')
for i, c in enumerate(cases):
    print('%d. %s [%s] tier=%s' % (i+1, c.get('bazi',''), c.get('book',''), c.get('spectrum_tier','')))
    print('   原文: %s  引擎: %s/%s' % (c.get('raw_yongshen',''), c.get('engine_primary',''), c.get('engine_secondary','')))
    snippet = c.get('raw_snippet','')[:80].replace('\n', ' ')
    print('   原文: %s...' % snippet)
    print()
