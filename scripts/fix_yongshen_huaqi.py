# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.4: 修复假化有情判断过于激进的问题
# 问题: 假化有情第一个条件只要化神当令(月令本气=化神)就判为真，过于宽松
# 例如QT-0040戊子庚申乙丑壬午: 月令申金=化神金，但地支午火克金，化神被克制，不应判为假化有情
# 优化: 增加化神被克制的检查，如果化神的克神(KE[hua_hwx])有本气根/成势，则不判为假化有情

old = """    hua_youqing=False
    if hua_hwx and not hua_conf:
        _sh=SHENG_ME.get(hua_hwx)
        if (BRANCH_WX.get(mz)==hua_hwx) or \\
           (ben(hua_hwx)>=2 and (stem(hua_hwx)>=1 or (_sh and stem(_sh)>=1))) or \\
           (stem(hua_hwx)>=1 and ben(hua_hwx)>=1 and ben(dmw)==0 and ben(t['yin'])==0):
            hua_youqing=True"""

new = """    hua_youqing=False
    if hua_hwx and not hua_conf:
        _sh=SHENG_ME.get(hua_hwx)
        # V4.4: 化神被克制则不判假化有情(如QT-0040戊子庚申乙丑壬午: 化神金但地支午火克金)
        _ke_hua = KE.get(hua_hwx)
        _hua_suppressed = bool(_ke_hua) and (ben(_ke_hua)>=1 or cs(_ke_hua) or ling(_ke_hua) in ('旺','相'))
        if not _hua_suppressed:
            if (BRANCH_WX.get(mz)==hua_hwx) or \\
               (ben(hua_hwx)>=2 and (stem(hua_hwx)>=1 or (_sh and stem(_sh)>=1))) or \\
               (stem(hua_hwx)>=1 and ben(hua_hwx)>=1 and ben(dmw)==0 and ben(t['yin'])==0):
                hua_youqing=True"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.4完成(修复假化有情判断过于激进: 化神被克制则不判假化有情)')
