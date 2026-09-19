# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例6: 专旺格且食伤透干且日主成势时, 即使有比劫透干也走专旺泄秀路径
# 甲申丙子癸亥癸亥: 润下格+甲木食神透干+水成势, 原文用甲木泄秀, 但因癸水比劫透干被误判gen_zheng=True走调候火
old1 = "    zw_active = zw and (zw_conf or not gen_zheng)  # 真专旺或假专旺无印比帮身才触发专旺路径"
new1 = "    zw_active = zw and (zw_conf or not gen_zheng or (stem(t['shi'])>=1 and cs(t['dm'])))  # 真专旺/假专旺无印比/专旺且食伤透干日主成势(泄秀)才触发专旺路径; 案例6甲申丙子癸亥癸亥润下格用甲木泄秀"

content = content.replace(old1, new1)

old2 = "    if zw and (zw_conf or not gen_zheng):  # 真专旺或假专旺无印比帮身才走专旺"
new2 = "    if zw and (zw_conf or not gen_zheng or (stem(t['shi'])>=1 and cs(t['dm']))):  # 真专旺/假专旺无印比/专旺且食伤透干日主成势(泄秀)才走专旺"

content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('专旺格泄秀路径修复完成')
