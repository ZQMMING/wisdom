# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复案例6: 专旺格且食伤透干且日主成势时, 即使有比劫透干也走专旺路径(食伤泄秀)
# 甲申丙子癸亥癸亥: 润下格+甲木透干, 原文"用神必是甲木", 但因比劫透干被误判gen_zheng=True走调候火
old = "    zw_active = zw and (zw_conf or not gen_zheng)  # 真专旺或假专旺无印比帮身才触发专旺路径"
new = "    zw_active = zw and (zw_conf or not gen_zheng or (stem(sw)>=1 and cs(dmw)))  # 真专旺/假专旺无印比/专旺且食伤透干日主成势(泄秀)才触发专旺路径; 案例6甲申丙子癸亥癸亥润下格用甲木泄秀"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('zw_active修复完成')
