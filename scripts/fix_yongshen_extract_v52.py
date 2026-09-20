# -*- coding: utf-8 -*-
"""V5.2: 用神提取增加五行匹配,扩大样本量"""
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_all_books.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改extract_yongshen函数,增加五行匹配
old = """def extract_yongshen(raw):
    \"\"\"从原文中提取用神判断 - V5优化版：优先匹配命例正文明确用神，支持天干和五行\"\"\"
    # V5: 最优先匹配"以X为用"，X可以是天干或五行，避免被后面注解覆盖
    import re as _re
    m = _re.search(r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用(?!者)', raw)
    if m:
        g = m.group(1)
        return WX.get(g, g)"""

new = """def extract_yongshen(raw):
    \"\"\"从原文中提取用神判断 - V5.2优化版：优先匹配命例正文明确用神，支持天干和五行\"\"\"
    # V5: 最优先匹配"以X为用"，X可以是天干或五行，避免被后面注解覆盖
    import re as _re
    m = _re.search(r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用(?!者)', raw)
    if m:
        g = m.group(1)
        return WX.get(g, g)
    # V5.2: 匹配五行用神模式
    wx_patterns = [
        r'用神必在([水火木金土])',
        r'用神在([水火木金土])',
        r'以([水火木金土])为用神',
        r'用神是([水火木金土])',
        r'用神为([水火木金土])',
        r'专用([水火木金土])',
        r'专取([水火木金土])',
        r'取([水火木金土])为用神',
        r'当以([水火木金土])为用神',
        r'必以([水火木金土])为用神',
        r'宜用([水火木金土])为用',
    ]
    for pat in wx_patterns:
        m = _re.search(pat, raw)
        if m:
            return m.group(1)"""

if old in c:
    c = c.replace(old, new)
    print('V5.2修改成功: 增加五行用神匹配')
else:
    print('未找到目标字符串')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
