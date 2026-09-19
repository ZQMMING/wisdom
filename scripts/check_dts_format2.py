# -*- coding: utf-8 -*-
dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
with open(dts_path, encoding='utf-8-sig') as f:
    content = f.read()

print('文件长度:', len(content))
print('前200字:', content[:200])
print()

# 搜索各种格式
charts = ['辛卯丁酉庚午丙子', '辛卯 丁酉 庚午 丙子', '辛卯　丁酉　庚午　丙子']
for chart in charts:
    idx = content.find(chart)
    print('搜索 "%s": pos=%d' % (chart, idx))

# 搜索"庚午丙子"
idx = content.find('庚午丙子')
print('搜索 "庚午丙子": pos=%d' % idx)
if idx >= 0:
    print('上下文:', content[max(0,idx-100):idx+200])
