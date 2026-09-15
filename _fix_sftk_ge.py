# -*- coding: utf-8 -*-
"""SFTK 91 条 歌/詩 开头 text_layer 定性：
- 歌釋/詩釋 开头 = 对歌诀/断语的解释 → ANNOTATION / B
- 歌曰/詩曰 开头 = 歌诀引用 → QUOTED_SOURCE（新登记层）/ D（出处待核）
- 空条目（SFTK-125-038）→ ANNOTATION + NEEDS_REVIEW
同时识别：正文+歌釋/詩釋 混排条目（违反 D-4 Mixed Source，登记待拆）"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

P = r'D:\shuntian-ziping-p0\registries\source\sources.sftk.jsonl'
lines = open(P, encoding='utf-8').read().splitlines()
out = []
stat = {'SHI_ANN': 0, 'YUE_QUOTED': 0, 'EMPTY': 0}
mixed = []

for l in lines:
    if not l.strip():
        out.append(l)
        continue
    s = json.loads(l)
    txt = s.get('source_text', '').strip()
    if txt.startswith(('歌釋', '詩釋')):
        if txt == '詩釋':
            s['text_layer'] = 'ANNOTATION'
            s['evidence_grade'] = 'B'
            s['notes'] = s.get('notes', '') + '；2026-09-16：空「詩釋」条目，内容缺失，标 NEEDS_REVIEW'
            s['status'] = 'NEEDS_REVIEW'
            stat['EMPTY'] += 1
        else:
            s['text_layer'] = 'ANNOTATION'
            s['evidence_grade'] = 'B'
            s['notes'] = s.get('notes', '') + '；2026-09-16 定性：歌釋/詩釋=对歌诀/断语的解释（《继善篇》等体例），注解层，非 ORIGINAL'
            stat['SHI_ANN'] += 1
    elif txt.startswith(('歌曰', '詩曰')):
        s['text_layer'] = 'QUOTED_SOURCE'
        s['evidence_grade'] = 'D'
        s['notes'] = s.get('notes', '') + '；2026-09-16 定性：歌诀引用（歌曰/詩曰），原出处待核（前贤赋文或张楠自作），不得作神峰通考 ORIGINAL 证据；QUOTED_SOURCE 为新增 text_layer 层（Human 点名登记）'
        stat['YUE_QUOTED'] += 1
    # 混排识别：非歌詩开头但正文中夹带 歌釋/詩釋/歇釋
    elif re.search(r'(歌釋|詩釋|歇釋)', txt):
        mixed.append((s['source_id'], s.get('chapter'), txt[:50] + '...[含釋混排]'))
    out.append(json.dumps(s, ensure_ascii=False))

open(P, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('定性结果:', stat)
print()
print('===== 混排条目（正文+釋，违反 D-4，待拆条）=====')
for sid, ch, t in mixed:
    print(f'  {sid} | {ch} | {t}')
print(f'混排总数: {len(mixed)}')
