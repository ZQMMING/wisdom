# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 直接在兜底调候路径最前面增加印旺+财有气优先财破印
old = """        # 兜底: 所有路径都不满足时, 确保有primary输出(避免None)
        if primary is None:
            if hou:
                P(sorted(hou)[0],'QIHOU','兜底取调候候神(所有结构化路径未命中)')"""
new = """        # 兜底: 所有路径都不满足时, 确保有primary输出(避免None)
        if primary is None:
            # 最优先: 印旺+财有气时财破印(案例5丙申己亥庚辰戊寅印旺用木破印, 不走调候火)
            if (cs(t['yin']) or ben(t['yin'])>=2) and qi(t['cai']):
                P(t['cai'],'BINGYAO','印旺成势反为病，财星有气破印为用(兜底最优先)'); S(t['shi'],'食伤生财'); A(t['yin'],'印旺为病')
            elif hou:
                P(sorted(hou)[0],'QIHOU','兜底取调候候神(所有结构化路径未命中)')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('兜底最优先财破印修复完成')
