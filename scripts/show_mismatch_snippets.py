# -*- coding: utf-8 -*-
import json

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    details = json.load(f)

# 输出前20个不匹配案例的原文片段
for d in details[:20]:
    print(f'{d["chart"]} {d["dayun"]}: 引擎={d["engine"]}, 原文={d["text"]}')
    print(f'  {d["text_snippet"][:120]}')
    print()
