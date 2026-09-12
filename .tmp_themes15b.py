# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_judgment import BlindJudgmentEngine
from src.tongshu.engines.blind_themes import aggregate_blind_themes

CASES = [
    ("#1", 1912,11,12,12,"male"),
    ("#2", 2027,3,22,2,"female"),
    ("#3", 2028,8,3,10,"male"),
    ("#4", 1974,12,24,8,"female"),
    ("#5", 1948,2,4,18,"male"),
    ("#6", 2010,2,18,4,"male"),
    ("#7", 1968,7,22,14,"male"),
    ("#8", 1965,9,4,14,"male"),
    ("#9", 1913,3,18,22,"male"),
    ("#10", 1968,10,21,4,"female"),
    ("#11", 1950,9,20,10,"female"),
    ("#12", 1947,4,20,4,"female"),
    ("#13", 1964,6,24,8,"female"),
    ("#14", 1985,5,22,22,"female"),
    ("#15", 2015,9,21,2,"female"),
]
be = BaziEngine(); bb = BlindBaziEngine(be)
jd = BlindJudgmentEngine()
out = {"cases": []}
for name, y, m, d, h, g in CASES:
    ch = be.compute((y,m,d,h), gender=g)
    br = bb.compute((y,m,d,h), gender=g)
    jr = jd.judge(ch, br)
    themes = aggregate_blind_themes(ch, br, None, jr)
    out["cases"].append({
        "id": name,
        "pillars": [f"{p.heavenly_stem}{p.earthly_branch}" for p in [ch.year_pillar, ch.month_pillar, ch.day_pillar, ch.hour_pillar]],
        "gender": g,
        "events": jr.to_dict(),
        "themes": themes.to_dict(),
    })
    print(name, "done", f"{ch.year_pillar.heavenly_stem}{ch.year_pillar.earthly_branch}")
with io.open("cases15_l2_full.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("TOTAL", len(out["cases"]))
