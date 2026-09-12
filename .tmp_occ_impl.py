# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()
old = """        result.occupation_candidate = {
            "work_types": list(dict.fromkeys(work_types)) or ["UNDETERMINED"],
            "palace_direction": list(dict.fromkeys(toward)) or ["UNDETERMINED"],
            "occupation_name": "UNDETERMINED",   # IMG-010 象法未核证 FACT_MISSING
            "status": "CANDIDATE" if work_types else "UNDETERMINED",
        }"""
new = """        # ── OCCUPATION-IMAGE 职业象映射（V3.5 解锁，仅收录案例原文取证的映射）──
        # 原则：方法层→职业候选 必须逐条有盲派原文实例支撑，无明文=UNDETERMINED。
        #   CASE-12 乾造甲辰戊辰癸卯己未（银行官员）："主位之卯穿制官星辰土→
        #           伤食制官局，命有官职；八字无财，以伤食当财富看→银行无疑"
        #   CASE-46 乾造戊辰己巳庚午辛未（医生·技术赚钱）："时柱辛未食神生财→
        #           食伤做功技术赚"
        #   CASE-23 坤造戊申壬戌戊午壬戌（工薪族）："食神主技能、印主单位→
        #           技能被单位重用→工薪族"
        #   CASE-8  乾造乙巳甲申辛酉乙未（仓库保管员）："官星被劫财合去→
        #           非我所有，终身仓库保管员"
        #   CASE-1  （辰库口诀）："辰库=银行、金融中心、巨大储蓄量"
        occ_names = []
        if "CONTROL_OFFICER_BY_FOOD_INJURY" in work_types:
            occ_names.append(("官职/公职", "CASE-12(伤食制官局,命有官职)"))
        if "GENERATE_WEALTH_BY_FOOD_INJURY" in work_types:
            occ_names.append(("技艺谋财", "CASE-46(食伤做功技术赚)"))
        if "TRANSFORM_OFFICER_BY_RESOURCE" in work_types:
            occ_names.append(("单位文职", "CASE-23(印主单位)"))
        # 互动制官：官非 DAMAGED 才映射官职（CASE-12 卯穿辰制官=命有官职；
        # 案例2 子穿未官库=DAMAGED 官场梦碎，互斥）
        occ_off = result.official_event_structure or {}
        occ_official_state = occ_off.get("official_state", "UNDETERMINED")
        if ("CONTROL_OFFICER_BY_INTERACTION" in work_types
                and occ_official_state != "DAMAGED"):
            occ_names.append(("官职/公职", "CASE-12(互动制官,命有官职)"))
        # ROBBED：官被劫财合走 → 非管理职/看守（CASE-8 终身仓库保管员）
        if occ_official_state == "ROBBED":
            occ_names.append(("非管理/看守", "CASE-8(官被劫财合走,终身仓库保管员)"))
        # 墓库收物且官非ROBBED → 金融/银行（CASE-1 辰库=银行金融中心）
        if "STORE_BY_MUKU" in work_types and occ_official_state != "ROBBED":
            occ_names.append(("金融/银行", "CASE-1(辰库=银行金融中心,巨大储蓄量)"))
        occ_uniq = []
        for n, e in occ_names:
            if n not in [x[0] for x in occ_uniq]:
                occ_uniq.append((n, e))
        result.occupation_candidate = {
            "work_types": list(dict.fromkeys(work_types)) or ["UNDETERMINED"],
            "palace_direction": list(dict.fromkeys(toward)) or ["UNDETERMINED"],
            "occupation_names": [{"name": n, "evidence": e} for n, e in occ_uniq],
            "occupation_name": "、".join(n for n, _e in occ_uniq) or "UNDETERMINED",
            "status": "CANDIDATE" if work_types else "UNDETERMINED",
        }"""
assert old in src, "OLD NOT FOUND"
src = src.replace(old, new, 1)
# 更新函数 docstring（原"occupation_name 恒 UNDETERMINED"说法已过时）
old2 = '''        """职业系统（§63）。原书：职业不是十神单独决定；
        食伤制官→CONTROL_OFFICER_BY_FOOD_INJURY→再由象法映射职业候选。
        象法（IMG-010）未核证 → occupation_name 恒 UNDETERMINED（FACT_MISSING），
        只输出做功类型+宫位方向候选。禁止"食神制杀=律师"。"""'''
new2 = '''        """职业系统（§63）。原书：职业不是十神单独决定；
        食伤制官→CONTROL_OFFICER_BY_FOOD_INJURY→再由象法映射职业候选。
        V3.5：OCCUPATION-IMAGE 已按案例原文取证解锁部分映射（CASE-12/46/23/8/1），
        仅收录有明文实例的 method→职业 映射；无明文仍 UNDETERMINED。"""'''
assert old2 in src, "OLD2 NOT FOUND"
src = src.replace(old2, new2, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 已实现 OCCUPATION-IMAGE")
