# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在P函数添加调试输出(仅庚申戊寅壬子甲辰)
old = """    def P(w, path, note=''):
        nonlocal primary
        primary=w; paths.append(path); notes[w]=note"""
new = """    def P(w, path, note=''):
        nonlocal primary
        if dm=='壬' and mz=='寅': print(f'DEBUG P: w={w}, path={path}, note={note[:30]}')
        primary=w; paths.append(path); notes[w]=note"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('P函数调试print添加完成')
