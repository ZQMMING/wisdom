# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

# ── 修5：R2 反局收紧（日主合财≠反局；只合官/杀追求 vs 原局去官/杀=冲突） ──
old = """        day_he_methods = [f"日主合{tg}" for _, tg in day_he_targets]
        # 原局制类做功（制官/制杀/伤官制官/食伤制杀等）
        zhi_methods = [m for m in methods if '制' in m]
        # 日主合财/合官 与 原局制官/制杀 并存 = 意向冲突（追求 vs 去除）
        if day_he_methods and zhi_methods:
            he_has_cai = any('财' in m for m in day_he_methods)
            zhi_has_guan = any(('官' in m or '杀' in m) for m in zhi_methods)
            if he_has_cai and zhi_has_guan:
                reasons.append(
                    f"R2日主做功与日支做功相反: {'+'.join(day_he_methods)}(追求)"
                    f" vs 原局{'+'.join(zhi_methods)}(去除)"
                )
"""
new = """        day_he_methods = [f"日主合{tg}" for _, tg in day_he_targets]
        # 原局制类做功（制官/制杀/伤官制官/食伤制杀等）
        zhi_methods = [m for m in methods if '制' in m]
        # V3.4.3 R2 收紧（对齐案例9"癸丑乙卯戊戌癸亥"原文）：
        # 原文"身弱财官旺，双癸合戊(财来合我)；原局'双癸合戊'激活，身强担旺财，
        # 2008戊子年资产几何级增长" —— 日主合【财】是求财意向（原书定意向），
        # 与"原局制财/去杀"并存是复合做功（意向+应期），不判反局。
        # 原书R2："日主合时柱官做功，要看官坐下的支去干啥了；官的坐支与日支
        # 做的功相反时，就反局了" —— 只有日主合【官/杀】(追求权位) 与
        # 原局去官/去杀（去除权位）并存才是意向冲突。
        if day_he_methods and zhi_methods:
            he_has_guan = any(('官' in m or '杀' in m) for m in day_he_methods)
            zhi_has_guan = any(('官' in m or '杀' in m) for m in zhi_methods)
            if he_has_guan and zhi_has_guan:
                reasons.append(
                    f"R2日主做功与日支做功相反: {'+'.join(day_he_methods)}(追求)"
                    f" vs 原局{'+'.join(zhi_methods)}(去除)"
                )
"""
assert old in src, "R2块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK R2反局收紧 已改")
