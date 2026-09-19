# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 用正确格式在P函数添加调试print
old = """    def P(w,path,note):
        nonlocal primary
        if w and w in WUXING and primary is None:
            primary=w; paths.append(path); notes[w]=note"""
new = """    def P(w,path,note):
        nonlocal primary
        if w and w in WUXING and primary is None:
            if dm=='壬' and mz=='寅': print(f'DEBUG P: w={w}, path={path}, note={note[:40]}')
            primary=w; paths.append(path); notes[w]=note"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('P函数调试print正确添加完成')
