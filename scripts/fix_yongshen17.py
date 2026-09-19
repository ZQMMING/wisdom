# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在仲冬调候路径前增加印旺+财有气优先财破印
old = """        # B6 调候兜底 / 扶抑
        if primary is None and mz in MIDWINTER and (ben('火')>=1 or ling('火') in ('旺','相') or d('火')['zhong_n']+d('火')['yu_n']>=1 or stem('火')>=2):
            P('火','QIHOU','仲冬寒凝无制化，取火调候待运(火有根/有气)')"""
new = """        # B6 调候兜底 / 扶抑
        # 印旺+财有气时优先财破印, 优先于仲冬调候(案例5丙申己亥庚辰戊寅亥月印旺用木破印, 不走调候火)
        _yin_wang_b6 = (ben(t['yin'])>=2) or (ben(t['yin'])>=1 and stem(t['yin'])>=2)
        _cai_youqi_b6 = (ben(t['cai'])>=1) or (stem(t['cai'])>=1) or (ling(t['cai']) in ('旺','相'))
        if primary is None and _yin_wang_b6 and _cai_youqi_b6:
            P(t['cai'],'BINGYAO','印旺成势反为病，财星有气破印为用(优先于调候)'); S(t['shi'],'食伤生财'); A(t['yin'],'印旺为病')
        elif primary is None and mz in MIDWINTER and (ben('火')>=1 or ling('火') in ('旺','相') or d('火')['zhong_n']+d('火')['yu_n']>=1 or stem('火')>=2):
            P('火','QIHOU','仲冬寒凝无制化，取火调候待运(火有根/有气)')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('仲冬调候前财破印优先修复完成')
