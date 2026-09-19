# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 改进B4b排除条件: 印星当令且印成势/印透干即认为日主有气, 用食伤泄秀而非财破印
old1 = "                and not (ling(t['yin'])=='旺' and (cs(dmw) or ben(dmw)>=1 or stem(dmw)>=1)):"
new1 = "                and not (ling(t['yin'])=='旺' and (cs(dmw) or ben(dmw)>=1 or stem(dmw)>=1 or cs(t['yin']) or stem(t['yin'])>=1)):"
content = content.replace(old1, new1)

# 改进"印星当令且日主有气"路径条件: 同样放宽
old2 = "        if primary is None and ling(t['yin'])=='旺' and (cs(dmw) or ben(dmw)>=1 or stem(dmw)>=1) \\"
new2 = "        if primary is None and ling(t['yin'])=='旺' and (cs(dmw) or ben(dmw)>=1 or stem(dmw)>=1 or cs(t['yin']) or stem(t['yin'])>=1) \\"
content = content.replace(old2, new2)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('改进完成')
