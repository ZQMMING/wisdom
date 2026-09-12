# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open("cases1980_full.json", encoding="utf-8"))
ch = d["chart"]; b1 = d["blind_L1"]; l2 = d["L2"]; t5 = d["L2_5"]
CN = {"GENGSHEN":"庚申","RENWU":"壬午","BINGYIN":"丙寅","GUISI":"癸巳"}
L = []
L.append("# 1980-06-22 10:00 男 广州 — 全链路引擎输出（L0→L2.5，停 L3 前）")
L.append("")
L.append("> 口径：八字排盘引擎（北京时间口径）→ 盲派引擎（DUAN_JIANYE）→ L2 解层 → L2.5 12主题。引擎原始输出转 MD，无 LLM 断言。")
L.append("")
L.append("## 一、八字排盘 L0")
L.append("")
L.append("| 项 | 值 |")
L.append("|---|---|")
L.append(f"| 公历 | 1980-06-22 10:00 | 性别 | 男 |")
L.append(f"| 年柱 | {CN.get(ch['year'],ch['year'])}（{ch['nayin']['year']}） | 月柱 | {CN.get(ch['month'],ch['month'])}（{ch['nayin']['month']}） |")
L.append(f"| 日柱 | {CN.get(ch['day'],ch['day'])}（{ch['nayin']['day']}） | 时柱 | {CN.get(ch['hour'],ch['hour'])}（{ch['nayin']['hour']}） |")
L.append(f"| 日主 | {ch['day_master']} | | |")
L.append("")
L.append("## 二、盲派 L1 做功层")
L.append("")
L.append("| # | 方法 | 归属 | 明细 |")
L.append("|---|---|---|---|")
for i,(m,a,det) in enumerate(zip(b1["zuo_gong_methods"], b1["zuo_gong_attributions"], b1["zuo_gong_detail"])):
    L.append(f"| {i} | {m} | {a} | {det} |")
L.append("")
L.append(f"- 效率：{b1['work_efficiency']} | 制净：{b1['control_completeness']} | 等级：{b1['work_level']} | 反局：{b1['zheng_fan_ju']} | 旺衰：{b1['blind_wangshuai']}")
L.append("")
L.append("## 三、L2 解层事件")
L.append("")
for e in l2["event_candidates"]:
    det = e.get("detail") or {}
    occ = f"｜职业名：{det.get('occupation_name')}" if det.get("occupation_name") else ""
    L.append(f"- **{e['domain']} → {e['event_type']}（{e['direction']}）**｜{e['structure_ref']}{occ}")
L.append("")
L.append("## 四、L2.5 十二主题")
L.append("")
L.append("| 主题 | 状态 | 条目 |")
L.append("|---|---|---|")
for t in t5["themes"]:
    vals = "; ".join(f"{e['source']}={e['value']}" for e in t["entries"])
    L.append(f"| {t['theme_id']} {t['theme_name']} | {t['state']} | {vals} |")
L.append("")
io.open("cases1980_full.md", "w", encoding="utf-8").write("\n".join(L))
print("OK md")
