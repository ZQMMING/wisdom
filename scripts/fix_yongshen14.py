# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 兜底调候前增加双重保险: 印旺+财有气时优先财破印(案例5丙申己亥庚辰戊寅)
old = """        # 兜底: 所有路径都不满足时, 确保有primary输出(避免None)
        if primary is None:
            if hou:"""
new = """        # 兜底前双重保险: 印旺+财有气时优先财破印(案例5丙申己亥庚辰戊寅印旺用木破印)
        if primary is None and (cs(t['yin']) or ben(t['yin'])>=2) and qi(t['cai']):
            P(t['cai'],'BINGYAO','印旺成势反为病，财星有气破印为用(兜底前保险)'); S(t['shi'],'食伤生财'); A(t['yin'],'印旺为病')
        # 兜底: 所有路径都不满足时, 确保有primary输出(避免None)
        if primary is None:
            if hou:"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('兜底前财破印保险修复完成')
