# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    lines = f.readlines()

# 修改第308-310行（索引307-309）
for i, line in enumerate(lines):
    if 'V4.31: 枭印夺食' in line:
        lines[i] = "    # V4.31: 枭印夺食: 印星极旺(ben>=3或当令ben>=2)且食伤当令(月令本气)被印克，病药用食伤泄秀\n"
    elif 'if primary is None and (ben(t[\'yin\'])>=2 or cs(t[\'yin\']))' in line and 'BRANCH_WX' in line:
        lines[i] = "    if primary is None and (ben(t['yin'])>=3 or (ling(t['yin'])=='旺' and ben(t['yin'])>=2)) \\\n            and BRANCH_WX.get(mz)==t['shi'] and ben(t['shi'])>=1:\n"
    elif '枭印夺食: 印星成势克当令食伤' in line:
        lines[i] = "        P(t['shi'],'BINGYAO','枭印夺食: 印星极旺克当令食伤，病在印、药在食，用食伤泄秀卫食')\n"

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.writelines(lines)
print('yongshen_engine.py V4.31修正完成(直接修改行)')
