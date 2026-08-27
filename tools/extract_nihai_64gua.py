#!/usr/bin/env python3
"""从倪海厦64卦文档中提取每卦的核心断言（人间道+卜筮用例）。"""
import re
import json
from pathlib import Path

DOC = Path(r"D:\today\nihai-tianji-corpus\docs\09-六十四卦.md")
text = DOC.read_text(encoding="utf-8")

# 按 ## 分割每卦
blocks = re.split(r'\n## ', text)
hexagrams = []

for block in blocks[1:]:  # 跳过标题
    lines = block.split('\n')
    title = lines[0].strip()
    # 提取卦名
    m = re.match(r'(.+?)（', title)
    gua_name = m.group(1) if m else title.split('（')[0]

    # 按 ### 分段
    sections = {}
    current = None
    buf = []
    for line in lines[1:]:
        if line.startswith('### '):
            if current:
                sections[current] = '\n'.join(buf)
            current = line[4:].strip()
            buf = []
        else:
            buf.append(line)
    if current:
        sections[current] = '\n'.join(buf)

    # 提取人间道的关键判语
    renjian = sections.get('人间道', '')
    # 提取卜筮用例
    bushi = sections.get('卜筮用例', '')
    # 提取卦象/卦德
    guaxiang = sections.get('卦象 / 卦德', '')

    # 提取引文（「...」格式）
    def extract_quotes(text):
        quotes = re.findall(r'「(.+?)」', text)
        # 过滤太短的
        return [q for q in quotes if len(q) > 10]

    hexagrams.append({
        'name': gua_name,
        'renjian_quotes': extract_quotes(renjian)[:5],
        'bushi_quotes': extract_quotes(bushi)[:5],
        'guaxiang_quotes': extract_quotes(guaxiang)[:3],
        'has_renjian': bool(renjian.strip()),
        'has_bushi': bool(bushi.strip()),
    })

print(f"共提取 {len(hexagrams)} 卦")
print(f"有人间道: {sum(1 for h in hexagrams if h['has_renjian'])}")
print(f"有卜筮用例: {sum(1 for h in hexagrams if h['has_bushi'])}")
print()

# 输出前8卦的关键断言
for h in hexagrams[:8]:
    print(f"=== {h['name']} ===")
    if h['renjian_quotes']:
        print("人间道:")
        for q in h['renjian_quotes'][:3]:
            print(f"  - {q[:80]}...")
    if h['bushi_quotes']:
        print("卜筮:")
        for q in h['bushi_quotes'][:2]:
            print(f"  - {q[:80]}...")
    print()

# 保存完整JSON
out = Path(r"D:\TODAY\backend\data\research\nihai_64gua_extract.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(hexagrams, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"已保存到 {out}")
