# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_all_books.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4: extract_yongshen调整策略：先从命例正文(截断通用注解)提取，没有再从完整原文提取
old = """def extract_yongshen(raw):
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

new = """def extract_yongshen(raw):
    \"\"\"从原文中提取用神判断 - V4优化版：先从命例正文提取，没有再从完整原文提取\"\"\"
    import re as _re
    # V4: 先截断DTS通用注解(【原注】【任氏曰】)，避免被通用注解误提取
    # 保留徐乐吾曰、楠曰等命例专属注解
    cut_markers = ['【原注】', '【任氏曰】', '【白话释意】', '【释义】']
    main_text = raw
    for marker in cut_markers:
        idx = main_text.find(marker)
        if idx > 0:
            main_text = main_text[:idx]

    def _extract(text):
        # 高优先级模式: 明确的用神判断"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_yongshen_all_books.py V4完成(extract_yongshen先正文后全文提取)')
