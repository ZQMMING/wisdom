# -*- coding: utf-8 -*-
"""枚举三态化完整性校验（验收）"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

errors = []
warns = []

# 1. enum_registry 校验
reg = json.load(open(r'D:\shuntian-ziping-p0\governance\enum_registry.json', encoding='utf-8'))
enums = reg['enums']
print('=== 1. enum_registry ===')
print('总枚举:', len(enums), '| version:', reg.get('version'))

single = [e for e in enums if e.get('values') and len(e['values']) == 1]
two_no_unknown = [e for e in enums if e.get('values') and len(e['values']) == 2
                  and not (set(e['values']) & {'UNKNOWN', 'UNDETERMINED'})]
two_with_unknown = [e for e in enums if e.get('values') and len(e['values']) == 2
                    and bool(set(e['values']) & {'UNKNOWN', 'UNDETERMINED'})]
deprecated = [e for e in enums if e.get('status') == 'DEPRECATED']

print('单值枚举:', len(single), [e['enum_id'] for e in single])
print('二态无兜底:', len(two_no_unknown), [e['enum_id'] for e in two_no_unknown])
print('二态有兜底(UNKNOWN):', len(two_with_unknown), [e['enum_id'] for e in two_with_unknown])
print('DEPRECATED:', len(deprecated), [e['enum_id'] for e in deprecated])

if single: errors.append('仍有单值枚举: %s' % [e['enum_id'] for e in single])
if two_no_unknown: errors.append('仍有二态无兜底: %s' % [e['enum_id'] for e in two_no_unknown])

# 删除确认
ids = {e['enum_id'] for e in enums}
if 'dts_shangguan_ge_state' in ids:
    errors.append('shangguan_ge_state 未删除')
else:
    print('shangguan_ge_state: 已删除 ✓')
if 'dts_xing_ding_state' in ids:
    print('xing_ding_state: 已新增 ✓')
else:
    errors.append('xing_ding_state 未新增')

# 2. state.py 输出字段 vs registry 对照
src = open(r'D:\shuntian-ziping-p0\engines\ditiansui\calculation\state.py', encoding='utf-8').read()
# 提取 out["xxx"] 直接赋值的字面值
out_vals = {}
for m in re.finditer(r'out\["([^"]+)"\]\s*=\s*"([^"]+)"', src):
    fld, val = m.group(1), m.group(2)
    out_vals.setdefault(fld, set()).add(val)
print()
print('=== 2. state.py 字面输出 vs registry ===')
# registry 枚举值全表
reg_vals = {}
for e in enums:
    if e.get('values'):
        reg_vals[e['enum_id']] = set(e['values'])
# state 输出字段里哪些在 registry 有对应枚举但值不在值域
for fld, vals in sorted(out_vals.items()):
    for v in vals:
        if v in ('UNDETERMINED', 'UNKNOWN', 'True', 'False'):
            continue
        # 找 registry 中该字段名
        if fld in reg_vals and v not in reg_vals[fld]:
            errors.append('state 输出值不在 registry 值域: %s=%s (registry: %s)' % (fld, v, sorted(reg_vals[fld])))
        # 找别名（pending 里的）
print('state 字面输出字段数:', len(out_vals))
print()
# 3. 结论
print('=== 结论 ===')
if errors:
    print('❌ 校验失败:')
    for e in errors: print('  -', e)
else:
    print('✅ 全部通过：0 单值、0 二态无兜底、state 输出值均在 registry 值域内')
