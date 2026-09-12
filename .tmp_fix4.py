# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

# ── 修4：身体「禄被合克」（巳申合=火克金） ──
old = """        # 禄神（日主禄位）
        dm_lu = road_branch(day_master)
        lu_present = dm_lu in branches
        lu_attacked = any(
            b != dm_lu and (BRANCH_CHONG.get(b) == dm_lu or BRANCH_CHUAN.get(b) == dm_lu)
            for b in branches
        )
"""
new = """        # 禄神（日主禄位）
        dm_lu = road_branch(day_master)
        lu_present = dm_lu in branches
        # V3.4.3 【禄被合克】（对齐案例3"戊申己未庚申辛巳"原文）：
        # "巳申合：传统为合化水，盲派为合克（火克金）"；"禄怕见绝更怕穿害"——
        # 禄支被六合且相克之支合克（巳火合克申金禄）=禄神环境恶劣。
        lu_attacked = any(
            b != dm_lu and (BRANCH_CHONG.get(b) == dm_lu or BRANCH_CHUAN.get(b) == dm_lu)
            for b in branches
        )
        lu_he_ke = any(
            b != dm_lu and BRANCH_LIUHE.get(b) == dm_lu
            and CONTROLS.get(_branch_element(b)) == _branch_element(dm_lu)
            for b in branches
        )
        lu_attacked = lu_attacked or lu_he_ke
"""
assert old in src, "身体块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 禄被合克 已改")
