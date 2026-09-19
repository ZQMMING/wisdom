# -*- coding: utf-8 -*-
import json
lines=open(r'D:\shuntian-ziping-lab\cases\all_cases.jsonl',encoding='utf-8').readlines()
print(f'总案例: {len(lines)}')
d=json.loads(lines[0])
print(f'字段: {list(d.keys())}')
print(f'示例: book={d.get("book")}, chart={d.get("chart")}')
print(f'judgment: {d.get("judgment","")[:80]}')
books={}
for l in lines:
    d=json.loads(l)
    b=d.get('book','?')
    books[b]=books.get(b,0)+1
print(f'分布: {books}')
