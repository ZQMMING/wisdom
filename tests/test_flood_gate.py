# -*- coding: utf-8 -*-
"""ZIPING-YONGSHEN-FLOOD 验证: 泛滥闸门(纯枚举) + 120组逐日干调候表."""
import sys
sys.path.insert(0, ".")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.reasoning.ziping_v3.yongshen import YongShenEngine

BE = BaziEngine()


def run(y, m, d, h, label):
    c = BE.compute((y, m, d, h), gender="male")
    ys = c.year_pillar.heavenly_stem; yb = c.year_pillar.earthly_branch
    ms = c.month_pillar.heavenly_stem; mb = c.month_pillar.earthly_branch
    ds = c.day_pillar.heavenly_stem; db = c.day_pillar.earthly_branch
    hs = c.hour_pillar.heavenly_stem; hb = c.hour_pillar.earthly_branch
    print(f"=== {label} ({y}-{m:02d}-{d:02d} {h}时) ===")
    print(f"  四柱: {ys}{yb} / {ms}{mb} / {ds}{db} / {hs}{hb}")
    chart = {
        "month_branch": mb,
        "day_master": ds,
        "four_stems": [ys, ms, ds, hs],
        "four_branches": [yb, mb, db, hb],
        "has_root_for_yong": False,
    }
    v = YongShenEngine().verdict([], chart)
    d = YongShenEngine.to_dict(v)
    print(f"  喜用: 主用={d.get('primary_yong')} 次喜={d.get('primary_help')} 忌={d.get('Ji_shen', d.get('ji_shen'))}")
    print(f"  basis: {d.get('basis')}")
    if v.flood_note:
        print(f"  flood_note: {v.flood_note}")
    print(f"  引文: {d.get('classic_quote', '')[:50]}")
    print(f"  出处: {d.get('source', '')}")
    return v


js1983 = run(1983, 11, 3, 12, "1983案例(乙木戌月·水多)")
js1980 = run(1980, 6, 22, 10, "1980案例(丙火午月)")

print("\n=== 断言 ===")
# 1983: 乙木戌月调候"用癸水" → 水计数=癸+壬+壬+亥=4 → OVERFLOW → 转制化: 用=土(克水) 帮=火(生土) 忌=水
assert js1983.primary_yong == "EARTH", f"1983 应用土, 实得 {js1983.primary_yong}"
assert js1983.primary_help == "FIRE", f"1983 帮火, 实得 {js1983.primary_help}"
assert js1983.Ji_shen == "WATER", f"1983 忌水, 实得 {js1983.Ji_shen}"
assert "泛滥" in (js1983.flood_note or "") or "太过" in (js1983.flood_note or ""), "1983 应触发泛滥闸门"
print("  1983 泛滥闸门 ✓  用=土 帮=火 忌=水")

# 1980: 丙火午月 水计数=壬+癸=2 → NORMAL → 调候照常, 不回归
assert not js1980.flood_note, "1980 不应触发泛滥闸门"
print(f"  1980 不回归 ✓  调候 用={js1980.primary_yong} 忌={js1980.Ji_shen}")

print("\nALL PASS")
