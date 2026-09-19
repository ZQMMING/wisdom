# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 用更简单的ben>=3判断水专旺
old = "        _shui_zhuanwang = (cs(t['bi']) or ben(t['bi'])>=3) and stem(t['shi'])>=1 and dmw=='水'"
new = "        _shui_zhuanwang = (ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1)) and stem(t['shi'])>=1 and dmw=='水'"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('水专旺条件简化完成')
