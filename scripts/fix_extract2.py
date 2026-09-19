# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_accuracy3.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改天干开头的正则, 允许中间有其他文字(0-30个非句号字符)
old = """    for m in re.finditer(r'([甲乙丙丁戊己庚辛壬癸][木火土金水]?)[^，。；！？\\s]{0,4}，?而为用喜神', all_text):
        results.update(extract_wuxing(m.group(1)))"""

new = """    for m in re.finditer(r'([甲乙丙丁戊己庚辛壬癸][木火土金水]?)[^。]{0,30}?而为用喜神', all_text):
        results.update(extract_wuxing(m.group(1)))"""

c = c.replace(old, new)
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('对齐脚本天干提取正则放宽完成')
