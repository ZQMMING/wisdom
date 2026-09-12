# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()
old = """        # 墓库收物且官非ROBBED → 金融/银行（CASE-1 辰库=银行金融中心）
        if "STORE_BY_MUKU" in work_types and occ_official_state != "ROBBED":
            occ_names.append(("金融/银行", "CASE-1(辰库=银行金融中心,巨大储蓄量)"))"""
new = """        # 墓库收物且官非ROBBED → 金融/银行，仅限辰库（CASE-1 原文"辰库=银行、
        # 金融中心、巨大储蓄量"；丑/未/戌库无明文，不映射=UNDETERMINED）
        has_chen = any(
            b == "CHEN" for b in (
                chart.year_pillar.earthly_branch, chart.month_pillar.earthly_branch,
                chart.day_pillar.earthly_branch, chart.hour_pillar.earthly_branch,
            )
        )
        if ("STORE_BY_MUKU" in work_types and occ_official_state != "ROBBED"
                and has_chen):
            occ_names.append(("金融/银行", "CASE-1(辰库=银行金融中心,巨大储蓄量)"))"""
assert old in src, "OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 墓库映射收敛至辰库")
