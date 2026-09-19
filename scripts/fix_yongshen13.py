# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例5: 食伤成势身弱但印星已旺时, 不用印制食伤(印更壅塞), 继续走身弱扶抑财破印
old = """        if primary is None and cs(t['shi']) and tier in SHUAI_TIER:
            P(t['yin'],'BINGYAO','食伤泄气太过，印制食伤扶身'); S(t['bi']); A(t['shi'],t['cai'])"""
new = """        if primary is None and cs(t['shi']) and tier in SHUAI_TIER and not (cs(t['yin']) or ben(t['yin'])>=2):
            P(t['yin'],'BINGYAO','食伤泄气太过，印制食伤扶身'); S(t['bi']); A(t['shi'],t['cai'])
        # 印星已旺时不印制食伤(印更壅塞), primary保持None继续走身弱扶抑财破印(案例5丙申己亥庚辰戊寅印旺用木破印)"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('食伤成势印旺不印制修复完成')
