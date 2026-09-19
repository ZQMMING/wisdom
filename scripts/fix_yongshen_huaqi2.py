# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.4修复: ben()参数是十神类型不是五行，改用wuxing_power检查克化神的五行力量
old = """        # V4.4: 化神被克制则不判假化有情(如QT-0040戊子庚申乙丑壬午: 化神金但地支午火克金)
        _ke_hua = KE.get(hua_hwx)
        _hua_suppressed = bool(_ke_hua) and (ben(_ke_hua)>=1 or cs(_ke_hua) or ling(_ke_hua) in ('旺','相'))
        if not _hua_suppressed:"""

new = """        # V4.4: 化神被克制则不判假化有情(如QT-0040戊子庚申乙丑壬午: 化神金但地支午火克金)
        # 注意: ben()/cs()/ling()参数是十神类型不是五行，改用wuxing_power检查克化神的五行力量
        _ke_hua = KE.get(hua_hwx)
        _ke_hua_pow = wuxing_power.get('wuxing_power', {}).get(_ke_hua, {}) if _ke_hua else {}
        _hua_suppressed = bool(_ke_hua) and (
            int(_ke_hua_pow.get('ben_n', 0)) >= 1 or
            int(_ke_hua_pow.get('ju_n', 0)) >= 1 or
            _ke_hua_pow.get('ling_state', '') in ('旺', '相') or
            int(_ke_hua_pow.get('stem_n', 0)) >= 1
        )
        if not _hua_suppressed:"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.4修复完成(改用wuxing_power检查克化神的五行力量)')
