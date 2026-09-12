# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

old = """        lu_he_ke = any(
            b != dm_lu and BRANCH_LIUHE.get(b) == dm_lu
            and CONTROLS.get(_branch_element(b)) == _branch_element(dm_lu)
            for b in branches
        )
        lu_attacked = lu_attacked or lu_he_ke
"""
new = """        lu_he_ke = any(
            b != dm_lu and BRANCH_LIUHE.get(b) == dm_lu
            and CONTROLS.get(_branch_element(b)) == _branch_element(dm_lu)
            for b in branches
        )
        lu_attacked = lu_attacked or lu_he_ke
        # V3.4.3 【燥土脆金伤禄】（对齐案例3原文"申金被未土脆克+巳火合克，
        # 禄神环境恶劣"；VERIFY-BLIND-034 原书"如四柱无水，见未戌之燥土定主
        # 脆金"）：禄支五行=金 且 局有未/戌燥土 且 四柱无水（无壬癸干、无亥子支）
        # → 禄被燥土脆金。
        stems_l = [
            chart.year_pillar.heavenly_stem, chart.month_pillar.heavenly_stem,
            chart.day_pillar.heavenly_stem, chart.hour_pillar.heavenly_stem,
        ]
        lu_cui_jin = (
            _branch_element(dm_lu) == "METAL"
            and any(b in DRY_EARTH_BRANCHES for b in branches)
            and not any(s in WATER_STEMS for s in stems_l)
            and not any(b in WATER_BRANCHES for b in branches)
        )
        lu_attacked = lu_attacked or lu_cui_jin
"""
assert old in src, "脆金块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 燥土脆金 已补")
