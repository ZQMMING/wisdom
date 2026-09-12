# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()
old = """        # 互动制官：官非 DAMAGED 才映射官职（CASE-12 卯穿辰制官=命有官职；
        # 案例2 子穿未官库=DAMAGED 官场梦碎，互斥）
        occ_off = result.official_event_structure or {}
        occ_official_state = occ_off.get("official_state", "UNDETERMINED")
        if ("CONTROL_OFFICER_BY_INTERACTION" in work_types
                and occ_official_state != "DAMAGED"):
            occ_names.append(("官职/公职", "CASE-12(互动制官,命有官职)"))"""
new = """        # 互动制官：仅"互动+五行制"（刑制/穿制/冲制官）映射官职（CASE-12 卯穿制官
        # 辰=命有官职）；纯合官（合正官/合七杀）无明文不映射；官 DAMAGED 互斥
        # （案例2 子穿未官库=官场梦碎）
        occ_off = result.official_event_structure or {}
        occ_official_state = occ_off.get("official_state", "UNDETERMINED")
        interaction_officer_with_control = any(
            m in eff_methods for m in (
                '刑制正官', '刑制七杀', '刑正官', '刑七杀',
                '穿制正官', '穿制七杀', '穿正官', '穿七杀',
                '冲制官杀', '冲正官', '冲七杀',
            )
        )
        if (interaction_officer_with_control
                and occ_official_state != "DAMAGED"):
            occ_names.append(("官职/公职", "CASE-12(互动制官,命有官职)"))"""
assert old in src, "OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 互动制官收敛")
