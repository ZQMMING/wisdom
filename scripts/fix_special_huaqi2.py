# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.7修正: 化神被克制时仍然判化气格，但状态只能是CANDIDATE(假化)，不能是CONFIRMED(真化)
# 问题: 之前完全去掉化气格导致己卯甲戌甲子己巳测试失败(期望化土CANDIDATE)
# 优化: 化神被克制时，强制hua_state=CANDIDATE，不影响化气格的识别

old = """            # V4.7: 化神被克制则不判化气格(QT-0040戊子庚申乙丑壬午: 乙庚化金但午火克金)
            _KE_HUA = {'木':'金', '火':'水', '土':'木', '金':'火', '水':'土'}
            _ke_hs = _KE_HUA.get(hs)
            _all_branches = [pillars[k][1] for k in ('year','month','day','hour')]
            _hs_suppressed = bool(_ke_hs) and any(BRANCH_WX.get(b) == _ke_hs for b in _all_branches)
            if _hs_suppressed:
                continue
            hd = pw[hs]"""

new = """            # V4.7: 化神被克制时只能是CANDIDATE(假化)，不能是CONFIRMED(真化)
            _KE_HUA = {'木':'金', '火':'水', '土':'木', '金':'火', '水':'土'}
            _ke_hs = _KE_HUA.get(hs)
            _all_branches = [pillars[k][1] for k in ('year','month','day','hour')]
            _hs_suppressed = bool(_ke_hs) and any(BRANCH_WX.get(b) == _ke_hs for b in _all_branches)
            hd = pw[hs]"""
c = c.replace(old, new)

# 修改CONFIRMED条件：化神被克制时不能是CONFIRMED
old2 = """            hua_name = '化%s气格' % hs
            if on_qi and dm_ben_eff == 0 and yin_ben_eff == 0 and (hb >= 1 or hju >= 1 or hs_t >= 1):
                hua_state = 'CONFIRMED'
            else:
                hua_state = 'CANDIDATE'                 # 微根/微印=假化"""

new2 = """            hua_name = '化%s气格' % hs
            # V4.7: 化神被克制时不能是CONFIRMED，只能是CANDIDATE(假化)
            if on_qi and dm_ben_eff == 0 and yin_ben_eff == 0 and (hb >= 1 or hju >= 1 or hs_t >= 1) and not _hs_suppressed:
                hua_state = 'CONFIRMED'
            else:
                hua_state = 'CANDIDATE'                 # 微根/微印/化神被克制=假化"""
c = c.replace(old2, new2)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('special_pattern.py V4.7修正完成(化神被克制时只能是CANDIDATE假化，不能是CONFIRMED真化)')
