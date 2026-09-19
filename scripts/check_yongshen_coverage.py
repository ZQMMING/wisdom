# -*- coding: utf-8 -*-
import csv

path = r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv'
with open(path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print('总案例数:', len(rows))
print()
print('=== 关键字段非空率 ===')
fields = ['ys_primary', 'ys_secondary', 'ys_avoid', 'ys_path', 'climate', 'zhonghe', 'cong', 'zhuanwang', 'hua_qi', 'mu_mie', 'root', 'season', 'spectrum', 'ratio']
for field in fields:
    non_empty = sum(1 for r in rows if r.get(field, '').strip() and r.get(field, '').strip() not in ('[]', '{}', 'None', 'null', 'UNKNOWN', '未识别'))
    pct = non_empty / len(rows) * 100 if rows else 0
    print('  %-15s: %d/%d (%.1f%%)' % (field, non_empty, len(rows), pct))

print()
print('=== ys_primary 样例(前10个非空) ===')
count = 0
for r in rows:
    if r.get('ys_primary', '').strip() and r['ys_primary'].strip() not in ('[]', '{}', 'None', 'UNKNOWN'):
        print('  %s: %s' % (r['chart'], r['ys_primary'][:80]))
        count += 1
        if count >= 10:
            break

print()
print('=== ys_avoid 样例(前10个非空) ===')
count = 0
for r in rows:
    if r.get('ys_avoid', '').strip() and r['ys_avoid'].strip() not in ('[]', '{}', 'None', 'UNKNOWN'):
        print('  %s: %s' % (r['chart'], r['ys_avoid'][:80]))
        count += 1
        if count >= 10:
            break
