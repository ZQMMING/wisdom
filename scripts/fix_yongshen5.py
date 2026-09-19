# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 移除原来在if zw之前的zw_conf定义(位置不对)
old1 = "    zw_conf = bool(zw) and 'CONFIRMED' in (zw_state or '')\n    if zw_active:"
new1 = "    if zw_active:"
content = content.replace(old1, new1)

# 在gen_zheng定义之后添加zw_conf和zw_active
old2 = "    gen_zheng = yin_load or dm_ben_real or _yueyin_tuoshen or stem(t['bi'])>=1  # 比劫透干帮身亦不从"
new2 = """    gen_zheng = yin_load or dm_ben_real or _yueyin_tuoshen or stem(t['bi'])>=1  # 比劫透干帮身亦不从
    zw_conf = bool(zw) and 'CONFIRMED' in (zw_state or '')
    zw_active = zw and (zw_conf or not gen_zheng)  # 真专旺或假专旺无印比帮身才触发专旺路径"""
content = content.replace(old2, new2)

# 移除重复的zw_active定义(在zheng定义行)
old3 = "    zw_active = zw and (zw_conf or not gen_zheng)  # 真专旺或假专旺无印比帮身才触发专旺路径\n    zheng=(not zw_active) and (not lq) and (not hua_conf) and (not hua_youqing) and (not cong_shun)"
new3 = "    zheng=(not zw_active) and (not lq) and (not hua_conf) and (not hua_youqing) and (not cong_shun)"
content = content.replace(old3, new3)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('zw_conf位置修复完成')
