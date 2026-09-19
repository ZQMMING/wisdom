# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.7: 直接用BRANCH_WX检查地支中是否有克化神的五行
# 问题: wuxing_power字段名可能不对，导致_hua_suppressed计算错误
# 优化: 直接遍历地支，用BRANCH_WX检查是否有克化神的五行

old = """    # ---------- A 化气 / 从顺 / 专旺 / 成象 ----------
    # V4.6: 化神被克制时即使CONFIRMED也不走化气格路径(QT-0040化金气格但午火克金)
    _hua_ke = KE.get(hua_hwx) if hua_hwx else None
    _hua_ke_pow = wuxing_power.get('wuxing_power', {}).get(_hua_ke, {}) if _hua_ke else {}
    _hua_suppressed = bool(_hua_ke) and (
        int(_hua_ke_pow.get('ben_n', 0)) >= 1 or
        int(_hua_ke_pow.get('ju_n', 0)) >= 1 or
        int(_hua_ke_pow.get('stem_n', 0)) >= 1
    )
    if hua_conf and not _hua_suppressed:"""

new = """    # ---------- A 化气 / 从顺 / 专旺 / 成象 ----------
    # V4.7: 直接用BRANCH_WX检查地支中是否有克化神的五行(QT-0040化金气格但午火克金)
    _hua_ke = KE.get(hua_hwx) if hua_hwx else None
    _hua_suppressed = bool(_hua_ke) and any(BRANCH_WX.get(b) == _hua_ke for b in brs)
    if hua_conf and not _hua_suppressed:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.7完成(直接用BRANCH_WX检查地支中是否有克化神的五行)')
