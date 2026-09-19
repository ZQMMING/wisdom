# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例9: 仲冬调候火必须有根/有气才用, 虚透无根时不走调候路径
# 己丑丙子辛酉壬辰: 丙火虚透无根(ben=0, ling=死), 原文"虚火无根，必以水为用神也"
old = """        if primary is None and mz in MIDWINTER:
            P('火','QIHOU','仲冬寒凝无制化，取火调候待运')"""
new = """        if primary is None and mz in MIDWINTER and (ben('火')>=1 or ling('火') in ('旺','相') or d('火')['zhong_n']+d('火')['yu_n']>=1 or stem('火')>=2):
            P('火','QIHOU','仲冬寒凝无制化，取火调候待运(火有根/有气)')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('仲冬调候火判断修复完成')
