# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open("cases1980_both.json", encoding="utf-8"))
for cid in ["1980A","1980B"]:
    c = d[cid]["chart"]
    print(cid, c["year"], c["month"], c["day"], c["hour"], "日主", c["day_master"])
