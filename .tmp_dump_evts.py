# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
data = json.load(io.open("cases15_l2_full.json", encoding="utf-8"))
focus = {"#2","#3","#4","#7","#8","#9"}
for c in data["cases"]:
    if c["id"] not in focus: continue
    print("="*60)
    print(c["id"], "".join(c["pillars"]), c["gender"])
    evs = c["events"].get("events", c["events"]) if isinstance(c["events"], dict) else c["events"]
    if isinstance(c["events"], dict):
        for k in c["events"]:
            if k != "method_scope":
                v = c["events"][k]
                if isinstance(v, list):
                    for e in v:
                        if isinstance(e, dict) and ("event_type" in e or "kind" in e):
                            print("  EVT:", e.get("event_type") or e.get("kind"), "|", e.get("direction") or e.get("status"))
                else:
                    print("  ", k, "=", v)
