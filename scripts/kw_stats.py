# -*- coding: utf-8 -*-
"""统计案例里有身强身弱有根无根的案例数."""
import re, sys
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

records = []
for i, ln in enumerate(lines):
    s = ln.strip()
    if s.startswith('八字'):
        body = s.split('：', 1)[-1].split(':', 1)[-1].strip()
        pairs = GZ.findall(body)
        if len(pairs) == 4:
            duanyu = ''
            for j in range(i+2, min(i+12, len(lines))):
                if lines[j].strip():
                    duanyu += lines[j].strip() + ' '
            records.append({'src_line': i+1, 'pillars': pairs, 'duanyu': duanyu[:300]})
        continue
    pairs = GZ.findall(s)
    if len(pairs) == 4 and len(s) < 60:
        cleaned = GZ.sub('', s).replace(' ', '').replace('\u3000', '')
        if cleaned == '':
            duanyu = ''
            for j in range(i+2, min(i+12, len(lines))):
                if lines[j].strip():
                    duanyu += lines[j].strip() + ' '
            records.append({'src_line': i+1, 'pillars': pairs, 'duanyu': duanyu[:300]})

# 统计关键词
kw_counts = {
    '身旺': 0,
    '身弱': 0,
    '身强': 0,
    '身衰': 0,
    '旺': 0,
    '衰': 0,
    '有根': 0,
    '无根': 0,
    '根重': 0,
    '根轻': 0,
    '得时': 0,
    '失时': 0,
    '得令': 0,
    '失令': 0,
    '得地': 0,
    '得势': 0,
}

for r in records:
    dy = r['duanyu']
    for kw in kw_counts:
        if kw in dy:
            kw_counts[kw] += 1

print('DTS 513命例关键词统计:')
print(f'总命例: {len(records)}')
print()
for kw, cnt in sorted(kw_counts.items(), key=lambda x: -x[1]):
    print(f'  {kw:6s} {cnt:4d} ({cnt/len(records)*100:.1f}%)')
