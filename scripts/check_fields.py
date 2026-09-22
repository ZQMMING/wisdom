# -*- coding: utf-8 -*-
"""检查各经典切片的字段名是否一致"""
import json
from pathlib import Path
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SOURCE_DIR = Path(r'D:\shuntian-ziping-p0\registries\source')

files = [
    'sources.dts.jsonl',
    'sources.pzzq.jsonl',
    'sources.qtbj.jsonl',
    'sources.smth.jsonl',
    'sources.yhzp.jsonl',
    'sources.sftk.jsonl'
]

for f in files:
    p = SOURCE_DIR / f
    if not p.exists():
        print(f'{f}: 文件不存在')
        continue
    lines = p.read_text(encoding='utf-8').splitlines()
    if not lines:
        print(f'{f}: 空文件')
        continue
    rec = json.loads(lines[0])
    fields = list(rec.keys())
    print(f'{f}:')
    print(f'  字段: {fields}')
    print(f'  book: {rec.get("book", "(无)")}')
    print(f'  evidence_grade: {rec.get("evidence_grade", "(无)")}')
    print()
