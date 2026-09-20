# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_all_books.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = "m = _re.search(r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用', raw)"
new = "m = _re.search(r'以([甲乙丙丁戊己庚辛壬癸水火木金土])为用(?!者)', raw)"
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('V5.1修改完成: 排除以X为用者')
