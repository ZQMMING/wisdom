# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    lines = f.readlines()

# 删除第230行（索引229）的重复else:
# 第229行（索引228）是原来的else:
# 第230行（索引229）是我插入的重复else:
if lines[228].strip() == 'else:' and lines[229].strip() == 'else:':
    del lines[229]
    print('删除第230行重复else:完成')
else:
    print('未找到重复else:，当前第229行:', repr(lines[228]), '第230行:', repr(lines[229]))

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.writelines(lines)
