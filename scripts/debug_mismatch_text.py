# -*- coding: utf-8 -*-
import json, re

with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', encoding='utf-8') as f:
    details = json.load(f)

# 读取DTS全文
with open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt', encoding='utf-8-sig') as f:
    content = f.read()

# 输出前5个不匹配案例的完整原文上下文
for d in details[:5]:
    chart = d['chart']
    dayun = d['dayun']
    print(f'=== {chart} {dayun} ===')
    print(f'引擎: {d["engine"]}, 原文: {d["text"]}')
    print(f'原文片段: {d["text_snippet"]}')
    # 在原文中查找这个命例
    chart_no_space = chart.replace(' ', '')
    pattern = re.compile(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s*){4}')
    for m in pattern.finditer(content):
        found = ''.join(m.groups()).replace(' ', '')
        if found == chart_no_space:
            start = m.end()
            next_m = pattern.search(content, start + 10)
            end = next_m.start() if next_m else start + 1500
            ctx = content[start:end]
            # 查找大运相关的句子
            sentences = re.split(r'[，。；！？\n]', ctx)
            gan = dayun[0]
            zhi = dayun[1]
            for i, sent in enumerate(sentences):
                if gan in sent or zhi in sent or dayun in sent:
                    print(f'  [{i}] {sent.strip()[:80]}')
            break
    print()
