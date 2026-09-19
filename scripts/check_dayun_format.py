# -*- coding: utf-8 -*-
"""查看DTS大运断语格式."""
dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
with open(dts_path, encoding='utf-8-sig') as f:
    content = f.read()

# 找一个有大运的命例, 查看大运断语格式
import re
chart_pattern = re.compile(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s+[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s+[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s+[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]')

# 找前5个命例, 查看后面的大运断语
count = 0
for m in chart_pattern.finditer(content):
    if count >= 3:
        break
    chart = re.sub(r'\s+', '', m.group())
    # 查看后面800字
    ctx = content[m.end():m.end()+800]
    print('=== %s ===' % chart)
    print(ctx[:600])
    print()
    count += 1
