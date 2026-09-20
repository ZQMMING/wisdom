# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    lines = f.readlines()

# 在伤官制杀后面增加印旺用财病药结构
insert_after = None
for i, line in enumerate(lines):
    if "A(t['yin'],'印克食伤破格')" in line:
        insert_after = i
        break

if insert_after:
    new_lines = [
        "\n",
        "    # V4.33: 印旺用财: 印星成势(stem>=2且ben>=2)且财星透干，病药用财破印\n",
        "    if primary is None and stem(t['yin'])>=2 and ben(t['yin'])>=2 and stem(t['cai'])>=1:\n",
        "        P(t['cai'],'BINGYAO','印旺用财: 印星成势透干有根，财星透干破印为用')\n",
        "        S(t['shi'],'食伤生财'); A(t['yin'],'印旺为病被破'); A(t['guan'],'官杀生印助病')\n",
    ]
    lines = lines[:insert_after+1] + new_lines + lines[insert_after+1:]
    print(f'在第{insert_after+1}行后插入印旺用财病药结构')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.writelines(lines)
print('yongshen_engine.py V4.33完成(印旺用财病药结构)')
