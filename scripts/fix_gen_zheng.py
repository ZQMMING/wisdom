# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复gen_zheng: 专旺格本身就有比劫透干和日主本气根, 不应作为不从格条件
# 只有印星有根(yin_load)或月令印星托身(_yueyin_tuoshen)才是真不从
# 案例6甲申丙子癸亥癸亥: 润下格+甲木透干, 原文"用神必是甲木", 但因比劫透干被误判gen_zheng=True走调候火
old = "    gen_zheng = yin_load or dm_ben_real or _yueyin_tuoshen or stem(t['bi'])>=1  # 比劫透干帮身亦不从"
new = "    gen_zheng = yin_load or _yueyin_tuoshen  # 仅印星有根/月令印星托身才不从; 专旺格本身有比劫透干和日主根, 不作不从条件(案例6甲申丙子癸亥癸亥润下格用甲木泄秀)"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('gen_zheng修复完成')
