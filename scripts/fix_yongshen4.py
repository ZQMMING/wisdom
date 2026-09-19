# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复zheng定义: 用zw_active而不是zw
old1 = "    zheng=(not zw) and (not lq) and (not hua_conf) and (not hua_youqing) and (not cong_shun)"
new1 = "    zw_active = zw and (zw_conf or not gen_zheng)  # 真专旺或假专旺无印比帮身才触发专旺路径\n    zheng=(not zw_active) and (not lq) and (not hua_conf) and (not hua_youqing) and (not cong_shun)"
content = content.replace(old1, new1)

# 修复zw路径判断: 用zw_active而不是重复条件
old2 = "    if zw and (zw_conf or not gen_zheng):  # 真专旺或假专旺无印比帮身才走专旺; 有印比帮身回正格"
new2 = "    if zw_active:"
content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('zheng定义bug修复完成')
