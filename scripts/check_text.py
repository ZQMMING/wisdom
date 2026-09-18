# -*- coding: utf-8 -*-
import csv, re
GZ = r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ_RE = re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')
lines=open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt',encoding='utf-8').readlines()
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
for r in rows[:5]:
    ln=int(r['line'])
    start=ln+2
    end=start
    while end < len(lines):
        l=lines[end].strip()
        if l.startswith('八字：') or l.startswith('====') or l.startswith('【') or BZ_RE.match(l):
            break
        end+=1
    text=''.join(lines[start:end])
    print(f"{r['chart']}: text_len={len(text)}, 有身旺={'身旺' in text}, 有得地={'得地' in text}")
