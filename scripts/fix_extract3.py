# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_accuracy3.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在extract_yongshen_wuxing函数中增加"必以X为用"提取模式
old = """    for m in re.finditer(r'用神([^，。；！？\\s]{1,4})[伤尽去损]', all_text):
        results.update(extract_wuxing(m.group(1)))
    return results"""

new = """    for m in re.finditer(r'用神([^，。；！？\\s]{1,4})[伤尽去损]', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'必以([^，。；！？\\s]{1,6})为用', all_text):
        results.update(extract_wuxing(m.group(1)))
    return results"""

c = c.replace(old, new)
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('对齐脚本增加必以X为用提取模式完成')
