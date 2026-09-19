# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例8: 官杀不成势+食伤当令旺(ben>=2且ling=旺)时印制食伤扶身
# 之前条件ben>=3太窄, 案例8丁亥辛亥辛未壬辰ben=2但月令旺, 原文"用神在土不在火也"
old1 = "                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])) and not (cs(t['guan']) and ben(dmw)>=1 and stem(t['bi'])==0) and not (not cs(t['guan']) and ben(t['shi'])>=3):"
new1 = "                elif zhi_ok and (ben(t['shi'])>=1 or cs(t['shi'])) and not (cs(t['guan']) and ben(dmw)>=1 and stem(t['bi'])==0) and not (not cs(t['guan']) and (ben(t['shi'])>=3 or (ben(t['shi'])>=2 and ling(t['shi'])=='旺'))):"

content = content.replace(old1, new1)

old2 = "                elif zhi_ok and not cs(t['guan']) and ben(t['shi'])>=3:"
new2 = "                elif zhi_ok and not cs(t['guan']) and (ben(t['shi'])>=3 or (ben(t['shi'])>=2 and ling(t['shi'])=='旺')):"

content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('案例8修复完成')
