# -*- coding: utf-8 -*-
"""003B-02 概念遗漏检查：现代术语 → 六部原文表达簇 对照 Scope 覆盖"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BOOK_FILE = {'YHZP': 'yhzp', 'PZZQ': 'pzzq', 'DTS': 'dts', 'QTBJ': 'qtbj', 'SMTH': 'smth', 'SFTK': 'sftk'}
src = {}
for b, f in BOOK_FILE.items():
    src[b] = []
    for l in io.open(rf'D:\shuntian-ziping-p0\registries\source\sources.{f}.jsonl', encoding='utf-8'):
        if not l.strip():
            continue
        src[b].append(json.loads(l))

scope = json.load(io.open(r'D:\shuntian-ziping-p0\governance\r1_05_verified_scope.json', encoding='utf-8'))

# 现代术语 → (同词, 六部原文近义表达簇)
TERMS = [
    ('身强', ['身強', '身强', '日主強', '日主强'], ['身健', '身旺', '身強體健', '強者']),
    ('身弱', ['身弱', '日主弱', '日主太弱'], ['身衰', '日主無氣', '日干無氣', '身柔']),
    ('旺', ['旺'], ['旺相', '當旺', '得旺', '旺論', '興旺', '當權', '司權', '帝旺']),
    ('衰', ['衰'], ['衰看', '衰弱', '休囚', '失令', '衰敗']),
    ('清', ['清'], ['清奇', '清純', '清枯', '清得', '清氣', '清貴']),
    ('浊', ['濁', '浊'], ['混', '混雜', '濁氣', '雜氣']),
    ('真', ['真'], ['真神', '真者', '真機', '真實']),
    ('假', ['假'], ['假神', '假者', '假借']),
    ('病', ['病'], ['有病', '病神', '病處', '為病']),
    ('药', ['藥', '药'], ['救應', '去病', '為藥', '醫', '解']),
    ('喜忌', ['喜忌', '喜', '忌'], ['喜神', '忌神', '喜用', '所喜', '所忌']),
]

print('=' * 100)
print('003B-02 概念遗漏检查：现代术语 × 六部原文表达命中')
print('=' * 100)

for term, same_words, alt_words in TERMS:
    print(f'\n### 「{term}」')
    for b, items in src.items():
        same = sum(1 for s in items if any(k in s.get('source_text', '') for k in same_words))
        alt = sum(1 for s in items if any(k in s.get('source_text', '') for k in alt_words))
        # 取一个代表性近义表达
        sample = ''
        for s in items:
            t = s.get('source_text', '')
            for k in alt_words:
                if k in t:
                    i = t.find(k)
                    sample = t[max(0, i - 8):i + 12]
                    break
            if sample:
                break
        print(f'  {b}: 同词{same}条 / 近义{alt}条 | 代表：「{sample}」')
