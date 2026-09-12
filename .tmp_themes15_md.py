# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

themes = json.load(open("cases15_themes.json", encoding="utf-8"))

lines = []
lines.append("# 盲派 L2.5 维度断言（15 例，引擎原始输出转 MD，零加工）")
lines.append("")
lines.append("| 例 | 四柱 | 反局/状态 |")
lines.append("|---|---|---|")
for c in themes:
    p = c["pillars"]
    pstr = " ".join(p.values())
    lines.append("| #%s | %s | PRODUCED |" % (c["case"], pstr))
lines.append("")

for c in themes:
    p = c["pillars"]
    pstr = " ".join(p.values())
    lines.append("## 例 #%s  %s" % (c["case"], pstr))
    lines.append("")
    lines.append("| 主题 | 状态 | 断言条目 | 规则 |")
    lines.append("|---|---|---|---|")
    for t in c["themes"]:
        entries = "  \n".join("%s = %s" % (e["source"], e["value"]) for e in t["entries"])
        rules = ", ".join(t.get("rule_ids") or [])
        lines.append("| %s %s | %s | %s | %s |" % (t["theme_id"], t["theme_name"], t["state"], entries.replace("|", "\\|"), rules))
    lines.append("")

open("cases15_themes.md", "w", encoding="utf-8").write("\n".join(lines))
print("done")
