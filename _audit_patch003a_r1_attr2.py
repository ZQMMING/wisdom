# -*- coding: utf-8 -*-
"""R1-01：本地 DTS 注文任氏特征扫描 + 长注全文输出（判定 B1/B2 依据）"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

lines = open(r'D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl', encoding='utf-8').read().splitlines()
books = [json.loads(l) for l in lines if l.strip()]

ann = [s for s in books if s.get('text_layer') == 'ANNOTATION']

# 任氏命例特征词
FEAT = ['余曰', '余觀', '余观', '余詳', '余详', '此造', '彼曰', '運行', '運行', '某造', '命書', '命书',
        '余行', '余推', '余細', '余细', '考之', '論命', '余嘗', '余尝', '推過', '推过', '干為天元',
        '以餘論之', '以余论之', '謬書', '谬书', '俗論', '俗论']

print("===== 含任氏特征词的本地注文 =====")
for s in ann:
    t = s.get('source_text', '')
    hits = [f for f in FEAT if f in t]
    if hits:
        print(f"  {s['source_id']} [{s.get('chapter')}] {len(t)}字 特征: {hits}")

print("\n===== 长注（>=150字）全文（逐一人工鉴别） =====")
for s in ann:
    t = s.get('source_text', '')
    if len(t) >= 150:
        print(f"\n--- {s['source_id']} [{s.get('chapter')}] {len(t)}字")
        print(t[:500])
