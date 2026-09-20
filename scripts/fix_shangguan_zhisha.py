# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    lines = f.readlines()

# 在枭印夺食后面增加伤官制杀病药结构
insert_after = None
for i, line in enumerate(lines):
    if 'A(t[\'yin\'],\'印旺克食为病\')' in line:
        insert_after = i
        break

if insert_after:
    new_lines = [
        "    # V4.32: 伤官制杀: 官杀透干有力(stem>=2或当令)且食伤透干有根，病药用食伤制杀\n",
        "    if primary is None and (stem(t['guan'])>=2 or ling(t['guan'])=='旺') \\\n",
        "            and stem(t['shi'])>=1 and (ben(t['shi'])>=1 or d(t['shi']).get('zhong_n',0)+d(t['shi']).get('yu_n',0)>=1):\n",
        "        P(t['shi'],'BINGYAO','伤官制杀: 官杀有力透干，食伤透干有根制官杀为用')\n",
        "        S(t['cai'],'食伤生财'); A(t['guan'],'官杀为病被制'); A(t['yin'],'印克食伤破格')\n",
        "\n",
    ]
    lines = lines[:insert_after+1] + new_lines + lines[insert_after+1:]
    print(f'在第{insert_after+1}行后插入伤官制杀病药结构')

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.writelines(lines)
print('yongshen_engine.py V4.32完成(伤官制杀病药结构)')
