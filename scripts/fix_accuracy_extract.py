# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_accuracy3.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复原文用神提取: 排除"以X为仇神/忌神"中的X被误提取
old = "    for m in re.finditer(r'[用取以]([^，。；！？\\s]{1,4})[为用]', all_text):"
new = "    for m in re.finditer(r'[用取以]([^，。；！？\\s]{1,4})[为用](?!仇|忌)', all_text):"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('对齐脚本提取逻辑修复完成')
