# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 直接用ben/stem原始值判断印旺财有气, 绕过cs/qi函数
old = """            # 最优先: 印旺+财有气时财破印(案例5丙申己亥庚辰戊寅印旺用木破印, 不走调候火)
            if (cs(t['yin']) or ben(t['yin'])>=2) and qi(t['cai']):
                P(t['cai'],'BINGYAO','印旺成势反为病，财星有气破印为用(兜底最优先)'); S(t['shi'],'食伤生财'); A(t['yin'],'印旺为病')"""
new = """            # 最优先: 印旺+财有气时财破印(案例5丙申己亥庚辰戊寅印旺用木破印, 不走调候火)
            _yin_wang = (ben(t['yin'])>=2) or (ben(t['yin'])>=1 and stem(t['yin'])>=2)
            _cai_youqi = (ben(t['cai'])>=1) or (stem(t['cai'])>=1) or (ling(t['cai']) in ('旺','相'))
            if _yin_wang and _cai_youqi:
                P(t['cai'],'BINGYAO','印旺成势反为病，财星有气破印为用(兜底最优先)'); S(t['shi'],'食伤生财'); A(t['yin'],'印旺为病')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('兜底财破印用原始值判断修复完成')
