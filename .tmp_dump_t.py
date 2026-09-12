# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open("cases1980_full.json", encoding="utf-8"))
def dump(o, ind=0, maxd=8):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                print("  "*ind + str(k) + ":")
                if ind < maxd: dump(v, ind+1, maxd)
                else: print("  "*(ind+1) + "...")
            else:
                print("  "*ind + f"{k}: {v}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            if isinstance(v, (dict, list)):
                print("  "*ind + f"[{i}]:")
                if ind < maxd: dump(v, ind+1, maxd)
                else: print("  "*(ind+1) + "...")
            else:
                print("  "*ind + f"[{i}]: {v}")
print("===== L2.5 12主题 =====")
dump(d["L2_5"])
