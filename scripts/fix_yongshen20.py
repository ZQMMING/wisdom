# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复: 仲冬调候前财破印优先仅限仲冬(案例5丙申己亥庚辰戊寅亥月), 其他月份不走(避免辛亥庚寅丙子乙未寅月印绶格被误伤)
old = """        # 印旺+财有气时优先财破印, 优先于仲冬调候(案例5丙申己亥庚辰戊寅亥月印旺用木破印, 不走调候火)
        _yin_wang_b6 = (ben(t['yin'])>=2) or (ben(t['yin'])>=1 and stem(t['yin'])>=2)
        _cai_youqi_b6 = (ben(t['cai'])>=1) or (stem(t['cai'])>=1)  # 财有气必须透干或有本气根, 仅ling=相不算(避免案例9误伤)
        if primary is None and _yin_wang_b6 and _cai_youqi_b6:"""
new = """        # 印旺+财有气时优先财破印, 优先于仲冬调候(案例5丙申己亥庚辰戊寅亥月印旺用木破印, 不走调候火)
        # 仅限仲冬! 其他月份不走(避免辛亥庚寅丙子乙未寅月印绶格火虚木嫩用印护格被误伤)
        _yin_wang_b6 = (ben(t['yin'])>=2) or (ben(t['yin'])>=1 and stem(t['yin'])>=2)
        _cai_youqi_b6 = (ben(t['cai'])>=1) or (stem(t['cai'])>=1)  # 财有气必须透干或有本气根, 仅ling=相不算(避免案例9误伤)
        if primary is None and mz in MIDWINTER and _yin_wang_b6 and _cai_youqi_b6:"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('财破印优先仅限仲冬修复完成')
