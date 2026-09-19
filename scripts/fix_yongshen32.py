# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在官杀制化路径最前面(if tier in WANG_TIER:之后)直接判断提纲不照用印
old = """                if tier in WANG_TIER:
                    if zhi_ok and ben(t['guan'])==0 and ling(t['shi'])=='旺' and not _tigang_buzhao:"""
new = """                if tier in WANG_TIER:
                    if _tigang_buzhao:
                        P(t['yin'],'BINGYAO','提纲不照：月令本气不透，印星透干有根为用(透金为用神)'); S(t['bi'],'比劫帮身'); _zhuan_shi=True
                    elif zhi_ok and ben(t['guan'])==0 and ling(t['shi'])=='旺':"""
content = content.replace(old, new)

# 移除第343行的and not _tigang_buzhao(因为已经在前面判断了)
old2 = """                    elif zhi_ok and ben(t['guan'])==0 and ling(t['shi'])=='旺':"""
new2 = """                    elif zhi_ok and ben(t['guan'])==0 and ling(t['shi'])=='旺':"""
content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('提纲不照官杀制化路径最前面判断修复完成')
