# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_accuracy3.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在断语中遇到章节标题时截断
old = """    # 断语 = 当前命例结束到下一个命例开始
    context = content[end:next_pos]

    sentences = re.split(r'[。；！？\\n]', context)"""

new = """    # 断语 = 当前命例结束到下一个命例开始
    context = content[end:next_pos]
    # 遇到章节标题时截断(避免包含下一章内容)
    chapter_match = re.search(r'={3,}\\s*[^=]+\\s*={3,}', context)
    if chapter_match:
        context = context[:chapter_match.start()]

    sentences = re.split(r'[。；！？\\n]', context)"""

c = c.replace(old, new)
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('对齐脚本章节标题截断修复完成')
