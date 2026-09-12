# -*- coding: utf-8 -*-
import json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_yingqi import BlindYingqiEngine
from src.tongshu.engines.blind_judgment import BlindJudgmentEngine
from src.tongshu.engines.blind_themes import BlindThemeEngine

CASES = [
    (1, 1912,11,12,12,"male"), (2, 2027,3,22,2,"female"), (3, 2028,8,3,10,"male"),
    (4, 1974,12,24,8,"female"), (5, 1948,2,4,18,"male"), (6, 2010,2,18,4,"male"),
    (7, 1968,7,22,14,"male"), (8, 1965,9,4,14,"male"), (9, 1913,3,18,22,"male"),
    (10, 1968,10,21,4,"female"), (11, 1950,9,20,10,"female"), (12, 1947,4,20,4,"female"),
    (13, 1964,6,24,8,"female"), (14, 1985,5,22,22,"female"), (15, 2015,9,21,2,"female"),
]
be = BaziEngine(); bb = BlindBaziEngine(be); by = BlindYingqiEngine(be)
jd = BlindJudgmentEngine(); th = BlindThemeEngine()
out = []
for no, y, m, d, h, g in CASES:
    ch = be.compute((y,m,d,h), gender=g)
    br = bb.compute((y,m,d,h), gender=g)
    yr = by.analyze((y,m,d,h), gender=g, target_age=46)
    jr = jd.judge(ch, br, yr)
    tr = th.aggregate(ch, br, yr, jr).to_dict()
    out.append({"case": no, "pillars": ch.get_pillars_chinese(), "themes": tr["themes"]})
json.dump(out, open("cases15_themes.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

# 转 MD
lines = ["# 盲派 L2.5 维度断言（15 例，引擎原始输出转 MD，零加工）", ""]
lines.append("| 例 | 四柱 |")
lines.append("|---|---|")
for c in out:
    pstr = " ".join(c["pillars"].values())
    lines.append("| #%s | %s |" % (c["case"], pstr))
lines.append("")
for c in out:
    pstr = " ".join(c["pillars"].values())
    lines.append("## 例 #%s  %s" % (c["case"], pstr))
    lines.append("")
    lines.append("| 主题 | 状态 | 断言条目 | 规则 |")
    lines.append("|---|---|---|---|")
    for t in c["themes"]:
        entries = "<br>".join("%s = %s" % (e["source"], e["value"]) for e in t["entries"])
        rules = ", ".join(t.get("rule_ids") or [])
        lines.append("| %s %s | %s | %s | %s |" % (t["theme_id"], t["theme_name"], t["state"], entries.replace("|","\\|"), rules))
    lines.append("")
open("cases15_themes.md", "w", encoding="utf-8").write("\n".join(lines))
print("exists json:", os.path.exists("cases15_themes.json"), os.path.getsize("cases15_themes.json"))
print("exists md:", os.path.exists("cases15_themes.md"), os.path.getsize("cases15_themes.md"))
