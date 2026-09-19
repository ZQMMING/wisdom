# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.7: 化神被克制则不判化气格(QT-0040戊子庚申乙丑壬午: 乙庚化金但午火克金)
old = """            hs = WUHE_HUASHEN.get((day_stem, other[0]))
            if not hs or hs not in pw:
                continue
            hd = pw[hs]"""

new = """            hs = WUHE_HUASHEN.get((day_stem, other[0]))
            if not hs or hs not in pw:
                continue
            # V4.7: 化神被克制则不判化气格(QT-0040戊子庚申乙丑壬午: 乙庚化金但午火克金)
            _KE_HUA = {'木':'金', '火':'水', '土':'木', '金':'火', '水':'土'}
            _ke_hs = _KE_HUA.get(hs)
            _all_branches = [pillars[k][1] for k in ('year','month','day','hour')]
            _hs_suppressed = bool(_ke_hs) and any(BRANCH_WX.get(b) == _ke_hs for b in _all_branches)
            if _hs_suppressed:
                continue
            hd = pw[hs]"""

if old in c:
    c = c.replace(old, new)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(c)
    print('special_pattern.py V4.7完成(化神被克制则不判化气格)')
else:
    print('ERROR: 未找到匹配的代码段')
