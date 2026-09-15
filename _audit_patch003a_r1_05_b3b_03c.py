# -*- coding: utf-8 -*-
"""003B-03 验证：禁 has_root(day_master)→strong 模式 + 旺≠强/得令≠强 边界扫描"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.load(io.open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8'))

# 检查所有 cell 的 semantic_definition/excluded_scope 是否含固化推导模式
BAD_PATTERNS = [
    ('有根→身强', lambda d: '有根' in d and '身強' in d and '≠' not in d),
    ('得令→身强', lambda d: '得令' in d and '身強' in d and '≠' not in d),
    ('得令=强', lambda d: '得令' in d and '=强' in d.replace('＝', '=')),
    ('旺=强', lambda d: '旺' in d and '=强' in d.replace('＝', '=')),
]

violations = []
total_cells = 0
for dk, dom in data.items():
    for b, cells in dom.get('books', {}).items():
        for c in cells:
            total_cells += 1
            text = (c.get('semantic_definition') or '') + (c.get('excluded_scope') or '')
            for name, fn in BAD_PATTERNS:
                if fn(text):
                    violations.append((dk, b, c.get('source_id'), name, c.get('semantic_definition')))

print(f'总 cell：{total_cells}')
print(f'固化推导模式违规：{len(violations)}')
for dk, b, sid, name, defn in violations:
    print(f'  ⚠️ {dk}/{b}/{sid} [{name}]: {defn[:60]}')

# 旺≠强边界确认（rule_boundary）
print('\n=== 旺≠强 / 得令≠强 边界（rule_boundary）===' )
for dk in ['domain_01_wang_qiang_shuai', 'domain_02_ling_shi_di_gen']:
    rb = data[dk].get('rule_boundary', {})
    print(f'{dk}:')
    print(f'  forbidden: {rb.get("forbidden")}')
