# -*- coding: utf-8 -*-
import json

GEJU_PATTERNS = ['正官格','偏官格','七杀格','正财格','偏财格','正印格','偏印格','食神格','伤官格','建禄格','月劫格','羊刃格','阳刃格','从财格','从杀格','从儿格','从官格','曲直格','炎上格','稼穑格','从革格','润下格','化气格','化土格','化木格','化金格','化水格','化火格','合禄格','井栏叉格','六阴朝阳格','刑合格']

with open(r'D:\顺天系统资料\用神案例JSONL\原局层\用神专项\用神_all.jsonl', 'r', encoding='utf-8') as f:
    cases = [json.loads(line) for line in f if line.strip()]

print('总案例:', len(cases))
has_ge = 0
has_geju_pattern = 0
geju_examples = []
for case in cases:
    text = case.get('raw', '')
    if '格' in text:
        has_ge += 1
    found = []
    for pat in GEJU_PATTERNS:
        if pat in text:
            found.append(pat)
    if found:
        has_geju_pattern += 1
        if len(geju_examples) < 5:
            geju_examples.append((case.get('bazi',''), found))

print('包含格字:', has_ge)
print('包含格局模式:', has_geju_pattern)
print()
print('前5个包含格局的案例:')
for bazi, geju in geju_examples:
    print('  %s: %s' % (bazi, geju))
