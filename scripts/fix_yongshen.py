# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复1: gen_zheng增加比劫透干帮身判断
old1 = "    gen_zheng = yin_load or dm_ben_real or _yueyin_tuoshen"
new1 = "    gen_zheng = yin_load or dm_ben_real or _yueyin_tuoshen or stem(t['bi'])>=1  # 比劫透干帮身亦不从"
content = content.replace(old1, new1)

# 修复2: zw专旺增加CONFIRMED判断
old2 = "    if zw:"
new2 = "    zw_conf = bool(zw) and 'CONFIRMED' in (zw_state or '')\n    if zw and (zw_conf or not gen_zheng):  # 真专旺或假专旺无印比帮身才走专旺"
content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('修复完成')
