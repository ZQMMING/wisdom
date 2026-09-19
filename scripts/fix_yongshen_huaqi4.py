# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.6: 化神被克制时即使CONFIRMED也不走化气格路径
# 问题: QT-0040戊子庚申乙丑壬午被判为化金气格CONFIRMED，但地支午火克金，化神被克制
# 原文说"专用午中一点丁火"，应该用丁火调候制杀，不是化金气格
# 优化: 化神被克制(克神有本气根/成势/透干)时，不走化气格路径，走正常扶抑/调候路径

old = """    # ---------- A 化气 / 从顺 / 专旺 / 成象 ----------
    # V4.5: 只有真化(CONFIRMED)才触发化气格路径，假化(CANDIDATE)走正常扶抑/调候路径
    if hua_conf:"""

new = """    # ---------- A 化气 / 从顺 / 专旺 / 成象 ----------
    # V4.6: 化神被克制时即使CONFIRMED也不走化气格路径(QT-0040化金气格但午火克金)
    _hua_ke = KE.get(hua_hwx) if hua_hwx else None
    _hua_ke_pow = wuxing_power.get('wuxing_power', {}).get(_hua_ke, {}) if _hua_ke else {}
    _hua_suppressed = bool(_hua_ke) and (
        int(_hua_ke_pow.get('ben_n', 0)) >= 1 or
        int(_hua_ke_pow.get('ju_n', 0)) >= 1 or
        int(_hua_ke_pow.get('stem_n', 0)) >= 1
    )
    if hua_conf and not _hua_suppressed:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.6完成(化神被克制时即使CONFIRMED也不走化气格路径)')
