# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open("cases1980_full.json", encoding="utf-8"))
for e in d["L2"]["event_candidates"]:
    if e.get("domain") == "OCCUPATION":
        print(json.dumps(e, ensure_ascii=False, indent=1))
# 同时看L2.5事业主题
for t in d["L2_5"]["themes"]:
    if "事业" in t["theme_name"]:
        print("THEME-008:", json.dumps(t, ensure_ascii=False, indent=1))
