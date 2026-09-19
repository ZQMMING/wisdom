# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例9被误伤: 财有气必须透干或有本气根, ling=相不算(案例9财星木仅ling=相, 不透干无本气根, 不应财破印)
old = "        _cai_youqi_b6 = (ben(t['cai'])>=1) or (stem(t['cai'])>=1) or (ling(t['cai']) in ('旺','相'))"
new = "        _cai_youqi_b6 = (ben(t['cai'])>=1) or (stem(t['cai'])>=1)  # 财有气必须透干或有本气根, 仅ling=相不算(避免案例9误伤)"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('财有气条件收紧修复完成')
