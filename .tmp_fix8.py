# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

old = """        day_he_methods = [f"日主合{tg}" for _, tg in day_he_targets]
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
new = """        day_he_methods = [f"日主合{tg}" for _, tg in day_he_targets]
        # 原局【有效】的"去正官"方法（伤官制官/制正官/刑制正官/穿制正官）
        # V3.4.3 R2 判据再次收紧（对齐案例4/7/9原文）：
        #  1) 必须 EFFECTIVE（无效的伤官制官不构成去官意向——案例9 伤官制官 INEFFECTIVE）
        #  2) 排除"官杀制X/比劫制财/财制印"——那些不是去官（案例4 官杀制比劫=官杀自己做功）
        #  3) 制【七杀】≠ 去正官：合官+制杀=制凶得权，方向同向不冲突（案例7 合戊官+制己杀=大贵）
        #  4) 案例 D28 反局依据=日主合【财】+ 伤官制官 EFFECTIVE（求财 vs 丢官）
        zhi_guan_eff = [
            m for m, a in zip(result.zuo_gong_methods, result.zuo_gong_attributions)
            if a == ZuoGongAttribution["EFFECTIVE"]
            and ('伤官制官' in m or '制正官' in m or '刑制正官' in m or '穿制正官' in m)
        ]
        # 原书R2："日主合时柱官做功，要看官坐下的支去干啥了；官的坐支与日支
        # 做的功相反时，就反局了" —— 日主合正官(追求权位) 或 日主合财(求财)
        # 与原局去正官（丢官）并存 = 意向冲突。
        if day_he_methods and zhi_guan_eff:
            he_has_guan = any('正官' in m for m in day_he_methods)
            he_has_cai = any('财' in m for m in day_he_methods)
            if he_has_guan or he_has_cai:
                reasons.append(
                    f"R2日主做功与日支做功相反: {'+'.join(day_he_methods)}(追求)"
                    f" vs 原局{'+'.join(zhi_guan_eff)}(去除正官)"
                )
"""
assert old in src, "R2块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK R2判据二收紧 已改")
