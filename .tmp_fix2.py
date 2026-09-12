# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

# ── 修2：官杀"穿≠制"（穿=损官）+ 官被劫财合走 ──
old = """        # 制官类有效方法（食伤制官/刑制官/穿制官/制官制杀；排除"官杀制比劫"=官杀自身做功）
        # 命名双源：L638 五行制=刑制X / 互动无制=刑X；合官=官被合绊（制官一种）
        control_officer_keywords = (
            '伤官制官', '食伤制杀',
            '刑制正官', '刑制七杀', '穿制正官', '穿制七杀', '冲制官杀',
            '刑正官', '刑七杀', '穿正官', '穿七杀', '冲正官', '冲七杀',
            '合正官', '合七杀',
            '制官', '制杀',
        )
        eff_methods = [
            m for m, a in zip(result.zuo_gong_methods, result.zuo_gong_attributions)
            if a == ZuoGongAttribution["EFFECTIVE"]
        ]
        controlled = any(m in eff_methods for m in control_officer_keywords) or any(
            m in eff_methods and ('制官' in m or '制杀' in m) and '官杀制' not in m
            for m in eff_methods
        )
        # 墓库收官：官杀所在支为墓库且墓库收物有效=官被收（D29 辛入丑墓→车间主任有制但制不净）
        officer_branches = [
            b for b in branches
            if any(ten_god(day_master, h) in GROUP_GUAN for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        ]
        muku_officer_controlled = any(
            b in MU_KU and '墓库收物' in eff_methods for b in officer_branches
        )
        controlled = controlled or muku_officer_controlled
        if officer_present and controlled and result.control_completeness == "CLEAN":
            official_state = "CONTROLLED_AND_CLEAN"   # D32 乾隆：金水伤官制净
        elif officer_present and controlled:
            official_state = "CONTROLLED_PARTIAL"
        elif officer_present and not controlled:
            official_state = "UNCONTROLLED"           # OFF-001 官杀无制必犯官非
        else:
            official_state = "UNDETERMINED"
"""
new = """        # 制官类有效方法（食伤制官/刑制官/冲制官/合官；排除"官杀制比劫"=官杀自身做功）
        # 命名双源：L638 五行制=刑制X / 互动无制=刑X；合官=官被合绊（制官一种）
        # V3.4.3 修正（对齐案例2"丁未癸卯庚子丁丑"原文）：【穿≠制】——
        # 盲派"穿的力量比冲大，穿是背后偷袭、排斥破坏"；"子水伤官穿未土官库=伤官损官，
        # 官根受损，体制内不适应、反骨"（盲派核心技法 §3）。穿官=损官（破坏官根），
        # 不是制官。故穿类方法从制官判据中剔除，另立"官根受损(DAMAGED)"状态。
        control_officer_keywords = (
            '伤官制官', '食伤制杀',
            '刑制正官', '刑制七杀', '冲制官杀',
            '刑正官', '刑七杀', '冲正官', '冲七杀',
            '合正官', '合七杀',
            '制官', '制杀',
        )
        eff_methods = [
            m for m, a in zip(result.zuo_gong_methods, result.zuo_gong_attributions)
            if a == ZuoGongAttribution["EFFECTIVE"]
        ]
        controlled = any(m in eff_methods for m in control_officer_keywords) or any(
            m in eff_methods and ('制官' in m or '制杀' in m) and '官杀制' not in m
            for m in eff_methods
        )
        # 墓库收官：官杀所在支为墓库且墓库收物有效=官被收（D29 辛入丑墓→车间主任有制但制不净）
        officer_branches = [
            b for b in branches
            if any(ten_god(day_master, h) in GROUP_GUAN for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        ]
        muku_officer_controlled = any(
            b in MU_KU and '墓库收物' in eff_methods for b in officer_branches
        )
        controlled = controlled or muku_officer_controlled
        # V3.4.3 【穿官=损官】DAMAGED：穿类方法 EFFECTIVE 且目标是官杀 → 官根受损
        # （案例2原文"伤官损官：子水伤官穿未土官库→官根受损、官场梦碎"）
        officer_damaged = any(
            m in eff_methods and ('穿' in m and ('正官' in m or '七杀' in m))
            for m in eff_methods
        )
        # V3.4.3 【官被劫财合走】ROBBED：官杀支被比劫支六合（如巳申=官被劫财合去）
        # （案例8原文"官星被劫财合去→非我所有、做功无效、终身仓库保管员"）
        bi_branches = [
            b for b in branches
            if any(ten_god(day_master, h) in GROUP_BI for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        ]
        officer_robbed = any(
            BRANCH_LIUHE.get(b_bi) in officer_branches for b_bi in bi_branches
        )
        if officer_present and officer_damaged:
            official_state = "DAMAGED"            # 官根受损（非官非，非官贵）
        elif officer_present and officer_robbed:
            official_state = "ROBBED"             # 官被劫财合走（非我所有）
        elif officer_present and controlled and result.control_completeness == "CLEAN":
            official_state = "CONTROLLED_AND_CLEAN"   # D32 乾隆：金水伤官制净
        elif officer_present and controlled:
            official_state = "CONTROLLED_PARTIAL"
        elif officer_present and not controlled:
            official_state = "UNCONTROLLED"           # OFF-001 官杀无制必犯官非
        else:
            official_state = "UNDETERMINED"
"""
assert old in src, "官杀块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 官杀穿≠制+被夺 已改")
