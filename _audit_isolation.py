# -*- coding: utf-8 -*-
"""PENDING 执行隔离审计：registry 中 status=PENDING 的枚举，state.py 必须收进 pending 命名空间"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

reg = json.load(open(r'D:\shuntian-ziping-p0\governance\enum_registry.json', encoding='utf-8'))
src = open(r'D:\shuntian-ziping-p0\engines\ditiansui\calculation\state.py', encoding='utf-8').read()

# 取 pending 收拢清单（_PENDING_FIELDS 元组内容）
m = re.search(r'_PENDING_FIELDS = \((.*?)\)\n', src, re.S)
pending_fields = set(re.findall(r'"([^"]+)"', m.group(1))) if m else set()

print('pending 隔离字段数:', len(pending_fields))

# registry 里 status=PENDING 或 CANDIDATE 的枚举
pend_reg = {e['enum_id'] for e in reg['enums'] if e.get('status') in ('PENDING', 'CANDIDATE', 'PENDING_VERIFY')}
active_reg = {e['enum_id'] for e in reg['enums'] if e.get('status') == 'ACTIVE'}
print('registry PENDING:', len(pend_reg), '| ACTIVE:', len(active_reg))

# 对照：registry PENDING 的枚举在 state.py 是否被输出（进 pending 或正式 out）
# 找 state.py 中 out["xxx"] 输出但不在 _PENDING_FIELDS 里的字段 → 正式输出
out_keys = set(re.findall(r'out\["([^"]+)"\]', src))
formal_out = out_keys - pending_fields - {'pending'} - {'stem', 'stem_yinyang', 'branch_yinyang',
                                                        'relation', 'pillar', 'day_strength_state',
                                                        'day_strength_classic', 'yong_shen_el',
                                                        'yong_shen_ten_god', 'cai_guan_state',
                                                        'cong_support_state', 'special_state',
                                                        'cong_candidate', 'xing_state', 'is_cold',
                                                        'is_hot', 'is_dry', 'is_wet', 'climate',
                                                        'climate_type', 'day_master_strength'}
print()
print('=== 正式输出字段（非 pending）===')
for f in sorted(formal_out):
    # 该字段在 registry 里的状态
    st = next((e.get('status') for e in reg['enums'] if e['enum_id'] == f), '?')
    mark = '❌ PENDING泄漏' if st in ('PENDING', 'CANDIDATE', 'PENDING_VERIFY') else ''
    print('  %-22s registry_status=%s %s' % (f, st, mark))

print()
print('=== 结论 ===')
bad = [f for f in formal_out
       if next((e.get('status') for e in reg['enums'] if e['enum_id'] == f), '?') in ('PENDING', 'CANDIDATE', 'PENDING_VERIFY')]
if bad:
    print('❌ PENDING 泄漏到正式输出:', bad)
else:
    print('✅ 无 PENDING 泄漏：所有 PENDING 枚举均收拢在 pending 命名空间')
