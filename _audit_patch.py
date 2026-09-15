# -*- coding: utf-8 -*-
"""PATCH-001 现状审计：registry 关键枚举核对"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

reg = json.load(open(r'D:\shuntian-ziping-p0\governance\enum_registry.json', encoding='utf-8'))
print('registry 枚举数:', len(reg['enums']))

print('\n=== support/effect/chengbai/formation/structure/activation/dongjing/gaitou ===')
for kw in ('support', 'effect', 'chengbai', 'formation', 'destruction', 'rescue',
           'structure', 'activation', 'dongjing', 'gaitou', 'pattern', 'disease', 'medicine'):
    for h in reg['enums']:
        if kw in h['enum_id']:
            print('%-28s [%s]: %s' % (h['enum_id'], h.get('status'), h.get('values')))

print('\n=== registry vs enums.py 类清单对照 ===')
# enums.py 类
import re
src = open(r'D:\shuntian-ziping-p0\shared_types\enums.py', encoding='utf-8').read()
classes = re.findall(r'class (\w+)\(str, Enum\):', src)
print('enums.py 类:', classes)
print('registry enum_id 全部:', [e['enum_id'] for e in reg['enums']])
