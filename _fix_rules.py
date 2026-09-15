# -*- coding: utf-8 -*-
"""修正 rules.dts.jsonl 消费同步（三态化）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\shuntian-ziping-p0\registries\rule\rules.dts.jsonl'
lines = open(p, encoding='utf-8').read().splitlines()
out_lines = []
changed = []

for ln in lines:
    if not ln.strip():
        out_lines.append(ln)
        continue
    d = json.loads(ln)
    rid = d.get('rule_id', '')
    conds = d.get('preconditions', {}).get('conditions', [])
    new_conds = []
    for c in conds:
        if not isinstance(c, dict):
            new_conds.append(c)
            continue
        f = c.get('field', '')
        v = c.get('value', '')
        # CAND-DTS-042 寿段「性定」：xing_state=定 → xing_ding_state=定
        if f == 'xing_state' and v == '定':
            c = dict(c); c['field'] = 'xing_ding_state'
            changed.append('%s: xing_state=定 → xing_ding_state=定' % rid)
        # CAND-DTS-070/071 伤官格：shangguan_ge_state=清/濁 → qing_state=一清到底有精神/满盘浊气
        # 注：qing_state 的「清」语义值域含 一清到底有精神/清得盡；「濁」含 滿盤濁氣/半濁半清/清枯
        if f == 'shangguan_ge_state':
            c = dict(c)
            if v == '清':
                c['field'] = 'qing_state'; c['value'] = '一清到底有精神'
                c['note'] = '2026-09-16 三态化：shangguan_ge_state 已删，复用 qing_state（清=一清到底有精神）'
            elif v == '濁':
                c['field'] = 'qing_state'; c['value'] = '滿盤濁氣'
                c['note'] = '2026-09-16 三态化：shangguan_ge_state 已删，复用 qing_state（濁=滿盤濁氣）'
            changed.append('%s: shangguan_ge_state=%s → qing_state=%s' % (rid, v, c['value']))
        new_conds.append(c)
    if new_conds != conds:
        d['preconditions']['conditions'] = new_conds
    out_lines.append(json.dumps(d, ensure_ascii=False))

open(p, 'w', encoding='utf-8').write('\n'.join(out_lines) + '\n')
print('改动:')
for c in changed:
    print('  ', c)
print('done')
