# -*- coding: utf-8 -*-
dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
with open(dts_path, encoding='utf-8') as f:
    content = f.read()

# 查找几个命例的位置
charts = ['辛卯丁酉庚午丙子', '庚申庚辰戊辰戊午', '辛酉辛丑己酉丙寅', '丁巳壬子辛巳丁酉']
for chart in charts:
    idx = content.find(chart)
    if idx >= 0:
        print('=== %s (pos=%d) ===' % (chart, idx))
        print(content[max(0,idx-50):idx+400])
        print()
