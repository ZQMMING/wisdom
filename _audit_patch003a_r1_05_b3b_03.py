# -*- coding: utf-8 -*-
"""003B-03 Scope 边界复核：旺/强/衰/令/地/根/势 对象化完整性审计"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.load(io.open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8'))

DOMAINS = ['domain_01_wang_qiang_shuai', 'domain_02_ling_shi_di_gen', 'domain_03_shi',
           'domain_04_yue_ling', 'gen_qi']

print('=' * 90)
print('003B-03 对象化审计：每个 cell 是否满足 OBJECT+SOURCE+RELATION+CLASSICAL_SCOPE')
print('=' * 90)

issues = []
for dk in DOMAINS:
    dom = data.get(dk)
    if not dom:
        print(f'\n### {dk}: 不存在！')
        continue
    print(f'\n### {dom.get("domain_id")}（{dk}）')
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            sid = c.get('source_id') or '—'
            obj = c.get('object_type') or '—'
            role = c.get('semantic_role') or '—'
            layer = c.get('text_layer') or '—'
            grade = c.get('evidence_grade') or '—'
            elig = c.get('execution_eligibility') or '—'
            ok = obj not in ('TO_VERIFY', '—', None) and role not in ('TO_VERIFY', '—', None)
            flag = 'OK' if ok else '⚠️ 对象/角色缺失'
            print(f'  {b} {sid} | obj={obj} | role={role} | {layer}/{grade} | {elig} {flag}')
            if not ok:
                issues.append((dk, b, sid, 'object_type 或 semantic_role 缺失'))

print(f'\n=== 问题总数：{len(issues)} ===')
for dk, b, sid, m in issues:
    print(f'  {dk}/{b}/{sid}: {m}')
