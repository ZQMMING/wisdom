# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复问题2(案例9): 身旺官杀虚透无根时, 优先食伤泄秀而非官杀
old = """            elif stem(t['guan'])>=1: P(t['guan'],'FUYI','身旺官杀透干，用官杀克身成权(待根)')
            elif ben(t['guan'])==0 and stem(t['shi'])>=1: P(t['shi'],'FUYI','身旺官杀虚透无根，食伤制杀兼泄秀')"""
new = """            elif stem(t['guan'])>=1 and (ben(t['guan'])>=1 or ling(t['guan']) in ('旺','相') or d(t['guan'])['zhong_n']+d(t['guan'])['yu_n']>=1):
                P(t['guan'],'FUYI','身旺官杀透干有根/有气，用官杀克身成权')
            elif stem(t['guan'])>=1 and stem(t['shi'])>=1: P(t['shi'],'FUYI','身旺官杀虚透无根，食伤制杀兼泄秀(案例9己丑丙子辛酉壬辰虚火无根必以水为用)')
            elif stem(t['guan'])>=1: P(t['guan'],'FUYI','身旺官杀透干，用官杀克身成权(待根)')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('身旺官杀虚透判断修复完成')
