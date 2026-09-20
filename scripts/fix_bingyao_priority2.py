# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.31修正: 收紧枭印夺食条件，避免stem>=2 ben>=1的普通印星误触发
old = """    # V4.31: 枭印夺食: 印星成势(ben>=2或成局)且食伤当令(月令本气)被印克，病药用食伤泄秀
    if primary is None and (ben(t['yin'])>=2 or cs(t['yin'])) \\
            and BRANCH_WX.get(mz)==t['shi'] and ben(t['shi'])>=1:
        P(t['shi'],'BINGYAO','枭印夺食: 印星成势克当令食伤，病在印、药在食，用食伤泄秀卫食')"""

new = """    # V4.31: 枭印夺食: 印星极旺(ben>=3或当令ben>=2)且食伤当令(月令本气)被印克，病药用食伤泄秀
    if primary is None and (ben(t['yin'])>=3 or (ling(t['yin'])=='旺' and ben(t['yin'])>=2)) \\
            and BRANCH_WX.get(mz)==t['shi'] and ben(t['shi'])>=1:
        P(t['shi'],'BINGYAO','枭印夺食: 印星极旺克当令食伤，病在印、药在食，用食伤泄秀卫食')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.31修正完成(枭印夺食条件收紧)')
