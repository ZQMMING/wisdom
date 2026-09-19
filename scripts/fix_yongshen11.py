# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例5: 身弱+印旺+财有气时用财破印, 而不是印扶身
# 丙申己亥庚辰戊寅: 印星土旺(ben=2,stem=2), 财星木有根(寅), 原文用木破印, 引擎输出土
old = """        if primary is None and tier in SHUAI_TIER:
            if qi(t['yin']): P(t['yin'],'FUYI','身弱用印，生我扶身')
            elif qi(t['bi']): P(t['bi'],'FUYI','身弱用比劫帮身')
            else: P(t['yin'],'FUYI','身弱印比微，取印待运扶身')
            S(t['bi'] if primary==t['yin'] else t['yin'],''); A(t['cai'],t['guan'],t['shi'])"""
new = """        if primary is None and tier in SHUAI_TIER:
            if (cs(t['yin']) or ben(t['yin'])>=2) and qi(t['cai']):
                P(t['cai'],'BINGYAO','身弱印旺成势反为病，财星有气破印为用(案例5丙申己亥庚辰戊寅印旺用木破印)'); S(t['shi'],'食伤生财'); A(t['yin'],'印旺为病')
            elif qi(t['yin']): P(t['yin'],'FUYI','身弱用印，生我扶身')
            elif qi(t['bi']): P(t['bi'],'FUYI','身弱用比劫帮身')
            else: P(t['yin'],'FUYI','身弱印比微，取印待运扶身')
            S(t['bi'] if primary==t['yin'] else t['yin'],''); A(t['cai'],t['guan'],t['shi'])"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('身弱印旺财破印修复完成')
