# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 回退gen_zheng修改
old = "    gen_zheng = yin_load or _yueyin_tuoshen  # 仅印星有根/月令印星托身才不从; 专旺格本身有比劫透干和日主根, 不作不从条件(案例6甲申丙子癸亥癸亥润下格用甲木泄秀)"
new = "    gen_zheng = yin_load or dm_ben_real or _yueyin_tuoshen or stem(t['bi'])>=1  # 比劫透干帮身亦不从"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('gen_zheng回退完成')
