# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 回退专旺格泄秀路径激进修改(导致大量命例导出失败)
old1 = "    zw_active = zw and (zw_conf or not gen_zheng or (stem(t['shi'])>=1 and cs(t['dm'])))  # 真专旺/假专旺无印比/专旺且食伤透干日主成势(泄秀)才触发专旺路径; 案例6甲申丙子癸亥癸亥润下格用甲木泄秀"
new1 = "    zw_active = zw and (zw_conf or not gen_zheng)  # 真专旺或假专旺无印比帮身才触发专旺路径"

content = content.replace(old1, new1)

old2 = "    if zw and (zw_conf or not gen_zheng or (stem(t['shi'])>=1 and cs(t['dm']))):  # 真专旺/假专旺无印比/专旺且食伤透干日主成势(泄秀)才走专旺"
new2 = "    if zw and (zw_conf or not gen_zheng):  # 真专旺或假专旺无印比帮身才走专旺"

content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('专旺格泄秀路径激进修改已回退')
