# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_all_books.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V3: extract_yongshen增加注解截断逻辑
old = """def extract_yongshen(raw):
    \"\"\"从原文中提取用神判断 - V2优化版\"\"\"
    # 高优先级模式: 明确的用神判断"""

new = """def extract_yongshen(raw):
    \"\"\"从原文中提取用神判断 - V3优化版：只提取命例正文，截断注解部分\"\"\"
    # V3: 截断注解/评论部分，只保留命例正文
    cut_markers = ['【原注】', '【任氏曰】', '徐乐吾曰', '楠曰', '【白话释意】', '【释义】']
    main_text = raw
    for marker in cut_markers:
        idx = main_text.find(marker)
        if idx > 0:
            main_text = main_text[:idx]
    raw = main_text

    # 高优先级模式: 明确的用神判断"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_yongshen_all_books.py V3完成(extract_yongshen增加注解截断)')
