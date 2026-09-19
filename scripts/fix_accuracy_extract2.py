# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_accuracy3.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 增加正则: 匹配"X而为用喜神"模式(案例7庚寅戊子甲寅丙寅: 丙火清透...而为用喜神)
old = "    for m in re.finditer(r'用神([^，。；！？\\s]{1,4})[伤尽去损]', all_text):"
new = """    for m in re.finditer(r'([^，。；！？\\s]{1,6})而为用喜神', all_text):
        results.update(extract_wuxing(m.group(1)))
    for m in re.finditer(r'用神([^，。；！？\\s]{1,4})[伤尽去损]', all_text):"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('提取正则增加完成')
