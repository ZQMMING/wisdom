# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_themes import aggregate_blind_themes
from src.tongshu.engines.blind_judgment import judge_blind

be = BaziEngine()
bb = BlindBaziEngine(be)

cases = [
    {"id": "1980A", "label": "1980-07-31 10:00（性别未指定，按male）", "ymdh": (1980,7,31,10), "gender": "male"},
    {"id": "1980B", "label": "1980-06-22 10:00 男 广州", "ymdh": (1980,6,22,10), "gender": "male"},
]
def d(o):
    return o.to_dict() if hasattr(o, "to_dict") else vars(o)

out_all = {}
for c in cases:
    Y,M,D,H = c["ymdh"]
    ch = be.compute(c["ymdh"], gender=c["gender"])
    br = bb.compute(c["ymdh"], gender=c["gender"])
    jr = judge_blind(ch, br)
    tr = aggregate_blind_themes(ch, br, None, jr)
    out_all[c["id"]] = {
        "input": {"solar": f"{Y}-{M:02d}-{D:02d} {H:02d}:00", "gender": c["gender"], "note": c["label"]},
        "chart": {
            "year": f"{ch.year_pillar.heavenly_stem}{ch.year_pillar.earthly_branch}",
            "month": f"{ch.month_pillar.heavenly_stem}{ch.month_pillar.earthly_branch}",
            "day": f"{ch.day_pillar.heavenly_stem}{ch.day_pillar.earthly_branch}",
            "hour": f"{ch.hour_pillar.heavenly_stem}{ch.hour_pillar.earthly_branch}",
            "day_master": ch.day_master,
            "nayin": {k: v for k, v in getattr(ch, "nayin", {}).items()},
        },
        "blind_L1": d(br),
        "L2": d(jr),
        "L2_5": d(tr),
    }
    print(f"OK {c['id']} {c['label']}")
json.dump(out_all, open("cases1980_both.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("写出 cases1980_both.json")
