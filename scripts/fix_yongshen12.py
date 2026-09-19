# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例5: 官杀虚透无根时不输出印化杀, 继续走后面身弱扶抑的财破印路径
old = """                else:
                    P(t['yin'],'BINGYAO','官杀重身轻印无气，取印化杀待运'); S(t['bi'])
                    if tier in SHUAI_TIER: A(t['guan'],'杀重身轻印未到位，官杀再旺攻身忌')"""
new = """                elif cs(t['guan']) or ben(t['guan'])>=2 or (stem(t['guan'])>=1 and (ben(t['guan'])>=1 or ling(t['guan']) in ('旺','相'))):
                    P(t['yin'],'BINGYAO','官杀重身轻印无气，取印化杀待运'); S(t['bi'])
                    if tier in SHUAI_TIER: A(t['guan'],'杀重身轻印未到位，官杀再旺攻身忌')
                # 官杀虚透无根不重: 不印化杀, primary保持None继续走后面路径(案例5丙申己亥庚辰戊寅官杀虚透+印旺用财破印)"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('官杀虚透不印化杀修复完成')
