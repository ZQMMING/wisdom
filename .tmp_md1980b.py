# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open("cases1980_both.json", encoding="utf-8"))
CN = {"GENGSHEN":"庚申","RENWU":"壬午","BINGYIN":"丙寅","GUISI":"癸巳","GENGWU":"庚午","GUIWEI":"癸未","DINGYOU":"丁酉"}
L = []
for cid in ["1980A","1980B"]:
    c = d[cid]; ch = c["chart"]; b1 = c["blind_L1"]; l2 = c["L2"]; t5 = c["L2_5"]
    L.append(f"# {c['input']['note']}")
    L.append("")
    L.append("## 一、八字排盘 L0")
    L.append("")
    L.append("| 年柱 | 月柱 | 日柱 | 时柱 | 日主 |")
    L.append("|---|---|---|---|---|")
    L.append(f"| {CN.get(ch['year'],ch['year'])}·{ch['nayin']['year']} | {CN.get(ch['month'],ch['month'])}·{ch['nayin']['month']} | {CN.get(ch['day'],ch['day'])}·{ch['nayin']['day']} | {CN.get(ch['hour'],ch['hour'])}·{ch['nayin']['hour']} | {ch['day_master']} |")
    L.append("")
    L.append("## 二、盲派 L1 做功层")
    L.append("")
    L.append("| # | 方法 | 归属 | 明细 |")
    L.append("|---|---|---|---|")
    for i,(m,a,det) in enumerate(zip(b1["zuo_gong_methods"], b1["zuo_gong_attributions"], b1["zuo_gong_detail"])):
        L.append(f"| {i} | {m} | {a} | {det} |")
    L.append("")
    L.append(f"- 效率：{b1['work_efficiency']} | 制净：{b1['control_completeness']} | 等级：{b1['work_level']} | 反局：{b1['zheng_fan_ju']} | 旺衰：{b1['blind_wangshuai']}")
    L.append(f"- 做功串：{b1['zuo_gong_type']}")
    L.append(f"- 六亲：{b1['kinship_chain']}")
    L.append("")
    L.append("## 三、L2 解层事件")
    L.append("")
    for e in l2["event_candidates"]:
        L.append(f"- **{e['domain']} → {e['event_type']}（{e['direction']}）**｜{e['structure_ref']}｜{','.join(e['matched_rule_ids'])}")
    L.append("")
    L.append("## 四、L2.5 十二主题")
    L.append("")
    L.append("| 主题 | 状态 | 条目 |")
    L.append("|---|---|---|")
    for t in t5["themes"]:
        vals = "; ".join(f"{e['source']}={e['value']}" for e in t["entries"])
        L.append(f"| {t['theme_id']} {t['theme_name']} | {t['state']} | {vals} |")
    L.append("")
    L.append("---")
    L.append("")
io.open("cases1980_both.md", "w", encoding="utf-8").write("\n".join(L))
print("OK cases1980_both.md")
