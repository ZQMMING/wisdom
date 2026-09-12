# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

# ── 修3：婚姻「宾主易位/官星投墓」 ──
old = """        star_weakened = any(
            BRANCH_CHONG.get(b) in branches or BRANCH_CHUAN.get(b) in branches
            for b in star_branches
        )
        # 综合（结构枚举，非吉凶词汇）
        broken_palace = any(tok in palace_state for tok in ("CLASHED", "HARMED", "PUNISHED"))
        if palace_state == "STABLE" and star_present and not star_weakened:
            marriage_state = "HARMONIOUS"
        elif broken_palace and star_weakened:
            marriage_state = "BROKEN"
        elif palace_state != "STABLE" or star_weakened:
            marriage_state = "CHALLENGED"
        else:
            marriage_state = "UNDETERMINED"
        result.marriage_event_structure = {
            "spouse_palace": day_branch,
            "palace_state": palace_state,
            "spouse_star_present": str(star_present),
            "spouse_star_weakened": str(star_weakened),
            "marriage_state": marriage_state,
        }
        result.rules_triggered.append("EVT-MARRIAGE-001")
"""
new = """        star_weakened = any(
            BRANCH_CHONG.get(b) in branches or BRANCH_CHUAN.get(b) in branches
            for b in star_branches
        )
        # V3.4.3 【宾主易位·官星投墓】（对齐案例4"甲寅丙子己亥戊辰"原文）：
        # 原文"日支亥水夫星被亥子水局推向月令→夫星出走；时柱戊土劫财坐辰(亥的墓库)
        # →丈夫(亥中甲木)被戊土(竞争对手)合走→官星投墓；官星在宾位有根(寅)，
        # 主位官星又被劫财收→宾主易位，婚姻难长久"。
        # 布尔判据：配偶星所在支（尤其日支=配偶宫）为入墓之字，且墓库支坐比劫
        # （竞争对手收走配偶星）→ 官星/妻星投墓 = 宾主易位 = 婚姻难长久。
        star_into_muku = False
        for sb in star_branches:
            sb_el = _branch_element(sb)
            # 该配偶星五行的墓库支（辰戌丑未）
            muku_b = None
            for mb, mel in MU_KU.items():
                if mel == sb_el:
                    muku_b = mb
                    break
            if muku_b is None or muku_b not in branches:
                continue
            # 墓库支坐比劫（竞争对手收走配偶星）→ 官星/妻星投墓
            muku_idx = branches.index(muku_b)
            muku_stem = [
                chart.year_pillar.heavenly_stem, chart.month_pillar.heavenly_stem,
                chart.day_pillar.heavenly_stem, chart.hour_pillar.heavenly_stem,
            ][muku_idx]
            if ten_god(day_master, muku_stem) in GROUP_BI:
                star_into_muku = True
                break
        # 综合（结构枚举，非吉凶词汇）
        broken_palace = any(tok in palace_state for tok in ("CLASHED", "HARMED", "PUNISHED"))
        if star_into_muku:
            marriage_state = "BROKEN"   # 宾主易位/官星投墓=婚姻难长久（案例4）
        elif palace_state == "STABLE" and star_present and not star_weakened:
            marriage_state = "HARMONIOUS"
        elif broken_palace and star_weakened:
            marriage_state = "BROKEN"
        elif palace_state != "STABLE" or star_weakened:
            marriage_state = "CHALLENGED"
        else:
            marriage_state = "UNDETERMINED"
        result.marriage_event_structure = {
            "spouse_palace": day_branch,
            "palace_state": palace_state,
            "spouse_star_present": str(star_present),
            "spouse_star_weakened": str(star_weakened),
            "spouse_star_into_muku": str(star_into_muku),
            "marriage_state": marriage_state,
        }
        result.rules_triggered.append("EVT-MARRIAGE-001")
"""
assert old in src, "婚姻块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 婚姻宾主易位 已改")
