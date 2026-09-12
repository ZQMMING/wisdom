# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_themes import aggregate_blind_themes
from src.tongshu.engines.blind_judgment import judge_blind

be = BaziEngine()
bb = BlindBaziEngine(be)

Y, M, D, H = 1980, 6, 22, 10
ch = be.compute((Y, M, D, H), gender="male")
br = bb.compute((Y, M, D, H), gender="male")
jr = judge_blind(ch, br)
tr = aggregate_blind_themes(ch, br, None, jr)

def d(o):
    return o.to_dict() if hasattr(o, "to_dict") else vars(o)

out = {
  "input": {"solar": f"{Y}-{M:02d}-{D:02d} {H:02d}:00", "gender": "male", "location": "广州(北京时间口径)"},
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
json.dump(out, open("cases1980_full.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("OK 写出 cases1980_full.json")
