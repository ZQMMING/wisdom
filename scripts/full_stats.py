# -*- coding: utf-8 -*-
"""统计完整信息案例数: 八字+大运+断语."""
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
            # 大运在下一行
            dy = ''
            if i+1 < len(lines): dy = lines[i+1]
            dy_pairs = GZ.findall(dy)
            # 断语在后面10行
            duanyu = ''
            for j in range(i+2, min(i+12, len(lines))):
                if lines[j].strip():
                    duanyu += lines[j].strip() + ' '
            records.append({
                'src_line': i+1,
                'pillars': pairs,
                'has_dayun': len(dy_pairs) >= 2,
                'has_duanyu': len(duanyu) > 50,
                'duanyu_len': len(duanyu),
            })
        continue
    pairs = GZ.findall(s)
    if len(pairs) == 4 and len(s) < 60:
        cleaned = GZ.sub('', s).replace(' ', '').replace('\u3000', '')
        if cleaned == '':
            dy = ''
            if i+1 < len(lines): dy = lines[i+1]
            dy_pairs = GZ.findall(dy)
            duanyu = ''
            for j in range(i+2, min(i+12, len(lines))):
                if lines[j].strip():
                    duanyu += lines[j].strip() + ' '
            records.append({
                'src_line': i+1,
                'pillars': pairs,
                'has_dayun': len(dy_pairs) >= 2,
                'has_duanyu': len(duanyu) > 50,
                'duanyu_len': len(duanyu),
            })

total = len(records)
has_dy = sum(1 for r in records if r['has_dayun'])
has_dy_dy = sum(1 for r in records if r['has_dayun'] and r['has_duanyu'])
has_all = sum(1 for r in records if r['has_dayun'] and r['has_duanyu'])

print('DTS 513命例完整信息统计:')
print(f'总命例: {total}')
print(f'有八字: {total}')
print(f'有大运: {has_dy} ({has_dy/total*100:.1f}%)')
print(f'有八字+大运+断语: {has_dy_dy} ({has_dy_dy/total*100:.1f}%)')
print(f'完整(八字+大运+断语>50字): {has_all} ({has_all/total*100:.1f}%)')
