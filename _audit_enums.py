# -*- coding: utf-8 -*-
"""枚举二态/单态审查"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

reg = json.load(open(r'D:\shuntian-ziping-p0\governance\enum_registry.json', encoding='utf-8'))
enums = reg.get('enums', [])
print('总枚举:', len(enums))
print()
print('=== 二态枚举（布尔化风险）===')
two = [e for e in enums if e.get('values') and len(e['values'])==2]
for e in two:
    print('  %-42s | %-8s | %s' % (e['enum_id'], e['status'], e['values']))
print('二态小计:', len(two))
print()
print('=== 单值枚举（无区分度）===')
one = [e for e in enums if e.get('values') and len(e['values'])==1]
for e in one:
    print('  %-42s | %-8s | %s' % (e['enum_id'], e['status'], e['values']))
print('单值小计:', len(one))
print()
print('=== 三态及以上 ===')
multi = [e for e in enums if e.get('values') and len(e['values'])>=3]
print('多态小计:', len(multi))
