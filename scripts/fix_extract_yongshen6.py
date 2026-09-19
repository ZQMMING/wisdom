# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_all_books.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 修改extract_yongshen开头的优先匹配，增加五行匹配
old = """def extract_yongshen(raw):
    \"\"\"从原文中提取用神判断 - V4优化版：优先匹配命例正文明确用神\"\"\"
    # V4: 最优先匹配"以X为用"这种命例正文明确用神，避免被后面注解覆盖
    import re as _re
    m = _re.search(r'以([甲乙丙丁戊己庚辛壬癸])为用', raw)
    if m:
        return WX.get(m.group(1), m.group(1))
    # 高优先级模式: 明确的用神判断"""

new = """def extract_yongshen(raw):
    \"\"\"从原文中提取用神判断 - V5优化版：优先匹配命例正文明确用神，支持天干和五行\"\"\"
    # V5: 最优先匹配"以X为用"，X可以是天干或五行，避免被后面注解覆盖
    import re as _re
    m = _re.search(r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用', raw)
    if m:
        g = m.group(1)
        return WX.get(g, g)
    # 高优先级模式: 明确的用神判断"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_yongshen_all_books.py V5完成(增加五行匹配)')
